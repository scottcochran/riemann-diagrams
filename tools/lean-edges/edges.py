"""The blueprint's arrows against the formal proof's: which `uses` edges the compiled Lean bears out.

Reads the per-module output of `deps` (run-deps.sh: one JSON line per declaration, with the constants its
statement and its value reference) and the blueprint. Each blueprint statement names Lean declarations (its
`lean` list). From those, the references are followed through every declaration no statement names (helper
lemmas, auxiliary definitions, `_proof_n`, matchers) until they reach a declaration that a statement names; that
statement is then one the first really uses. Two kinds of use, as the blueprint has them:

  statement  what a theorem's statement mentions, a definition's type and body, or a structure's fields
  proof      what a theorem's proof mentions

Helpers are followed through their type and value alike. A declaration outside the project (Mathlib, core) has
no entry and ends the search. Writes <out>.json: per statement, the Lean decls found and missing, and the formal
statement and proof uses; and prints how the blueprint's arrows compare.

The graph is cached in <out prefix>.graph.pkl and read from there when it exists, which is how the export's graph
(export_graph.py) is fed in; the deps dir is then not read and may be given as `-`.

usage: edges.py <deps dir | -> <blueprint dir> <out prefix>
"""
import collections
import json
import os
import pathlib
import pickle
import sys
import tomllib


def front(path):
    parts = path.read_text(encoding="utf-8").split("+++")
    return tomllib.loads(parts[1]) if len(parts) >= 3 else None


def blueprint(root):
    """Statements (kind not proof/section/chapter/reference/matter) with their `lean`, `uses`, and proof uses."""
    nodes, proofs = {}, {}
    for p in sorted(root.rglob("*.md")):
        fm = front(p)
        if not fm:
            continue
        if fm.get("kind") == "proof":
            proofs[fm["of"]] = fm.get("uses", [])
        elif fm.get("kind") in ("theorem", "lemma", "proposition", "definition", "remark", "corollary"):
            oid = fm.get("id") or p.stem
            nodes[oid] = fm
    return nodes, proofs


