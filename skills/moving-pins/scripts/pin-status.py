#!/usr/bin/env python3
"""Say where each pinned source stands: the pin, the checkout's commit, and what lies between them.

    python3 pin-status.py [--config proof-posters.toml] [--fetch] [--log N]

Reads the project's proof-posters.toml (default: at the root of the git tree the current directory is in). For
each [[pins.commit]] it prints the pinned value from [pins].file, and where the pin has a checkout, the checkout's
HEAD, how many commits lie between the two, and the last N of them. A pin read from a file in another pin's
checkout (read_in, read_file, read_regex) is compared with that file. Then it lists the re-read hashes and the
derived-file hashes with their current values, so that nothing pinned is forgotten. A pin the config names and the
pins file does not assign is an ERROR, and the exit is 1. With --fetch, each checkout is fetched first. Read-only
otherwise. Standard library only, Python 3.11+.
"""
import ast
import json
import os
import pathlib
import re
import subprocess
import sys
import tomllib


def git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


# load_config and pin_value are the same in moving-pins/scripts/pin-status.py and in
# cutting-releases/scripts/release-facts.py and verify-release.py (load_config only), so that each skill's folder
# stands alone and the scripts still read the config and the pins the same way. Change all copies together.
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
        sys.exit(f"{prog}: no {path}; the project describes its layout there (skills/README.md in the plugin)")
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
        sys.exit(f"{prog}: {path} has no {', '.join(missing)} (skills/README.md in the plugin says what each is)")
    return path.parent.resolve(), cfg


def pin_value(text, path, name):
    """The value the pins file `text` (read from `path`) gives `name`, or None where it gives none.

    A .toml or .json file is parsed as such, and `name` is a top-level key or a dotted path into its tables. Any
    other file is read as Python: the last top-level assignment to `name`, annotated or not, as a literal (a str, or
    a dict for a table of hashes). A value that is not a literal comes back as its AST dump, so that two revisions
    compare equal when only the formatting changed. Raises ValueError or SyntaxError when the file does not parse.
    """
    if text is None:
        return None
    suffix = pathlib.PurePosixPath(str(path)).suffix
    if suffix in (".toml", ".json"):
        data = tomllib.loads(text) if suffix == ".toml" else json.loads(text)
        for part in name.split("."):
            if not isinstance(data, dict) or part not in data:
                return None
            data = data[part]
        return data
    value = None
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        else:
            continue
        if any(isinstance(t, ast.Name) and t.id == name for t in targets):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                value = ast.dump(node.value)
    return value


def checkout(root, p):
    raw = os.environ.get(p.get("checkout_env", "")) or p.get("checkout_default")
    if not raw:
        return None
    path = pathlib.Path(raw)
    return path if path.is_absolute() else (root / path).resolve()


def main(argv):
    root, cfg = load_config(argv, "pin-status", ["pins.file"])
    n = int(argv[argv.index("--log") + 1]) if "--log" in argv else 10
    pins = cfg["pins"]
    path = root / pins["file"]
    if not path.is_file():
        sys.exit(f"pin-status: no {path} ([pins].file)")
    try:
        text = path.read_text(encoding="utf-8")
        values = {p["name"]: pin_value(text, pins["file"], p["name"])
                  for kind in ("commit", "reread", "derived") for p in pins.get(kind, [])}
    except (SyntaxError, ValueError) as e:
        sys.exit(f"pin-status: {pins['file']} does not parse: {e}")
    trees = {}
    bad = 0
    print(f"Pins in {pins['file']}\n")
    for p in pins.get("commit", []):
        name, value = p["name"], values[p["name"]]
        print(f"{name} = {value}    ({p.get('what', '')})")
        if not isinstance(value, str):
            print("  ERROR: " + ("not found in the pins file" if value is None else "not a string in the pins file"))
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
                v = values[p["name"]]
                if v is None:
                    shown = "ERROR: not found in the pins file"
                    bad += 1
                else:
                    shown = "a table" if isinstance(v, dict) else (v[:12] + "…") if isinstance(v, str) else repr(v)
                print(f"  {p['name']} = {shown}  {p.get('file') or p.get('source', '')}")
            print()
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
