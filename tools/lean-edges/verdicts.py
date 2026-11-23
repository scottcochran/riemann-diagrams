"""A verdict on every blueprint arrow, from the formal proof's references: the file the posters read.

Reads the blueprint and one or two runs of edges.py (<prefix>.json and the graph it was computed on,
<prefix>.graph.pkl). The first run is the source of the verdicts; the second, if given, is a cross-check whose
verdict is recorded wherever it differs. Each arrow A -> B (from A's `uses` or its proof's) gets the first of:

  no-lean-source  none of A's Lean names is in the formal proof
  no-lean-target  none of B's Lean names is in the formal proof
  hypothesis      A's Lean reaches B's only through the fields of a structure it takes: B is a hypothesis A carries
  direct          A's Lean reaches B's, through helper declarations that no statement names
  through         A's Lean reaches B's only by way of other statements' Lean (A -> C -> ... -> B)
  beside          A's Lean never reaches B's, but some declaration's proof mentions both: B is used next to A
  apart           none of these: the formal proof does not bear the arrow out

and the formal uses the blueprint does not draw are listed per statement.

usage: verdicts.py <blueprint dir> <run prefix> [<cross-check prefix>] --meta <meta.json> > lean-edges.json
"""
import collections
import json
import pathlib
import pickle
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from edges import blueprint  # noqa: E402

ORDER = ["direct", "hypothesis", "through", "beside", "apart", "no-lean-source", "no-lean-target"]
MEANING = {
    "direct": "A's Lean reaches B's, through helper declarations that no statement names",
    "hypothesis": "A's Lean reaches B's only through the fields of a structure it takes: B is a hypothesis A carries",
    "through": "A's Lean reaches B's only by way of other statements' Lean (A -> C -> ... -> B)",
    "beside": "A's Lean never reaches B's, but some declaration's proof mentions both: B is used next to A",
    "apart": "the formal proof does not bear the arrow out",
    "no-lean-source": "none of A's Lean names is in the formal proof",
    "no-lean-target": "none of B's Lean names is in the formal proof",
}


def arrows(nodes, proofs):
    """Every blueprint arrow between statements, as (A, B), once, sorted."""
    out = set()
    for a in nodes:
        for b in set(nodes[a].get("uses", [])) | set(proofs.get(a, [])):
            if b in nodes and b != a:
                out.add((a, b))
    return sorted(out)


def judge(nodes, proofs, prefix):
    res = json.loads(pathlib.Path(f"{prefix}.json").read_text())
    g = pickle.loads(pathlib.Path(f"{prefix}.graph.pkl").read_bytes())
    names, decl = g["names"], g["decl"]
    ids = {n: i for i, n in enumerate(names)}
    lean = {o: {ids[n] for n in res[o]["lean_found"] if n in ids} for o in nodes}
    formal = {a: set(r["statement_uses"]) | set(r["proof_uses"]) for a, r in res.items()}
    fields_only = {a: set(r["through_fields_only"]) for a, r in res.items()}

    # Who mentions each statement's Lean in a proof (a declaration's value), for `beside`.
    wanted = set().union(*lean.values())
    users = collections.defaultdict(set)
    for d, (_, _, v) in decl.items():
        for r in v:
            if r in wanted:
                users[r].add(d)

    def closure(a):
        seen, todo = set(), list(formal[a])
        while todo:
            x = todo.pop()
            if x not in seen:
                seen.add(x)
                todo.extend(formal.get(x, ()))
        return seen

    reach, out = {}, {}
    for a, b in arrows(nodes, proofs):
        if not lean[a]:
            v = "no-lean-source"
        elif not lean[b]:
            v = "no-lean-target"
        elif b in fields_only[a]:
            v = "hypothesis"
        elif b in formal[a]:
            v = "direct"
        else:
            if a not in reach:
                reach[a] = closure(a)
            if b in reach[a]:
                v = "through"
            else:
                ua = set().union(*(users[x] for x in lean[a]))
                ub = set().union(*(users[x] for x in lean[b]))
                v = "beside" if ua & ub else "apart"
        out[(a, b)] = v
    drawn = set(out)
    undrawn = {a: sorted(formal[a] - {b for (x, b) in drawn if x == a} - {a})
               for a in sorted(nodes) if lean[a]}
    missing = {o: sorted(set(nodes[o].get("lean", [])) - set(res[o]["lean_found"]))
               for o in sorted(nodes)}
    return out, {a: u for a, u in undrawn.items() if u}, {o: m for o, m in missing.items() if m}


def main():
    args = [a for a in sys.argv[1:]]
    meta = json.loads(pathlib.Path(args[args.index("--meta") + 1]).read_text())
    del args[args.index("--meta"):args.index("--meta") + 2]
    root, run = pathlib.Path(args[0]), args[1]
    cross = args[2] if len(args) > 2 else None
    nodes, proofs = blueprint(root)
    v, undrawn, missing = judge(nodes, proofs, run)
    counts = collections.Counter(v.values())
    doc = dict(meta)
    doc["verdicts"] = {k: MEANING[k] for k in ORDER}
    doc["counts"] = {k: counts[k] for k in ORDER}
    doc["arrows"] = {}
    for (a, b), x in sorted(v.items()):
        doc["arrows"].setdefault(a, {})[b] = x
    doc["undrawn"] = undrawn
    doc["lean_not_in_proof"] = missing
    if cross:
        cv, cu, cm = judge(nodes, proofs, cross)
        differs = {}
        for (a, b), x in sorted(cv.items()):
            if v[(a, b)] != x:
                differs.setdefault(a, {})[b] = x
        moves = collections.Counter((v[k], cv[k]) for k in v if v[k] != cv[k])
        doc["cross_check"]["differs"] = differs
        doc["cross_check"]["moves"] = {f"{p} -> {q}": n for (p, q), n in sorted(moves.items())}
        doc["cross_check"]["counts"] = {k: collections.Counter(cv.values())[k] for k in ORDER}
    sys.stdout.write(json.dumps(doc, indent=1, sort_keys=False, ensure_ascii=False) + "\n")
    print(json.dumps(doc["counts"]), file=sys.stderr)
    if cross:
        print("cross-check:", json.dumps(doc["cross_check"]["counts"]), file=sys.stderr)
        print("moves (export -> cache):", json.dumps(doc["cross_check"]["moves"], indent=1), file=sys.stderr)


if __name__ == "__main__":
    main()
