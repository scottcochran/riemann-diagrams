#!/usr/bin/env python3
"""The facts a release's number and tag message are decided from: what moved between the last tag and a commit.

    python3 release-facts.py [--since TAG] [--to REV] [--config proof-posters.toml]

Reads the project's proof-posters.toml (default: at the root of the git tree). Compares TAG (default: the latest
tag matching [release].tag_match reachable from REV) with REV (default: HEAD) and prints:

- each [[pins.commit]] value at both, and whether it moved;
- each re-read and derived-file hash at both, and whether it moved;
- the posters added and removed, from the manifests, and the posters whose [build].manifest_counts changed;
- for each poster module, which of [build].expected_names changed value (compared as parsed literals, so a
  reformatting is not a change);
- the commits between, by subject.

It ends with the class the table in PLAN-style release rules would give, as a suggestion with its reasons: MINOR
for a pin moved or added, a derived file moved or added, a poster added or removed, or a change to one of
[build].minor_names; PATCH otherwise. A change to what the posters are verified against (a new kind of check, a
check removed) is MAJOR and cannot be read off the tree: the script says so rather than guess.

A pin that the config in REV's tree names and the pins file at REV does not assign (or assigns in a form other
than a top-level NAME = literal), a pins file or poster module that does not parse, or a manifest that is not a
JSON object is an ERROR: the script then suggests no class and exits 1. A pin missing only at TAG was added since;
one missing only at REV was removed, which may be MAJOR. Where REV's tree has no config (a tag from before it), a
pin missing at REV is reported, not an error. Read-only. Standard library only, Python 3.11+.
"""
import ast
import fnmatch
import json
import pathlib
import subprocess
import sys
import tomllib

NEED = ["pins.file", "build.modules", "build.manifests", "build.manifest_counts", "build.expected_names",
        "build.minor_names", "release.tag_match"]


def git(*args, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"release-facts: git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout if r.returncode == 0 else None


def arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def show(rev, path):
    return git("show", f"{rev}:{path}", check=False)


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


def literals(text, names):
    """The values of the module-level assignments to `names`, as parsed literals (or their AST where not literal).

    Raises SyntaxError when the module is not Python."""
    out = {}
    if text is None:
        return out
    for node in ast.parse(text).body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name) and t.id in names and node.value is not None:
                    try:
                        out[t.id] = repr(ast.literal_eval(node.value))
                    except ValueError:
                        out[t.id] = ast.dump(node.value)
    return out


