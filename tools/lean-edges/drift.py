"""What changed in the formal proof between the two pins: the file F10 reads.

The export is the proof at MIRROR_PIN (8c90877c), holding what its five main theorems depend on. The cache run is
every compiled module at MIRROR_COMMIT (c900e67). To compare like with like, the cache graph is closed from the same
five theorems of Main.lean, and the two closures are compared by name, over the project's declarations (the rule
of weight.py). Names are sorted into three kinds, because two of them change with the compiler, not the proof:

  user     a name someone wrote
  aux      an auxiliary the compiler makes: a component starting with `_`, `match_n`, `proof_n`, `eq_n`
  private  `_private.<module>.0.<name>`, which carries the module's path

Writes: the counts by kind of what left the closure, what joined it and what stayed; of the user-written names that
left, how many the later tree still compiles (now unused) and how many it no longer has; those names by namespace
to the second level, both ways; per statement, the user-written helpers its Lean reached at the earlier pin
(through declarations no statement names) that left the closure; per blueprint Lean name, whether each tree has
it and whether it is in the later closure, or that it is the library's (Mathlib's `RiemannHypothesis`), which the
cache, holding the project's modules only, cannot say; and the mirror's git history between the pins.

usage: drift.py <blueprint dir> <export graph .pkl> <cache graph .pkl> <mirror checkout> --meta <meta.json>
       > lean-drift.json
"""
import collections
import json
import pathlib
import pickle
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from edges import blueprint  # noqa: E402

MODROOTS = {"Development", "Formalism", "GroundTheory", "ReciprocityTheory", "CompanionTheory", "PositivityTheory",
            "Lemmata", "Supplements", "Statements", "Main"}
MAINS = ["riemannHypothesis", "riemannZeta_eq_zero_re", "LFunction_ne_zero_of_half_lt_re", "LFunction_eq_zero_re",
         "LFunction_eq_zero_re_of_isPrimitive"]
AUX = re.compile(r"(^|\.)(_[^.]*|match_\d+|proof_\d+|eq_\d+)$")


def kind(n):
    if n.startswith("_private."):
        return "private"
    if AUX.search(n) or "._" in n or ".match_" in n:
        return "aux"
    return "user"


def ns2(n):
    parts = n.split(".")
    return ".".join(parts[:2]) if len(parts) > 2 else parts[0]


def git(mirror, *args):
    return subprocess.run(["git", "-C", str(mirror), *args], capture_output=True, text=True, check=True).stdout.strip()


