"""Where the formal work is: for each blueprint statement, the declarations under its Lean, and their size.

Reads Sutherland's export (its index and its declaration graph, export_graph.py) and the blueprint. Three steps:

  project   A declaration is the project's, not the library's (Mathlib, core), if the cache run at
            MIRROR_COMMIT names it (its deps cover the project's modules only); else if its name's root namespace
            is one where most of the export's names are the project's; else if it is private to a module under
            one of the project's source roots. A heuristic: a project lemma that the later tree dropped and that
            sits in a library namespace (`Nat.foo`) is counted as the library's.
  reach     Per statement, the project declarations its Lean reaches through declarations no statement names,
            stopping at another statement's: its cone of helpers. A helper in exactly one cone is that
            statement's own; one in several is shared; one in none is reached only from outside the statements.
  size      Per declaration, the number of distinct expression nodes in its type and value: the size of the
            terms the compiler wrote, a proof's included.

Writes, per statement, its own declarations and the helpers only it reaches, each with a count and a size, and
the helpers it shares; per pair of statements, nothing (too many); and for each statement in --open, its own
helpers grouped by namespace to the second level.

usage: weight.py <blueprint dir> <export index> <export graph .pkl> <cache graph .pkl> --meta <meta.json>
       [--open id ...] > lean-weight.json
"""
import collections
import json
import multiprocessing as mp
import pathlib
import pickle
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from edges import blueprint  # noqa: E402
from export import K_APP, K_FORALL, K_LAM, K_LET, K_PROJ, Index  # noqa: E402

MODROOTS = {"Development", "Formalism", "GroundTheory", "ReciprocityTheory", "CompanionTheory", "PositivityTheory",
            "Lemmata", "Supplements", "Statements", "Main"}
_ix = None


def _init(d):
    global _ix
    _ix = Index(pathlib.Path(d))


def _size(root, ix, seen):
    if root < 0:
        return 0
    ek, ea, eb, letc = ix.ek, ix.ea, ix.eb, ix.letc
    stack, n = [root], 0
    while stack:
        e = stack.pop()
        if e in seen:
            continue
        seen.add(e)
        n += 1
        k = ek[e]
        if k == K_APP or k == K_LAM or k == K_FORALL:
            stack.append(ea[e])
            if eb[e] >= 0:
                stack.append(eb[e])
        elif k == K_LET:
            stack.append(ea[e]); stack.append(eb[e]); stack.append(letc[e])
        elif k == K_PROJ:
            stack.append(ea[e])
    return n


def _chunk(dis):
    out = []
    for di in dis:
        seen = set()
        out.append((di, _size(_ix.dt[di], _ix, seen) + _size(_ix.dv[di], _ix, seen)))
    return out