def main(argv):
    to = arg(argv, "--to", "HEAD")
    _, cfg = load_config(argv, "release-facts", NEED)
    pins, build, rel = cfg["pins"], cfg["build"], cfg["release"]
    names, minor = set(build["expected_names"]), list(build["minor_names"])
    if not set(minor) <= names:
        sys.exit("release-facts: [build].minor_names has names that are not in [build].expected_names: "
                 + ", ".join(sorted(set(minor) - names)))
    since = arg(argv, "--since") or git("describe", "--tags", "--abbrev=0", "--match", rel["tag_match"], to).strip()
    print(f"From {since} to {to} ({git('rev-parse', '--short=10', to).strip()})\n")

    reasons = {"MINOR": [], "PATCH": []}
    errors = 0

    def error(line):
        nonlocal errors
        errors += 1
        print(f"  ERROR {line}")

    def read_pins(rev):
        text = show(rev, pins["file"])
        if text is None:
            return None
        try:
            return {p["name"]: pin_value(text, pins["file"], p["name"])
                    for kind in ("commit", "reread", "derived") for p in pins.get(kind, [])}
        except (SyntaxError, ValueError) as e:
            error(f"{pins['file']} at {rev} does not parse: {e}")
            return None

    # The pins the config at REV names, where REV's tree has the config: those the pins file at REV must assign. A
    # tree from before the config, or before a pin was added to it, may lack a pin the config here names.
    top = pathlib.Path(git("rev-parse", "--show-toplevel").strip())
    cfg_path = pathlib.Path(arg(argv, "--config") or top / "proof-posters.toml").resolve()
    try:
        cfg_in_tree = cfg_path.relative_to(top).as_posix()
    except ValueError:
        cfg_in_tree = None
    named_at_to = None
    text = show(to, cfg_in_tree) if cfg_in_tree else None
    if text is not None:
        try:
            cfg_to = tomllib.loads(text).get("pins", {})
            named_at_to = {p["name"] for kind in ("commit", "reread", "derived") for p in cfg_to.get(kind, [])}
        except (tomllib.TOMLDecodeError, KeyError, TypeError) as e:
            error(f"{cfg_in_tree} at {to} does not parse: {e}")

    print("Pins")
    if named_at_to is None:
        print(f"  ({cfg_in_tree or cfg_path} is not in the tree at {to}: a pin missing there is reported, "
              "not an error)")
    a, b = read_pins(since) or {}, read_pins(to)
    if b is None:
        error(f"{pins['file']} ([pins].file) is not readable at {to}")
        b = {}
    for kind in ("commit", "reread", "derived"):
        for p in pins.get(kind, []):
            name = p["name"]
            x, y = a.get(name), b.get(name)
            if y is None and named_at_to is not None and name in named_at_to:
                error(f"{name}: {cfg_in_tree} at {to} names it, and {pins['file']} there does not assign it "
                      "(only a top-level NAME = literal is read)")
            elif y is None and x is None:
                print(f"  {name}: not in {pins['file']} at either end")
            elif y is None:
                print(f"  {name}: " + (f"{x} → (none)" if kind == "commit" else "(none)") + "   removed")
                reasons["MINOR"].append(f"{name} removed (a check removed is MAJOR: decide by hand)")
            elif x is None:
                print(f"  {name}: (none)" + (f" → {y}" if kind == "commit" else "") + "   added")
                reasons["PATCH" if kind == "reread" else "MINOR"].append(f"{name} added")
            elif x != y:
                print(f"  {name}: " + (f"{x} → {y}" if kind == "commit" else "changed") + "   MOVED")
                reasons["PATCH" if kind == "reread" else "MINOR"].append(f"{name} moved")
            elif kind == "commit":
                print(f"  {name}: {x}   same")
    print()

    print("Posters")
    counts = list(build["manifest_counts"])
    for path in build["manifests"]:
        old, new = (json.loads(show(rev, path) or "{}") for rev in (since, to))
        if not (isinstance(old, dict) and isinstance(new, dict)):
            error(f"{path}: not a JSON object keyed by poster id at {since if not isinstance(old, dict) else to}")
            continue
        added, removed = sorted(set(new) - set(old)), sorted(set(old) - set(new))
        changed = [k for k in sorted(set(old) & set(new))
                   if [old[k].get(f) for f in counts] != [new[k].get(f) for f in counts]]
        print(f"  {path}: {len(new)} posters" + (f"; added {', '.join(added)}" if added else "")
              + (f"; removed {', '.join(removed)}" if removed else ""))
        for k in changed:
            print(f"    {k}: " + ", ".join(f"{f} {old[k].get(f)} → {new[k].get(f)}" for f in counts))
        if added:
            reasons["MINOR"].append(f"posters added in {path}: {', '.join(added)}")
        if removed:
            reasons["MINOR"].append(f"posters removed in {path}: {', '.join(removed)}")
    print()

    print("Recorded expectations (module-level names in the poster modules)")
    files = sorted(set(f for rev in (since, to) for f in git("ls-tree", "-r", "--name-only", rev).split()
                       if fnmatch.fnmatch(f, build["modules"])))
    any_change = False
    for f in files:
        try:
            x = literals(show(since, f), names)
            y = literals(show(to, f), names)
        except SyntaxError as e:
            error(f"{f}: not Python, so its expectations cannot be read ({e.msg}, line {e.lineno})")
            continue
        diff = sorted(k for k in set(x) | set(y) if x.get(k) != y.get(k))
        if diff:
            any_change = True
            status = "new module" if not x else "removed module" if not y else "changed"
            print(f"  {f}: {status}: {', '.join(diff)}")
            if x and y and any(k in minor for k in diff):
                reasons["MINOR"].append(f"{f}: {', '.join(k for k in diff if k in minor)} changed")
    if not any_change:
        print("  none changed")
    print()

    log = git("log", "--format=%h %s", "--no-merges", f"{since}..{to}").strip()
    print(f"Commits ({len(log.splitlines()) if log else 0}, merges left out)")
    for line in log.splitlines():
        print(f"  {line}")
    print()

    if errors:
        print(f"Suggested: none. {errors} ERROR line{'s' if errors > 1 else ''} above: the facts are incomplete, "
              "so a class read from them could be wrong.")
        return 1
    cls = "MINOR" if reasons["MINOR"] else "PATCH"
    print(f"Suggested: {cls}" + ("" if log else " (nothing to release: no commits since the tag)"))
    for r in reasons[cls] or [f"no pin moved, no poster added or removed, no {' or '.join(minor)} list changed"]:
        print(f"  - {r}")
    print("  Check for MAJOR by hand: did what a poster is verified against change (a kind of check added, "
          "removed or redefined)? That is not visible in these facts.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
