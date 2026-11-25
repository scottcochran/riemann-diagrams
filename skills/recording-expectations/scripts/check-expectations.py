#!/usr/bin/env python3
"""Check how the output modules record what they expect of their sources: the part other scripts rely on.

    python3 check-expectations.py [--config proof-posters.toml] [--strict]

Reads the project's proof-posters.toml (default: at the root of the git tree), and every module [build].modules
matches, from the directory the config is in. An expectation is a top-level assignment to a name in
[build].expected_names. ERROR, and exit 1, for:

- a module that does not parse as Python;
- a module that records none of the expected names;
- a name assigned at the top level of one module more than once (the later one hides the earlier);
- a name recorded and never read anywhere in its module: it checks nothing;
- a name in expected_names that no module records;
- a name in [build].minor_names that is not in expected_names.

Each value that is not a literal is listed as a NOTE: cutting-releases' release-facts.py then compares it as code,
so a change shows as "changed" without its value. With --strict, a NOTE is an ERROR too.

What it cannot see: whether a name that is read is compared with the sources, whether the comparison fails the
build in both directions, and whether each sentence is quoted, computed, framing or guarded. Those are the skill's
to check by reading. Standard library only, Python 3.11+.
"""
import ast
import collections
import pathlib
import subprocess
import sys
import tomllib

NEED = ["build.modules", "build.expected_names"]


# load_config is the same in moving-pins/scripts/pin-status.py and determinism.py, in
# cutting-releases/scripts/release-facts.py and verify-release.py, and in
# recording-expectations/scripts/check-expectations.py. Each skill's folder stands alone, and the scripts still
# read the config the same way. Change all copies together.
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


def recorded(tree, names):
    """The top-level assignments to `names`, in order, as (name, value node, line)."""
    out = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        else:
            continue
        out += [(t.id, value, node.lineno) for t in targets if isinstance(t, ast.Name) and t.id in names]
    return out


def is_literal(value):
    try:
        ast.literal_eval(value)
        return True
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        return False


def main(argv):
    root, cfg = load_config(argv, "check-expectations", NEED)
    build = cfg["build"]
    names = list(build["expected_names"])
    errors, notes, used = [], [], collections.Counter()
    for name in sorted(set(build.get("minor_names", [])) - set(names)):
        errors.append(f"[build].minor_names has {name}, which is not in [build].expected_names")
    files = sorted(root.glob(build["modules"]))
    if not files:
        errors.append(f"no module matches [build].modules = {build['modules']!r}")
    total = literal = 0
    for f in files:
        rel = f.relative_to(root).as_posix()
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"), filename=rel)
        except SyntaxError as e:
            errors.append(f"{rel}: not Python ({e.msg}, line {e.lineno})")
            continue
        rec = recorded(tree, set(names))
        if not rec:
            errors.append(f"{rel}: records none of [build].expected_names, so nothing it draws is checked")
            continue
        loads = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        seen = collections.Counter(name for name, _, _ in rec)
        for name, n in sorted(seen.items()):
            if n > 1:
                errors.append(f"{rel}: {name} is assigned {n} times at the top level; the last one hides the others")
        for name, value, line in rec:
            used[name] += 1
            total += 1
            if name not in loads:
                errors.append(f"{rel}:{line}: {name} is recorded and never read in the module: it checks nothing")
            if is_literal(value):
                literal += 1
            else:
                notes.append(f"{rel}:{line}: {name} is not a literal; release-facts.py compares it as code")
    for name in names:
        if not used[name]:
            errors.append(f"{name} is in [build].expected_names, and no module records it")

    for line in notes:
        print(("ERROR " if "--strict" in argv else "NOTE ") + line)
    for line in errors:
        print("ERROR " + line)
    print(f"check-expectations: {len(files)} modules, {total} expectations under {len(used)} of {len(names)} "
          f"names, {literal} of them literals")
    return 1 if errors or ("--strict" in argv and notes) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