def load(deps, cache):
    """name -> (kind, type refs, value refs), interned to ints; a later part (private) supersedes the public."""
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    ids, names = {}, []

    def iid(n):
        i = ids.get(n)
        if i is None:
            i = ids[n] = len(names)
            names.append(n)
        return i

    decl = {}
    files = sorted(f for f in os.listdir(deps) if f.endswith(".jsonl"))
    for k, f in enumerate(files):
        with open(deps / f, encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                decl[iid(r["name"])] = (r["kind"], tuple(iid(x) for x in r["type"]), tuple(iid(x) for x in r["value"]))
        if k % 10000 == 0:
            print(f"  read {k} of {len(files)} modules, {len(decl)} declarations", file=sys.stderr)
    g = {"names": names, "decl": decl}
    cache.write_bytes(pickle.dumps(g, protocol=5))
    return g


def main():
    deps, root, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
    nodes, proofs = blueprint(root)
    g = load(deps, out.with_suffix(".graph.pkl"))
    names, decl = g["names"], g["decl"]
    ids = {n: i for i, n in enumerate(names)}
    order = sorted(nodes)
    bit = {oid: 1 << i for i, oid in enumerate(order)}
    owner = {}                                    # decl id -> statement id
    for oid in order:
        for n in nodes[oid].get("lean", []):
            if n in ids:
                owner[ids[n]] = oid
    # Constructors belong to their inductive's statement: a structure's fields are its constructor's type.
    for d, (kind, _, _) in decl.items():
        if kind == "ctor" and d not in owner:
            parent = names[d].rsplit(".", 1)[0]
            if ids.get(parent) in owner:
                owner[d] = owner[ids[parent]]

    ctors = collections.defaultdict(list)          # inductive -> its constructors
    for d, (kind, _, _) in decl.items():
        if kind == "ctor":
            parent = ids.get(names[d].rsplit(".", 1)[0])
            if parent is not None:
                ctors[parent].append(d)

    def refs(x, fields):
        """What x references. With `fields`, an inductive also leads into its constructors: a structure that a
        proof takes as a bundle of hypotheses (`LiteratureCMHypothesis`) carries each of them as a field, and a
        reference to the structure is then a use of what its fields state."""
        kind, t, v = decl[x]
        r = t + v
        if fields and kind == "inductive":
            r = r + tuple(ctors.get(x, ()))
        return r

    memo = {False: {}, True: {}}

    def reach(d, fields):
        """The statements a helper reaches, as a bitmask, through what it references; iterative, memoized."""
        mm = memo[fields]
        if d in mm:
            return mm[d]
        stack, onpath = [d], set()
        while stack:
            x = stack[-1]
            if x in mm:
                stack.pop()
                continue
            onpath.add(x)
            rs = refs(x, fields)
            pending = [r for r in rs if r in decl and r not in owner and r not in mm and r not in onpath]
            if pending:
                stack.extend(pending)
                continue
            m = 0
            for r in rs:
                if r in owner:
                    m |= bit[owner[r]]
                elif r in mm:
                    m |= mm[r]
            mm[x] = m
            onpath.discard(x)
            stack.pop()
        return mm[d]

    def via(rs, oid, fields):
        m = 0
        for r in rs:
            if r in owner:
                if owner[r] != oid:
                    m |= bit[owner[r]]
            elif r in decl:
                m |= reach(r, fields)
        return m & ~bit[oid]

    def unmask(m):
        return [oid for oid in order if m & bit[oid]]

    result = {}
    for oid in order:
        found = [n for n in nodes[oid].get("lean", []) if n in ids and ids[n] in decl]
        missing = [n for n in nodes[oid].get("lean", []) if n not in ids or ids[n] not in decl]
        uses = {}
        for fields in (False, True):
            st, pf = 0, 0
            for n in found:
                d = ids[n]
                kind, t, v = decl[d]
                if kind == "theorem":
                    st |= via(t, oid, fields)
                    pf |= via(v, oid, fields)
                else:
                    # A definition's statement is its type and body; a structure's is the types of its
                    # constructors, i.e. its fields, which are its own content and so read in either mode.
                    own = tuple(r for c in ctors.get(d, ()) for r in decl[c][1])
                    st |= via(t + v + own, oid, fields)
            uses[fields] = (st, pf)
        (st0, pf0), (st1, pf1) = uses[False], uses[True]
        result[oid] = {"lean_found": found, "lean_missing": missing,
                       "statement_uses": unmask(st1), "proof_uses": unmask(pf1),
                       "through_fields_only": unmask((st1 | pf1) & ~(st0 | pf0))}
    out.with_suffix(".json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    # How the blueprint's arrows compare with the formal ones.
    c = collections.Counter()
    for oid in order:
        r = result[oid]
        if not r["lean_found"]:
            c["statements with no Lean found"] += 1
            continue
        formal = set(r["statement_uses"]) | set(r["proof_uses"])
        fields_only = set(r["through_fields_only"])
        for u in set(nodes[oid].get("uses", [])) | set(proofs.get(oid, [])):
            if u not in nodes:
                continue
            if not result[u]["lean_found"]:
                c["blueprint arrows to a statement with no Lean found"] += 1
            elif u in fields_only:
                c["blueprint arrows the Lean bears out as a hypothesis (a structure's field)"] += 1
            elif u in formal:
                c["blueprint arrows the Lean bears out directly"] += 1
            else:
                c["blueprint arrows the Lean does not bear out"] += 1
        for u in formal - set(nodes[oid].get("uses", [])) - set(proofs.get(oid, [])):
            c["formal uses the blueprint does not draw"] += 1
    for k, v in sorted(c.items()):
        print(f"{v:6}  {k}")


if __name__ == "__main__":
    main()