def main():
    args = sys.argv[1:]
    meta = json.loads(pathlib.Path(args[args.index("--meta") + 1]).read_text())
    del args[args.index("--meta"):args.index("--meta") + 2]
    opened = []
    if "--open" in args:
        i = args.index("--open")
        opened, args = args[i + 1:], args[:i]
    root, index_dir, graph, cache = pathlib.Path(args[0]), args[1], args[2], args[3]
    nodes, _ = blueprint(root)
    G = pickle.loads(pathlib.Path(graph).read_bytes())
    names, decl = G["names"], G["decl"]
    ids = {n: i for i, n in enumerate(names)}
    C = pickle.loads(pathlib.Path(cache).read_bytes())
    proj = {C["names"][d] for d in C["decl"]}
    del C

    roots, rootp = collections.Counter(), collections.Counter()
    for d in decl:
        n = names[d]
        r = n.split(".", 1)[0]
        roots[r] += 1
        rootp[r] += n in proj
    projroots = {r for r in roots if r != "_private" and rootp[r] * 2 > roots[r]}

    def is_proj(n):
        if n in proj:
            return True
        if n.startswith("_private."):
            return n.split(".")[1] in MODROOTS
        return n.split(".", 1)[0] in projroots

    P = {d for d in decl if is_proj(names[d])}
    order = sorted(nodes)
    owner = {}
    for o in order:
        for n in nodes[o].get("lean", []):
            if ids.get(n) in decl:
                owner[ids[n]] = o
    for d, (k, _, _) in decl.items():
        if k == "ctor" and d not in owner:
            p = ids.get(names[d].rsplit(".", 1)[0])
            if p in owner:
                owner[d] = owner[p]
    own = collections.defaultdict(list)
    for d, o in owner.items():
        own[o].append(d)

    reached = collections.defaultdict(list)
    for o in order:
        seen, q = set(), []
        for s in own.get(o, ()):
            _, t, v = decl[s]
            for r in t + v:
                if r in P and r not in owner and r not in seen:
                    seen.add(r)
                    q.append(r)
        while q:
            x = q.pop()
            _, t, v = decl[x]
            for r in t + v:
                if r in P and r not in owner and r not in seen:
                    seen.add(r)
                    q.append(r)
        for x in seen:
            reached[x].append(o)

    todo = sorted(P)
    chunks = [todo[i::400] for i in range(400)]
    size = {}
    with mp.get_context("fork").Pool(8, _init, (index_dir,)) as pool:
        for k, res in enumerate(pool.imap_unordered(_chunk, chunks)):
            size.update(res)
            if k % 50 == 0:
                print(f"  sizes: {k} of {len(chunks)} chunks", file=sys.stderr, flush=True)

    helpers = P - set(owner)
    excl = collections.defaultdict(list)
    shared = collections.Counter()
    for x in helpers:
        rs = reached.get(x, [])
        if len(rs) == 1:
            excl[rs[0]].append(x)
        for o in rs if len(rs) > 1 else ():
            shared[o] += 1
    unreached = [x for x in helpers if not reached.get(x)]

    out = dict(meta)
    out["totals"] = {
        "declarations": len(decl), "project": len(P), "named": len(set(owner) & P), "helpers": len(helpers),
        "helpers_by_reach": {"none": len(unreached),
                             "one": sum(1 for x in helpers if len(reached.get(x, [])) == 1),
                             "two": sum(1 for x in helpers if len(reached.get(x, [])) == 2),
                             "more": sum(1 for x in helpers if len(reached.get(x, [])) > 2)},
        "size_project": sum(size[x] for x in P),
        "size_unreached": sum(size[x] for x in unreached),
    }
    out["statements"] = {}
    for o in order:
        od = [d for d in own.get(o, ()) if d in P]
        ex = excl.get(o, [])
        out["statements"][o] = {"own": len(od), "own_size": sum(size[d] for d in od),
                                "helpers": len(ex), "helpers_size": sum(size[x] for x in ex),
                                "shared": shared[o]}

    def ns2(n):
        parts = n.split(".")
        if parts[0] == "_private":
            return "(private)"
        return ".".join(parts[:2]) if len(parts) > 2 else parts[0]

    out["opened"] = {}
    for o in opened:
        groups = collections.defaultdict(lambda: [0, 0])
        for x in excl.get(o, []):
            g_ = groups[ns2(names[x])]
            g_[0] += 1
            g_[1] += size[x]
        big = sorted(excl.get(o, []), key=lambda x: (-size[x], names[x]))[:12]
        out["opened"][o] = {"namespaces": {k: {"helpers": v[0], "size": v[1]} for k, v in sorted(groups.items())},
                            "largest": [{"name": names[x], "size": size[x]} for x in big],
                            "own": [{"name": names[d], "size": size[d]} for d in sorted(own.get(o, ()),
                                                                                       key=lambda d: names[d])]}
    sys.stdout.write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    t = out["totals"]
    print(f"{t['project']:,} project declarations, {t['helpers']:,} helpers ({t['helpers_by_reach']}), "
          f"size {t['size_project']:,}", file=sys.stderr)


if __name__ == "__main__":
    main()
