#!/usr/bin/env python3
"""Check a published release against the tree at its tag, and the Pages site against the release.

    python3 verify-release.py TAG [--sums FILE] [--metadata FILE] [--no-pages] [--config proof-posters.toml]

Reads the project's proof-posters.toml (default: at the root of the git tree). [release].checksums names the
release's checksum file (SHA256SUMS here), and [release].metadata, where the project has one, the file the release
workflow writes to record the release, which names its tag under [release].metadata_tag (pins.json and "tag"
here). Without --sums it downloads both from the release with `gh release download` (the GitHub CLI, logged in).
Then:

- every line of the checksum file names an asset; each one under [release].assets is hashed from the tree at TAG
  (`git show TAG:path`, not the working tree) and must match; one under [release].generated_assets is reported,
  not compared, since the workflow wrote it;
- every file the asset globs match in the tree at TAG must be in the checksum file;
- the metadata file must name TAG;
- unless --no-pages, [release].pages_url + the metadata file's name must name TAG (the site serves one release at
  a time).

Without [release].metadata, the last two are not checked, and the script says so. Exit 0 if all checked hold.
Read-only: it never edits a release, a tag or the site. Standard library only, Python 3.11+.
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

NEED = ["release.assets", "release.checksums"]


def arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def run(*cmd, binary=False):
    r = subprocess.run(cmd, capture_output=True, text=not binary)
    if r.returncode != 0:
        err = r.stderr if not binary else r.stderr.decode("utf-8", "replace")
        sys.exit(f"verify-release: {' '.join(cmd)}: {err.strip()}")
    return r.stdout


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


def main(argv):
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    tag = argv[0]
    _, cfg = load_config(argv, "verify-release", NEED)
    rel = cfg["release"]
    checksums, metadata, tag_key = rel["checksums"], rel.get("metadata"), rel.get("metadata_tag")
    if metadata and not tag_key:
        sys.exit("verify-release: [release].metadata is set, and [release].metadata_tag, the key that names the "
                 "release's tag in it, is not")
    sums_path, meta_path = arg(argv, "--sums"), arg(argv, "--metadata")
    if not sums_path:
        tmp = tempfile.mkdtemp(prefix="verify-release-")
        patterns = [x for name in (checksums, metadata) if name for x in ("-p", name)]
        run("gh", "release", "download", tag, *patterns, "-D", tmp)
        sums_path = f"{tmp}/{checksums}"
        meta_path = f"{tmp}/{metadata}" if metadata else None
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
            print(f"ERROR {name}: in {checksums}, but no file of the tree at {tag} matches {rel['assets']}")
            bad += 1
            continue
        actual = hashlib.sha256(run("git", "show", f"{tag}:{in_tree[name][0]}", binary=True)).hexdigest()
        if actual != digest:
            print(f"ERROR {name}: {checksums} has {digest[:12]}…, the tree at {tag} {actual[:12]}…")
            bad += 1
        else:
            ok += 1
    for name in sorted(set(in_tree) - set(sums)):
        print(f"ERROR {name}: in the tree at {tag}, not in {checksums}")
        bad += 1
    print(f"{ok} assets match the tree at {tag}")

    if not metadata:
        print("no [release].metadata: the release's record of its tag, and the site, are not checked")
        return 1 if bad else 0
    if meta_path:
        named = json.loads(pathlib.Path(meta_path).read_text("utf-8")).get(tag_key)
        print(f"{metadata} names {named}" + ("" if named == tag else f"   ERROR: not {tag}"))
        bad += named != tag
    if "--no-pages" not in argv and rel.get("pages_url"):
        url = rel["pages_url"].rstrip("/") + "/" + metadata
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "verify-release", "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=30) as r:
                served = json.load(r).get(tag_key)
        except Exception as e:
            served = None
            print(f"ERROR {url}: {e!r}")
        else:
            print(f"the site serves {served}" + ("" if served == tag else f"   ERROR: not {tag}"))
        bad += served != tag
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
