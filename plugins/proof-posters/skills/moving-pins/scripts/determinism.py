#!/usr/bin/env python3
"""Regenerate everything twice and fail unless both rounds give the same bytes and neither prints a failure marker.

    python3 determinism.py [--config proof-posters.toml] [ARG ...]

Reads the project's proof-posters.toml (default: at the root of the git tree). Each round runs every command of
[build].regenerate, in order, from the directory the config is in, with any ARGs appended (poster ids, say). A
command whose output has a line containing one of [build].failure_markers fails the check. A command that exits
non-zero fails it too, except that where [build].rerun_marker is set, a command that exits non-zero and prints a
line starting with it is run once more, as the generator asks.

The rounds differ only in their environment: [build].vary_env lists one table of variables per round (here
PYTHONHASHSEED 0, then 1, so that an output that depends on set or dict order shows). Without it, two rounds run in
the same environment. After each round, every file [build].outputs and [build].manifests match is hashed; the
rounds must give the same files with the same bytes. When they do not, the first round's files are kept in a
temporary directory, and the script says where.

It leaves the working tree as the last round wrote it, and ends by saying how many of those files differ from the
committed tree (`git status` names them). Standard library only, Python 3.11+.
"""
import hashlib
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib

NEED = ["build.regenerate", "build.failure_markers", "build.outputs"]


# load_config is the same in moving-pins/scripts/pin-status.py and determinism.py, in
# cutting-releases/scripts/release-facts.py and verify-release.py, in
# recording-expectations/scripts/check-expectations.py, and in linking-posters/scripts/check-links.py. Each
# skill's folder stands alone, and the scripts still read the config the same way. Change all copies together.
def load_config(argv, prog, need):
    """The project's proof-posters.toml, from --config FILE or the root of the git tree, and the directory it is in.

    Stops with a message saying what is missing when the file is not there, does not parse, or has no value for
    one of the dotted keys in `need` ("pins.file" is [pins].file).
    """
    if "--config" in argv:
        i = argv.index("--config") + 1
        if i >= len(argv):
            sys.exit(f"{prog}: --config needs a file")
        path = pathlib.Path(argv[i])
    else:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"{prog}: not in a git tree; pass --config FILE")
        path = pathlib.Path(r.stdout.strip()) / "proof-posters.toml"
    if not path.is_file():
        sys.exit(f"{prog}: no {path}; the project describes its layout there (README.md in the plugin)")
    try:
        cfg = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        sys.exit(f"{prog}: {path} does not parse: {e}")
    missing = []
    for key in need:
        node = cfg
        for part in key.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if node is None:
            table, _, name = key.rpartition(".")
            missing.append(f"[{table}].{name}")
    if missing:
        sys.exit(f"{prog}: {path} has no {', '.join(missing)} (README.md in the plugin says what each is)")
    return path.parent.resolve(), cfg


def snapshot(root, patterns):
    """Each file the globs match, relative to root, with the SHA-256 of its bytes."""
    files = sorted({p for g in patterns for p in root.glob(g) if p.is_file()})
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def run(cmd, root, env, markers, rerun):
    """Run one command; return None if it is clean, else what went wrong."""
    for attempt in (1, 2):
        r = subprocess.run(cmd, shell=True, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True)
        lines = r.stdout.splitlines()
        if r.returncode != 0 and rerun and attempt == 1 and any(l.startswith(rerun) for l in lines):
            continue
        flagged = [l for l in lines if any(m in l for m in markers)]
        if flagged:
            return "\n".join(flagged)
        if r.returncode != 0:
            return f"{r.stdout.rstrip()}\nexit {r.returncode}"
        return None


def main(argv):
    root, cfg = load_config(argv, "determinism", NEED)
    build = cfg["build"]
    rest = [a for i, a in enumerate(argv) if a != "--config" and (i == 0 or argv[i - 1] != "--config")]
    suffix = "".join(" " + shlex.quote(a) for a in rest)
    patterns = list(build["outputs"]) + list(build.get("manifests", []))
    rounds = build.get("vary_env") or [{}, {}]
    if len(rounds) < 2 or not all(isinstance(v, dict) for v in rounds):
        sys.exit("determinism: [build].vary_env must list a table of variables for each of two or more rounds")
    markers, rerun = list(build["failure_markers"]), build.get("rerun_marker")

    snaps, kept = [], None
    for n, vary in enumerate(rounds, 1):
        env = os.environ | {k: str(v) for k, v in vary.items()}
        label = " ".join(f"{k}={v}" for k, v in vary.items()) or "the same environment"
        for cmd in build["regenerate"]:
            wrong = run(cmd + suffix, root, env, markers, rerun)
            if wrong:
                print(f"{wrong}\ndeterminism: round {n} ({label}), `{cmd + suffix}`: the build is not clean")
                return 1
        snaps.append((label, snapshot(root, patterns)))
        if n == 1:
            kept = pathlib.Path(tempfile.mkdtemp(prefix="determinism-"))
            for rel in snaps[0][1]:
                (kept / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / rel, kept / rel)
        print(f"round {n} ({label}): {len(snaps[-1][1])} files, clean")

    first_label, first = snaps[0]
    bad = 0
    for label, snap in snaps[1:]:
        for rel in sorted(set(first) | set(snap)):
            if first.get(rel) != snap.get(rel):
                what = ("only in round 1" if rel not in snap else f"only under {label}" if rel not in first
                        else "differs")
                print(f"  {rel}: {what}")
                bad += 1
    if bad:
        print(f"determinism: {bad} files differ between rounds ({first_label} kept in {kept}): an output depends on "
              "something the rounds vary, such as set or dict order under PYTHONHASHSEED")
        return 1
    shutil.rmtree(kept)
    r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", *first], cwd=root,
                       capture_output=True, text=True)
    changed = len(r.stdout.splitlines()) if r.returncode == 0 else None
    rounds_said = " / ".join(label for label, _ in snaps)
    print(f"determinism: {len(first)} files, byte-identical over {len(snaps)} rounds ({rounds_said})"
          + ("" if changed is None else f"; {changed} differ from the committed tree"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
