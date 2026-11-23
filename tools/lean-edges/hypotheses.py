"""Where the formal proof's assumptions enter, and where they are discharged: the file F8 reads.

The theorems of Main.lean are closed propositions, so every assumption the proof takes is discharged inside it.
This finds two kinds of assumption in Sutherland's export of the proof, and what discharges each.

  packages  The structures behind the blueprint arrows that are borne out only as hypotheses (verdict
            `hypothesis` in lean-edges.json): A's Lean takes a structure one of whose fields states B. For each
            such arrow, the structures A's Lean reaches whose own fields reach B's Lean (through helpers, without
            opening a further structure); when none does, those whose fields reach it through nested structures,
            marked `nested`. Per structure: its fields' statements, the statements that take it, and its
            builders, the declarations whose type concludes in it, each with the statement that names it or
            the statements whose Lean reaches it.
  props     The statements whose Lean includes a `Prop` definition (by its signature in lean-facts.json): a
            claim stated, to be proved or assumed. Per `Prop`, the theorems in the export whose conclusion has
            it at its head, each with its premises typed by a blueprint `Prop` or by a structure above. A
            `Prop` is `outright` if one such theorem has no such premise, `conditional` if every one has, `never`
            if no theorem concludes it, and `absent` if the export does not contain it. Premises of other types
            are not seen, so `outright` means no premise this test recognises; nor is a theorem that concludes
            a `Prop` of another name unfolding to the same, so `never` means never under this name.
  axioms    The axioms the export holds: what everything the five main theorems depend on rests on.

usage: hypotheses.py <blueprint dir> <export index> <export graph .pkl> <lean-edges.json> --meta <meta.json>
       > lean-hypotheses.json
"""
import collections
import json
import pathlib
import pickle
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from edges import blueprint  # noqa: E402
from export import K_APP, K_CONST, K_FORALL, Index  # noqa: E402

CLASSES = ("outright", "conditional", "never", "absent")


