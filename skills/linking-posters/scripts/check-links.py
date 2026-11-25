#!/usr/bin/env python3
"""Check the links of a set of generated posters: every link lands, on a poster that exists, at an id that exists.

    python3 check-links.py [--config proof-posters.toml]

Reads the project's proof-posters.toml (default: at the root of the git tree): [build].outputs, the posters, and the
optional [links] table. Parses every output as XML and collects its ids and the addresses of its links (`href` or
`xlink:href` of `a`). ERROR, and exit 1, for:

- an output that does not parse, or an id given twice in one output;
- a link to `#id` that the same output does not have;
- a link to another file by a relative name that is not an output, or to an `#id` that output does not have;
- with [links].require_targets = true, a link to another output with no `#id`;
- a link out (an absolute address) that is neither at a pinned commit nor under one of [links].allow, when [links]
  has an `allow` list; without one, such links are counted and listed as NOTEs;
- any text of [links].unrendered in an output (markup the poster library left as text, such as `[[@`);
- with [links].frame_classes, a linked id whose element is not framed: neither its own class nor that of one of its
  direct children names one of the classes.

A pinned commit is each [[pins.commit]] that names a `repo`. A link https://github.com/<repo>/blob/<commit>/…
(or /tree/, /commit/) is at the pin when its repository is the pin's and its commit begins with the value the pins
file gives the pin, so that a short pin matches the full commit a link carries. It ends with the links by kind. Standard library only, Python 3.11+.
"""
import ast
import collections
import re
import fnmatch
import json
import pathlib
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET

NEED = ["build.outputs"]
XLINK = "{http://www.w3.org/1999/xlink}href"


# load_config is the same in moving-pins/scripts/pin-status.py and determinism.py, in
# cutting-releases/scripts/release-facts.py and verify-release.py, in
# recording-expectations/scripts/check-expectations.py, and in linking-posters/scripts/check-links.py; pin_value
# is the same in pin-status.py, release-facts.py and check-links.py. Each skill's folder stands alone, and the
# scripts still read the config and the pins the same way. Change all copies together.
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


GITHUB = re.compile(r"https://github\.com/([^/]+/[^/]+)/(?:blob|tree|commit)/([0-9a-f]{7,40})(?:[/#?]|$)")


def pinned(root, cfg):
    """(repo, commit value) of every [[pins.commit]] that names a repo, as the pins file gives the value."""
    pins = cfg.get("pins", {})
    out = []
    pfile = pins.get("file")
    text = (root / pfile).read_text(encoding="utf-8") if pfile and (root / pfile).is_file() else None
    for p in pins.get("commit", []):
        repo, name = p.get("repo"), p.get("name")
        if not (repo and name and text):
            continue
        value = pin_value(text, pfile, name)
        if isinstance(value, str) and value:
            out.append((repo.lower(), value.lower()))
    return out


def at_pin(href, pins):
    m = GITHUB.match(href)
    if not m:
        return False
    repo, commit = m.group(1).lower(), m.group(2).lower()
    return any(repo == r and commit.startswith(v) for r, v in pins)


def main(argv):
    root, cfg = load_config(argv, "check-links", NEED)
    links = cfg.get("links", {})
    require = bool(links.get("require_targets", False))
    allow = links.get("allow")
    unrendered = links.get("unrendered", [])
    frames = set(links.get("frame_classes", []))
    pins = pinned(root, cfg)
    files = sorted({p for g in cfg["build"]["outputs"] for p in root.glob(g) if p.is_file()})
    if not files:
        sys.exit(f"check-links: no file matches [build].outputs {cfg['build']['outputs']}")
    ids, elems, hrefs, errors, notes = {}, {}, {}, [], []
    for f in files:
        text = f.read_text(encoding="utf-8")
        rel = f.relative_to(root).as_posix()
        for marker in unrendered:
            if marker in text:
                i = text.index(marker)
                errors.append(f"{rel}: unrendered markup {text[i:i + 60]!r}")
        try:
            tree = ET.fromstring(text)
        except ET.ParseError as e:
            errors.append(f"{rel}: does not parse: {e}")
            continue
        seen = collections.Counter()
        elems[f] = {}
        for el in tree.iter():
            i = el.get("id")
            if i is not None:
                seen[i] += 1
                elems[f][i] = el
        for i, n in sorted(seen.items()):
            if n > 1:
                errors.append(f"{rel}: id {i!r} given {n} times")
        ids[f] = set(seen)
        hrefs[f] = [a.get("href") or a.get(XLINK) for a in tree.iter() if a.tag.rsplit("}", 1)[-1] == "a"]
    kinds = collections.Counter()
    out_of_pin = collections.Counter()
    targeted = collections.defaultdict(set)
    for f in files:
        rel = f.relative_to(root).as_posix()
        for h in hrefs.get(f, []):
            if not h:
                errors.append(f"{rel}: a link with no address")
                continue
            if "://" in h or h.startswith("mailto:"):
                if at_pin(h, pins):
                    kinds["to a source at its pin"] += 1
                elif allow is not None and any(h.startswith(p) for p in allow):
                    kinds["out, allowed"] += 1
                else:
                    kinds["out, not at a pin"] += 1
                    out_of_pin[h.split("#")[0]] += 1
                continue
            path, _, frag = h.partition("#")
            target = (f.parent / path).resolve() if path else f
            if target not in ids:
                errors.append(f"{rel}: link to {path!r}, which is not an output")
                continue
            if not frag:
                kinds["to a poster, no target"] += 1
                if require:
                    errors.append(f"{rel}: link to {path!r} with no #target")
                continue
            if frag not in ids[target]:
                errors.append(f"{rel}: link to #{frag} on {target.relative_to(root).as_posix()}, which has no such id")
                continue
            kinds["within a poster" if target == f else "to another poster's id"] += 1
            targeted[target].add(frag)
    if out_of_pin:
        msg = (f"{sum(out_of_pin.values())} links out to {len(out_of_pin)} addresses neither at a pinned commit nor "
               f"under [links].allow")
        if allow is not None:
            errors += [f"link out not at a pin or an allowed prefix: {h}" for h in sorted(out_of_pin)[:20]]
        else:
            notes.append(msg + "; e.g. " + ", ".join(sorted(out_of_pin)[:3]))
    if frames:
        for f, frags in sorted(targeted.items()):
            for frag in sorted(frags):
                el = elems[f][frag]
                classes = set((el.get("class") or "").split())
                for child in el:
                    classes |= set((child.get("class") or "").split())
                if not classes & frames:
                    errors.append(f"{f.relative_to(root).as_posix()}: #{frag} is linked and not framed "
                                  f"(no class of {sorted(frames)})")
    for e in errors[:200]:
        print("ERROR", e)
    if len(errors) > 200:
        print(f"ERROR … and {len(errors) - 200} more")
    for n in notes:
        print("NOTE", n)
    total = sum(kinds.values())
    print(f"check-links: {len(files)} outputs, {total:,} links: "
          + ", ".join(f"{n:,} {k}" for k, n in sorted(kinds.items(), key=lambda kv: -kv[1]))
          + (f"; {len(errors)} errors" if errors else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