def main():
    args = sys.argv[1:]
    meta = json.loads(pathlib.Path(args[args.index("--meta") + 1]).read_text())
    del args[args.index("--meta"):args.index("--meta") + 2]
    root, xg, cg, mirror = pathlib.Path(args[0]), args[1], args[2], pathlib.Path(args[3])
    nodes, _ = blueprint(root)
    X = pickle.loads(pathlib.Path(xg).read_bytes())
    C = pickle.loads(pathlib.Path(cg).read_bytes())
    xnames, xdecl = X["names"], X["decl"]
    cnames, cdecl = C["names"], C["decl"]
    cn = {cnames[d] for d in cdecl}

    # The later closure: from Main.lean's theorems, over the cache graph (the project's declarations only).
    cid = {n: i for i, n in enumerate(cnames)}
    q = [cid[m] for m in MAINS if cid.get(m) in cdecl]
    if len(q) != len(MAINS):
        raise SystemExit("drift.py: the cache does not hold every theorem of Main.lean")
    seen = set(q)
    while q:
        x = q.pop()
        _, t, v = cdecl[x]
        for r in t + v:
            if r in cdecl and r not in seen:
                seen.add(r)
                q.append(r)
    later = {cnames[d] for d in seen}

    # The earlier closure: the export's project declarations.
    roots, rootp = collections.Counter(), collections.Counter()
    for d in xdecl:
        r = xnames[d].split(".", 1)[0]
        roots[r] += 1
        rootp[r] += xnames[d] in cn
    projroots = {r for r in roots if r != "_private" and rootp[r] * 2 > roots[r]}

    def is_proj(n):
        if n in cn:
            return True
        if n.startswith("_private."):
            return n.split(".")[1] in MODROOTS
        return n.split(".", 1)[0] in projroots

    earlier = {xnames[d] for d in xdecl if is_proj(xnames[d])}
    left, joined, stayed = earlier - later, later - earlier, earlier & later

    def by_kind(s):
        c = collections.Counter(kind(n) for n in s)
        return {k: c[k] for k in ("user", "aux", "private")}

    user_left = sorted(n for n in left if kind(n) == "user")
    user_joined = sorted(n for n in joined if kind(n) == "user")

    # Per statement: the user-written helpers its Lean reached in the export that left the closure.
    xid = {n: i for i, n in enumerate(xnames)}
    order = sorted(nodes)
    owner = {}
    for o in order:
        for n in nodes[o].get("lean", []):
            if xid.get(n) in xdecl:
                owner[xid[n]] = o
    proj_ids = {xid[n] for n in earlier}
    gone_ids = {xid[n] for n in user_left}
    stmts = {}
    for o in order:
        seen_, q = set(), []
        for s in (d for d, oo in owner.items() if oo == o):
            _, t, v = xdecl[s]
            for r in t + v:
                if r in proj_ids and r not in owner and r not in seen_:
                    seen_.add(r)
                    q.append(r)
        while q:
            x = q.pop()
            _, t, v = xdecl[x]
            for r in t + v:
                if r in proj_ids and r not in owner and r not in seen_:
                    seen_.add(r)
                    q.append(r)
        users = [x for x in seen_ if kind(xnames[x]) == "user"]
        stmts[o] = {"user_helpers": len(users), "left": sum(1 for x in users if x in gone_ids)}

    lean_names = {}
    for o in order:
        for n in nodes[o].get("lean", []):
            lib = xid.get(n) in xdecl and not is_proj(n)
            lean_names[n] = {"statement": o, "earlier": n in earlier or xid.get(n) in xdecl,
                             "later": n in later, "compiled_later": n in cn, "library": lib}

    pin, head = meta["proof"]["mirror"], meta["later"]["mirror"]
    files = git(mirror, "diff", "--no-renames", "--shortstat", pin, head)
    src_files = git(mirror, "diff", "--no-renames", "--shortstat", pin, head, "--", "src")
    out = dict(meta)
    out["git"] = {"commits": int(git(mirror, "rev-list", "--count", f"{pin}..{head}")),
                  "earlier_date": git(mirror, "log", "-1", "--format=%cI", pin),
                  "later_date": git(mirror, "log", "-1", "--format=%cI", head),
                  "diff": files, "diff_src": src_files}
    out["closures"] = {"earlier": len(earlier), "later": len(later)}
    out["by_kind"] = {"left": by_kind(left), "joined": by_kind(joined), "stayed": by_kind(stayed)}
    out["user_left"] = {"total": len(user_left), "still_compiled": sum(1 for n in user_left if n in cn),
                        "gone": sum(1 for n in user_left if n not in cn),
                        "namespaces": dict(sorted(collections.Counter(ns2(n) for n in user_left).items()))}
    out["user_joined"] = {"total": len(user_joined),
                          "namespaces": dict(sorted(collections.Counter(ns2(n) for n in user_joined).items()))}
    out["statements"] = stmts
    out["lean_names"] = dict(sorted(lean_names.items()))
    sys.stdout.write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"closures {len(earlier):,} -> {len(later):,}; user-written left {len(user_left):,} "
          f"({out['user_left']['still_compiled']:,} still compiled), joined {len(user_joined):,}", file=sys.stderr)


if __name__ == "__main__":
    main()
