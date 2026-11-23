"""The declaration-level reference graph of Sutherland's export, in the form edges.py reads.

For every declaration of the export (export.py ingest), the constants its type and its value reference,
found by walking each expression DAG once per declaration. Written as the pickle edges.py caches its graph in:
{"names": [...], "decl": {id: (kind, type refs, value refs)}}, with a declaration's index in the export as its
id. Kinds follow the deps tool's: theorem, def (definition, opaque, axiom, quotient), inductive, ctor, recursor.

The export holds only what the five main theorems depend on, so a blueprint name missing from this graph is a
declaration the published proof does not use.

usage: export_graph.py <export index dir> <out .pkl> [--sample N]
"""
import multiprocessing as mp
import pathlib
import pickle
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from export import K_APP, K_CONST, K_FORALL, K_LAM, K_LET, K_PROJ, Index  # noqa: E402

KIND = {0: "theorem", 1: "def", 2: "def", 3: "def", 4: "def", 5: "inductive", 6: "ctor", 7: "recursor"}
_ix = None


def _init(d):
    global _ix
    _ix = Index(pathlib.Path(d))


def walk(ix, root):
    """The constants an expression references, in first-seen order (projections name their structure)."""
    if root < 0:
        return ()
    ek, ea, eb, letc = ix.ek, ix.ea, ix.eb, ix.letc
    seen, stack, out, got = set(), [root], [], set()
    while stack:
        e = stack.pop()
        if e in seen:
            continue
        seen.add(e)
        k = ek[e]
        if k == K_APP or k == K_LAM or k == K_FORALL:
            stack.append(ea[e])
            if eb[e] >= 0:
                stack.append(eb[e])
        elif k == K_CONST:
            n = ea[e]
            if n not in got:
                got.add(n)
                out.append(n)
        elif k == K_LET:
            stack.append(ea[e]); stack.append(eb[e]); stack.append(letc[e])
        elif k == K_PROJ:
            stack.append(ea[e])
            n = eb[e]
            if n not in got:
                got.add(n)
                out.append(n)
    return out


def _chunk(dis):
    ix, res = _ix, []
    for di in dis:
        t = [ix.decl_of[n] for n in walk(ix, ix.dt[di]) if n in ix.decl_of]
        v = [ix.decl_of[n] for n in walk(ix, ix.dv[di]) if n in ix.decl_of]
        res.append((di, tuple(t), tuple(v)))
    return res


def main():
    d, out = sys.argv[1], pathlib.Path(sys.argv[2])
    sample = int(sys.argv[sys.argv.index("--sample") + 1]) if "--sample" in sys.argv else 0
    t0 = time.time()
    ix = Index(pathlib.Path(d))
    n = len(ix.dn)
    todo = list(range(n))
    if sample:
        todo = sorted(random.Random(0).sample(todo, sample))
    # Big declarations are spread over the chunks by interleaving, so no one worker is left with the tail.
    chunks = [todo[i::400] for i in range(400)]
    decl, done = {}, 0
    with mp.get_context("fork").Pool(8, _init, (d,)) as pool:
        for res in pool.imap_unordered(_chunk, chunks):
            for di, t, v in res:
                decl[di] = (KIND[ix.dk[di]], t, v)
            done += 1
            if done % 20 == 0:
                print(f"  {done} of {len(chunks)} chunks, {time.time() - t0:.0f} s", file=sys.stderr, flush=True)
    if sample:
        print(f"sample of {sample}: {time.time() - t0:.0f} s, so all {n:,} in about "
              f"{(time.time() - t0) * n / sample / 60:.0f} min", file=sys.stderr)
        return
    names = [ix.name(x) for x in ix.dn]
    out.write_bytes(pickle.dumps({"names": names, "decl": decl}, protocol=5))
    print(f"{len(decl):,} declarations, {sum(len(t) + len(v) for _, t, v in decl.values()):,} references, "
          f"{time.time() - t0:.0f} s", file=sys.stderr)


if __name__ == "__main__":
    main()
