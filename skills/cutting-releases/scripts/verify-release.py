#!/usr/bin/env python3
"""Check a published release against the tree at its tag, and the Pages site against the release.

    python3 verify-release.py TAG [--sums SHA256SUMS] [--pins pins.json] [--no-pages] [--config proof-posters.toml]

Reads the project's proof-posters.toml (default: at the root of the git tree). Without --sums it downloads the
release's SHA256SUMS and pins.json with `gh release download` (the GitHub CLI, logged in). Then:

- every line of SHA256SUMS names an asset; each one under [release].assets is hashed from the tree at TAG
  (`git show TAG:path`, not the working tree) and must match; one under [release].generated_assets is reported,
  not compared, since the workflow wrote it;
- every file the asset globs match in the tree at TAG must be in SHA256SUMS;
- pins.json must name TAG;
- unless --no-pages, [release].pages_url + "pins.json" must name TAG (the site serves one release at a time).

Exit 0 if all hold. Read-only: it never edits a release, a tag or the site. Standard library only, Python 3.11+.
"""
import fnmatch
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import tomllib
import urllib.request


def arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def run(*cmd, binary=False):
    r = subprocess.run(cmd, capture_output=True, text=not binary)
    if r.returncode != 0:
        err = r.stderr if not binary else r.stderr.decode("utf-8", "replace")
        sys.exit(f"verify-release: {' '.join(cmd)}: {err.strip()}")
    return r.stdout


def main(argv):
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    tag = argv[0]
    root = pathlib.Path(run("git", "rev-parse", "--show-toplevel").strip())
    cfg = tomllib.loads(pathlib.Path(arg(argv, "--config", root / "proof-posters.toml")).read_text("utf-8"))
    rel = cfg["release"]
    sums_path, pins_path = arg(argv, "--sums"), arg(argv, "--pins")
    if not sums_path:
        tmp = tempfile.mkdtemp(prefix="verify-release-")
        run("gh", "release", "download", tag, "-p", "SHA256SUMS", "-p", "pins.json", "-D", tmp)
        sums_path, pins_path = f"{tmp}/SHA256SUMS", f"{tmp}/pins.json"
    sums = {}
    for line in pathlib.Path(sums_path).read_text("utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            sums[name.lstrip("*")] = digest

    tree = run("git", "ls-tree", "-r", "--name-only", tag).split("\n")
    in_tree = {}
    for path in tree:
        if any(fnmatch.fnmatch(path, g) for g in rel["assets"]):
            in_tree.setdefault(pathlib.PurePosixPath(path).name, []).append(path)
    bad = 0
    for name, paths in in_tree.items():
        if len(paths) > 1:
            print(f"ERROR {name}: two files in the tree have this asset name: {paths}")
            bad += 1
    ok = 0
    for name, digest in sorted(sums.items()):
        if name in rel.get("generated_assets", []):
            print(f"written by the workflow, not compared: {name}")
            continue
        if name not in in_tree:
            print(f"ERROR {name}: in SHA256SUMS, but no file of the tree at {tag} matches {rel['assets']}")
            bad += 1
            continue
        actual = hashlib.sha256(run("git", "show", f"{tag}:{in_tree[name][0]}", binary=True)).hexdigest()
        if actual != digest:
            print(f"ERROR {name}: SHA256SUMS has {digest[:12]}…, the tree at {tag} {actual[:12]}…")
            bad += 1
        else:
            ok += 1
    for name in sorted(set(in_tree) - set(sums)):
        print(f"ERROR {name}: in the tree at {tag}, not in SHA256SUMS")
        bad += 1
    print(f"{ok} assets match the tree at {tag}")

    if pins_path:
        named = json.loads(pathlib.Path(pins_path).read_text("utf-8")).get("tag")
        print(f"pins.json names {named}" + ("" if named == tag else f"   ERROR: not {tag}"))
        bad += named != tag
    if "--no-pages" not in argv and rel.get("pages_url"):
        url = rel["pages_url"].rstrip("/") + "/pins.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "verify-release", "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=30) as r:
                served = json.load(r).get("tag")
        except Exception as e:
            served = None
            print(f"ERROR {url}: {e!r}")
        else:
            print(f"the site serves {served}" + ("" if served == tag else f"   ERROR: not {tag}"))
        bad += served != tag
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
