"""Fetch compiled modules of the Lean mirror from its public build cache, and unpack them.

The cache is the one the mirror's `lake exe cache get` reads (scripts/ci-cache-get.py there): a receipt per
commit, `ci/revisions/<commit>.json`, names a module manifest whose rows are (module, dependency hash, archive,
sha256); each archive is a leantar file stored as `artifacts/<repo>/<hash>.art`. This fetches the receipt and
the manifest for one commit, checks both against the hashes the receipt gives, then downloads the archives of
the modules asked for, checks each against its sha256, and unpacks them with the toolchain's leantar into
<data>/oleans/<module path>.{olean,olean.private,...}. Files already present and correct are not fetched again.

usage: fetch.py <data dir> <commit> <toolchain bin dir> <modules file, one module name per line | all>
"""
import concurrent.futures
import gzip
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

BASE = "https://rh-cache.taucetiproject.org"
REPO = "leanprover-community/riemann-hypothesis"
AGENT = {"User-Agent": "RiemannHypothesisCache/1.0"}


def get(key, tries=6):
    """One object from the cache. A transient failure (a TLS alert, a reset, a 5xx) is retried with backoff; a
    404 is not, and the last failure is raised."""
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{BASE}/{key}", headers=AGENT), timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == tries - 1:
                raise
        except (urllib.error.URLError, OSError):
            if attempt == tries - 1:
                raise
        time.sleep(2 ** attempt)


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def manifest(data, commit):
    """The receipt and the module rows for `commit`, fetched once and checked against the receipt."""
    rpath = data / f"receipt-{commit[:7]}.json"
    if not rpath.exists():
        rpath.write_bytes(get(f"ci/revisions/{commit}.json"))
    receipt = json.loads(rpath.read_bytes())
    if receipt["candidate_head"] != commit or receipt["build_exit_code"] != 0:
        raise SystemExit(f"the cache's receipt is not a successful build of {commit}")
    mpath = data / "modules.jsonl.gz"
    if not mpath.exists() or sha256(mpath.read_bytes()) != receipt["module_manifest_sha256"]:
        mpath.write_bytes(get(receipt["module_manifest_key"]))
    raw = mpath.read_bytes()
    if sha256(raw) != receipt["module_manifest_sha256"]:
        raise SystemExit("the module manifest does not match the receipt")
    rows = {}
    for i, line in enumerate(gzip.decompress(raw).splitlines()):
        if i:
            name, dep_hash, art, digest = json.loads(line)
            rows[name] = (dep_hash, art, digest)
    return receipt, rows


def main():
    data, commit, toolbin, wanted = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3]), sys.argv[4]
    receipt, rows = manifest(data, commit)
    mods = sorted(rows) if wanted == "all" else [m.strip() for m in open(wanted) if m.strip()]
    missing = [m for m in mods if m not in rows]
    mods = [m for m in mods if m in rows]
    arts = data / "artifacts"
    arts.mkdir(exist_ok=True)

    done, lock = [0], threading.Lock()

    def one(m):
        dep_hash, art, digest = rows[m]
        path = arts / art
        if path.exists() and sha256(path.read_bytes()) == digest:
            n = 0
        else:
            b = get(f"artifacts/{REPO}/{art[:16]}.art")
            if sha256(b) != digest:
                raise ValueError(f"{m}: archive does not match the manifest's sha256")
            path.write_bytes(b)
            n = len(b)
        with lock:
            done[0] += 1
            if done[0] % 5000 == 0:
                print(f"  {done[0]} of {len(mods)} archives", file=sys.stderr, flush=True)
        return n

    with concurrent.futures.ThreadPoolExecutor(16) as pool:
        got = list(pool.map(one, mods))
    print(f"{len(mods)} modules, {sum(1 for g in got if g)} fetched, {sum(got) / 1e6:.1f} MB; "
          f"{len(missing)} not in the cache at {commit[:10]}", file=sys.stderr)
    out = data / "oleans"
    jobs = []
    for m in mods:
        dep_hash, art, _ = rows[m]
        parent = out.joinpath(*m.split(".")).parent
        parent.mkdir(parents=True, exist_ok=True)
        jobs.append({"file": str(arts / art), "hash": dep_hash, "base": [str(parent), str(parent)]})
    # leantar's worker threads overflow Rust's default 2 MB stack on some archives; the mirror's own restore
    # (scripts/ci-cache-get.py) raises it to 8 MB, and so does this.
    env = dict(os.environ, RUST_MIN_STACK=str(max(int(os.environ.get("RUST_MIN_STACK", "0")), 8388608)))
    subprocess.run([str(toolbin / "leantar"), "--jobs", "8", "-x", "-j", "-"], input=json.dumps(jobs), text=True,
                   check=True, env=env)
    (data / "not-in-cache.txt").write_text("".join(m + "\n" for m in missing))


if __name__ == "__main__":
    main()
