#!/usr/bin/env python3
"""Say where each pinned source stands: the pin, the checkout's commit, and what lies between them.

    python3 pin-status.py [--config proof-posters.toml] [--fetch] [--log N]

Reads the project's proof-posters.toml (default: at the root of the git tree the current directory is in). For
each [[pins.commit]] it prints the pinned value from [pins].file, and where the pin has a checkout, the checkout's
HEAD, how many commits lie between the two, and the last N of them. A pin read from a file in another pin's
checkout (read_in, read_file, read_regex) is compared with that file. Then it lists the re-read hashes and the
derived-file hashes with their current values, so that nothing pinned is forgotten. With --fetch, each checkout
is fetched first. Read-only otherwise. Standard library only, Python 3.11+.
"""
import os
import pathlib
import re
import subprocess
import sys
import tomllib


def git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def load_config(argv):
    if "--config" in argv:
        path = pathlib.Path(argv[argv.index("--config") + 1])
    else:
        top = git("rev-parse", "--show-toplevel")
        if not top:
            sys.exit("pin-status: not in a git tree; pass --config")
        path = pathlib.Path(top) / "proof-posters.toml"
    if not path.exists():
        sys.exit(f"pin-status: no {path}; the project has to describe its pins there (see skills/README.md)")
    return path.parent.resolve(), tomllib.loads(path.read_text(encoding="utf-8"))


def pinned(text, name):
    m = re.search(rf'^{re.escape(name)}\s*=\s*"([^"]*)"', text, re.M)
    return m.group(1) if m else None


def checkout(root, p):
    raw = os.environ.get(p.get("checkout_env", "")) or p.get("checkout_default")
    if not raw:
        return None
    path = pathlib.Path(raw)
    return path if path.is_absolute() else (root / path).resolve()


def main(argv):
    root, cfg = load_config(argv)
    n = int(argv[argv.index("--log") + 1]) if "--log" in argv else 10
    pins = cfg.get("pins", {})
    text = (root / pins["file"]).read_text(encoding="utf-8")
    trees = {}
    bad = 0
    print(f"Pins in {pins['file']}\n")
    for p in pins.get("commit", []):
        name, value = p["name"], pinned(text, p["name"])
        print(f"{name} = {value}    ({p.get('what', '')})")
        if value is None:
            print("  ERROR: not found in the pins file")
            bad += 1
            continue
        path = checkout(root, p)
        if path:
            top = git("rev-parse", "--show-toplevel", cwd=path) if path.exists() else None
            if not top:
                print(f"  no checkout at {path} (set {p.get('checkout_env')})")
                continue
            trees[name] = pathlib.Path(top)
            if "--fetch" in argv:
                git("fetch", "--quiet", cwd=top)
            head = git("rev-parse", "--short=10", "HEAD", cwd=top)
            upstream = git("rev-parse", "--short=10", "@{upstream}", cwd=top)
            print(f"  checkout {top} at {head}" + (f", upstream at {upstream}" if upstream else ""))
            ahead = upstream or head
            count = git("rev-list", "--count", f"{value}..{ahead}", cwd=top)
            if count is None:
                print(f"  ERROR: {value} is not a commit of this checkout (fetch it?)")
                bad += 1
            elif count == "0":
                print("  nothing newer than the pin")
            else:
                print(f"  {count} commits from the pin to {ahead}; the last {min(n, int(count))}:")
                for line in (git("log", "--oneline", f"-{n}", f"{value}..{ahead}", cwd=top) or "").splitlines():
                    print(f"    {line}")
        elif p.get("read_in"):
            top = trees.get(p["read_in"])
            if not top:
                print(f"  read from {p['read_file']} in {p['read_in']}'s checkout, which is not here")
                continue
            m = re.search(p["read_regex"], (top / p["read_file"]).read_text(encoding="utf-8"))
            found = m.group(1) if m else None
            same = bool(found) and found.startswith(value)
            print(f"  {p['read_file']} in the checkout says {found}: " + ("the same" if same else "MOVED"))
        print()
    for kind, label in (("reread", "Re-read hashes (prose to re-read when one fails)"),
                        ("derived", "Derived files (rebuilt outside the build)")):
        items = pins.get(kind, [])
        if items:
            print(label)
            for p in items:
                m = re.search(rf'^{re.escape(p["name"])}\s*=\s*("([0-9a-f]+)"|\{{)', text, re.M)
                v = (m.group(2)[:12] + "…") if m and m.group(2) else ("a table" if m else "NOT FOUND")
                print(f"  {p['name']} = {v}  {p.get('file') or p.get('source', '')}")
            print()
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