def main():
    args = sys.argv[1:]
    meta = json.loads(pathlib.Path(args[args.index("--meta") + 1]).read_text())
    del args[args.index("--meta"):args.index("--meta") + 2]
    root, index_dir, graph, edges_file = pathlib.Path(args[0]), args[1], args[2], args[3]
    nodes, _ = blueprint(root)
    lf = json.loads((root.parent / "lean-facts.json").read_text())["decls"]
    E = json.loads(pathlib.Path(edges_file).read_text())
    G = pickle.loads(pathlib.Path(graph).read_bytes())
    names, decl = G["names"], G["decl"]
    ids = {n: i for i, n in enumerate(names)}
    order = sorted(nodes)
    bit = {o: 1 << i for i, o in enumerate(order)}

    def unmask(m):
        return [o for o in order if m & bit[o]]

    owner = {}
    for o in order:
        for n in nodes[o].get("lean", []):
            if ids.get(n) in decl:
                owner[ids[n]] = o
    ctors = collections.defaultdict(list)
    for d, (k, _, _) in decl.items():
        if k == "ctor":
            p = ids.get(names[d].rsplit(".", 1)[0])
            if p is not None:
                ctors[p].append(d)
    for d, (k, _, _) in decl.items():
        if k == "ctor" and d not in owner:
            p = ids.get(names[d].rsplit(".", 1)[0])
            if p in owner:
                owner[d] = owner[p]

    memo = {False: {}, True: {}}

    def reach(d, fields):
        """The statements a helper reaches, as a bitmask, as edges.py computes it."""
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
            k, t, v = decl[x]
            rs = t + v + (tuple(ctors.get(x, ())) if fields and k == "inductive" else ())
            pend = [r for r in rs if r in decl and r not in owner and r not in mm and r not in onpath]
            if pend:
                stack.extend(pend)
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

    def via(rs, fields):
        m = 0
        for r in rs:
            if r in owner:
                m |= bit[owner[r]]
            elif r in decl:
                m |= reach(r, fields)
        return m

    def fields_reach(i, fields):
        return via(tuple(r for c in ctors.get(i, ()) for r in decl[c][1]), fields)

    def cone(o):
        """The helpers a statement's Lean reaches, through declarations no statement names and into the fields of
        the structures among them, kept to those that reach some statement, so that the library is never
        walked."""
        seen, q = set(), []
        for s in (ids[n] for n in nodes[o].get("lean", []) if ids.get(n) in decl):
            _, t, v = decl[s]
            for r in t + v:
                if r in decl and r not in owner and r not in seen and reach(r, True):
                    seen.add(r)
                    q.append(r)
        while q:
            x = q.pop()
            k, t, v = decl[x]
            for r in t + v + (tuple(ctors.get(x, ())) if k == "inductive" else ()):
                if r in decl and r not in owner and r not in seen and reach(r, True):
                    seen.add(r)
                    q.append(r)
        return seen

    # ---------------------------------------------------------------------------------- the packages
    hyp = collections.defaultdict(list)
    for a, us in E["arrows"].items():
        for b, v in us.items():
            if v == "hypothesis":
                hyp[a].append(b)
    arrows, nested = {}, {}
    for a in sorted(hyp):
        inds = sorted(x for x in cone(a) if decl[x][0] == "inductive")
        for b in sorted(hyp[a]):
            pk = [names[i] for i in inds if fields_reach(i, False) & bit[b]]
            if not pk:
                pk = [names[i] for i in inds if fields_reach(i, True) & bit[b]]
                nested[(a, b)] = True
            arrows[(a, b)] = sorted(pk)
    pkgs = sorted({p for ps in arrows.values() for p in ps})

    # ---------------------------------------------------------------------------------- the Props
    props = {}
    for o in order:
        for x in nodes[o].get("lean", []):
            v = lf.get(x)
            if v and v["kind"] == "definition" and re.search(r":\s*Prop\s*:=", v.get("signature", "")):
                props[x] = o
    ix = Index(pathlib.Path(index_dir))
    found = ix.by_name(set(props) | set(pkgs))
    nid = {ix.dn[di]: x for x, di in found.items()}

    def head(e):
        while e >= 0 and ix.ek[e] == K_APP:
            e = ix.ea[e]
        return ix.ea[e] if e >= 0 and ix.ek[e] == K_CONST else None

    def premises(e):
        ps, ks = set(), set()
        while e >= 0 and ix.ek[e] == K_FORALL:
            h = nid.get(head(ix.ea[e]))
            if h in props:
                ps.add(props[h])
            elif h in pkgs:
                ks.add(h)
            e = ix.eb[e]
        return sorted(ps), sorted(ks)

    proved, built = collections.defaultdict(list), collections.defaultdict(list)
    for di in range(len(ix.dn)):
        k = ix.dk[di]
        if k not in (0, 1):
            continue
        h = nid.get(head(ix.conclusion(ix.dt[di])))
        if h is None:
            continue
        n = ix.name(ix.dn[di])
        if h in props and k == 0:
            proved[h].append((n,) + premises(ix.dt[di]))
        elif h in pkgs and not n.startswith(h + "."):
            built[h].append(n)
    lean_owner = {x: o for o in order for x in nodes[o].get("lean", [])}

    # Who reaches each helper builder: the statements whose Lean's cone holds it.
    want = {ids[n] for b in built.values() for n in b if n not in lean_owner and n in ids}
    reached_from = collections.defaultdict(list)
    if want:
        for o in order:
            for x in cone(o) & want:
                reached_from[names[x]].append(o)

    out = dict(meta)
    out["classes"] = {
        "outright": "a theorem concludes the Prop with no premise typed by a blueprint Prop or a structure below",
        "conditional": "every theorem that concludes the Prop has such a premise",
        "never": "no theorem in the proof concludes the Prop",
        "absent": "the Prop is not in the formal proof",
    }
    out["packages"] = {}
    for p in pkgs:
        on = [(a, b) for (a, b), ps in arrows.items() if p in ps]
        out["packages"][p] = {
            "fields": sorted({b for _, b in on}),
            "taken_by": sorted({a for a, _ in on}),
            "builders": [{"name": n, "statement": lean_owner.get(n), "reached_from": sorted(reached_from.get(n, []))}
                         for n in sorted(built.get(p, []))],
        }
    out["arrows"] = {}
    for (a, b), ps in sorted(arrows.items()):
        out["arrows"].setdefault(a, {})[b] = {"packages": ps, "nested": bool(nested.get((a, b)))}
    out["axioms"] = sorted(ix.name(ix.dn[di]) for di in range(len(ix.dn)) if ix.dk[di] == 3)
    out["props"] = {}
    for x, o in sorted(props.items()):
        pb = [{"theorem": n, "statement": lean_owner.get(n), "premises": ps, "package_premises": ks}
              for n, ps, ks in sorted(proved.get(x, []))]
        cls = ("absent" if x not in found else "never" if not pb
               else "outright" if any(not q["premises"] and not q["package_premises"] for q in pb) else "conditional")
        out["props"][x] = {"statement": o, "class": cls, "proved_by": pb}
    sys.stdout.write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    c = collections.Counter(v["class"] for v in out["props"].values())
    print(f"{len(pkgs)} packages over {len(arrows)} arrows ({sum(nested.values())} nested); props: "
          + ", ".join(f"{c[k]} {k}" for k in CLASSES), file=sys.stderr)


if __name__ == "__main__":
    main()
