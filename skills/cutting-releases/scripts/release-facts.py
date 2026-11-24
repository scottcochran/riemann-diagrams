#!/usr/bin/env python3
"""The facts a release's number and tag message are decided from: what moved between the last tag and a commit.

    python3 release-facts.py [--since TAG] [--to REV] [--config proof-posters.toml]

Reads the project's proof-posters.toml (default: at the root of the git tree). Compares TAG (default: the latest
v* tag reachable from REV) with REV (default: HEAD) and prints:

- each [[pins.commit]] value at both, and whether it moved;
- each re-read and derived-file hash at both, and whether it moved;
- the posters added and removed, from the manifests, and the card and arrow counts that changed;
- for each poster module, which of [build].expected_names changed value (compared as parsed literals, so a
  reformatting is not a change);
- the commits between, by subject.

It ends with the class the table in PLAN-style release rules would give, as a suggestion with its reasons. A
change to what the posters are verified against (a new kind of check, a check removed) is MAJOR and cannot be
read off the tree: the script says so rather than guess. Read-only. Standard library only, Python 3.11+.
"""
import ast
import fnmatch
import json
import pathlib
import re
import subprocess
import sys
import tomllib


def git(*args, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"release-facts: git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout if r.returncode == 0 else None


def arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def show(rev, path):
    return git("show", f"{rev}:{path}", check=False)


def scalar(text, name):
    if text is None:
        return None
    m = re.search(rf'^{re.escape(name)}\s*=\s*"([^"]*)"', text, re.M)
    if m:
        return m.group(1)
    try:
        for node in ast.parse(text).body:
            if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
                return ast.dump(node.value)
    except SyntaxError:
        pass
    return None


def literals(text, names):
    """The values of the module-level assignments to `names`, as parsed literals (or their AST where not literal)."""
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
    cfg_path = arg(argv, "--config")
    root = pathlib.Path(git("rev-parse", "--show-toplevel").strip())
    cfg = tomllib.loads((pathlib.Path(cfg_path) if cfg_path else root / "proof-posters.toml").read_text("utf-8"))
    since = arg(argv, "--since") or git("describe", "--tags", "--abbrev=0", "--match", "v*", to).strip()
    pins, build = cfg["pins"], cfg["build"]
    print(f"From {since} to {to} ({git('rev-parse', '--short=10', to).strip()})\n")

    reasons = {"MINOR": [], "PATCH": []}
    a, b = show(since, pins["file"]), show(to, pins["file"])
    print("Pins")
    for p in pins.get("commit", []):
        x, y = scalar(a, p["name"]), scalar(b, p["name"])
        moved = x != y
        print(f"  {p['name']}: {x}" + (f" → {y}   MOVED" if moved else "   same"))
        if moved:
            reasons["MINOR"].append(f"{p['name']} moved")
    for kind in ("reread", "derived"):
        for p in pins.get(kind, []):
            x, y = scalar(a, p["name"]), scalar(b, p["name"])
            if x != y:
                print(f"  {p['name']}: {'(none)' if x is None else 'changed'}"
                      + ("   added" if x is None else "   MOVED"))
                reasons["PATCH" if kind == "reread" else "MINOR"].append(
                    f"{p['name']} {'added' if x is None else 'moved'}")
    print()

    print("Posters")
    for path in build.get("manifests", []):
        old = json.loads(show(since, path) or "{}")
        new = json.loads(show(to, path) or "{}")
        added, removed = sorted(set(new) - set(old)), sorted(set(old) - set(new))
        changed = [k for k in sorted(set(old) & set(new))
                   if (old[k].get("cards"), old[k].get("arrows")) != (new[k].get("cards"), new[k].get("arrows"))]
        print(f"  {path}: {len(new)} posters" + (f"; added {', '.join(added)}" if added else "")
              + (f"; removed {', '.join(removed)}" if removed else ""))
        for k in changed:
            print(f"    {k}: cards {old[k].get('cards')} → {new[k].get('cards')}, "
                  f"arrows {old[k].get('arrows')} → {new[k].get('arrows')}")
        if added:
            reasons["MINOR"].append(f"posters added in {path}: {', '.join(added)}")
        if removed:
            reasons["MINOR"].append(f"posters removed in {path}: {', '.join(removed)}")
    print()

    print("Recorded expectations (module-level names in the poster modules)")
    names = set(build.get("expected_names", []))
    files = sorted(set(f for rev in (since, to) for f in git("ls-tree", "-r", "--name-only", rev).split()
                       if fnmatch.fnmatch(f, build["modules"])))
    any_change = False
    for f in files:
        x, y = literals(show(since, f), names), literals(show(to, f), names)
        diff = sorted(k for k in set(x) | set(y) if x.get(k) != y.get(k))
        if diff:
            any_change = True
            status = "new module" if not x else "removed module" if not y else "changed"
            print(f"  {f}: {status}: {', '.join(diff)}")
            if x and y and any(k in ("EXPECTED", "HYPOTHESES") for k in diff):
                reasons["MINOR"].append(f"{f}: {', '.join(k for k in diff if k in ('EXPECTED', 'HYPOTHESES'))} changed")
    if not any_change:
        print("  none changed")
    print()

    log = git("log", "--format=%h %s", "--no-merges", f"{since}..{to}").strip()
    print(f"Commits ({len(log.splitlines()) if log else 0}, merges left out)")
    for line in log.splitlines():
        print(f"  {line}")
    print()

    cls = "MINOR" if reasons["MINOR"] else "PATCH"
    print(f"Suggested: {cls}" + ("" if log else " (nothing to release: no commits since the tag)"))
    for r in reasons[cls] or ["no pin moved, no poster added or removed, no EXPECTED or HYPOTHESES list changed"]:
        print(f"  - {r}")
    print("  Check for MAJOR by hand: did what a poster is verified against change (a kind of check added, "
          "removed or redefined)? That is not visible in these facts.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
