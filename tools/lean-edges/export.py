"""Index a lean4export 3.1 NDJSON export (Sutherland's solution.ndjson: the published archive's proof, Lean
v4.33.1) into flat arrays on disk, and answer reachability questions over it.

  export.py ingest <index dir>  < solution.ndjson     one streaming pass; pipe it from `zstd -dc --long=30`
  export.py query <index dir> <questions.json>        reachability, written as JSON to stdout

The export is lines of three kinds, each with a sequential id and defined before anything refers to it: names
("in": a string or number component on a prefix), universe levels ("il", ignored here), and expressions ("ie").
Declarations ("thm", "def", "opaque", "axiom", "quot", "inductive") point at expression ids for their type and
value; an "inductive" record carries its types, constructors and recursors. The ingest keeps, per expression, a
kind and up to three operands (int32), written in id order:

  const  a = name            app   a = fn, b = arg           lam/forallE  a = binder type, b = body
  letE   a = type, b = value, c = body (a side table)        proj  a = struct expr, b = structure name
  other  (bvar, sort, natVal, strVal)

and per name its prefix and component (a blob), and per declaration its name, kind, type and value. A query
walks the declarations reachable from some starting declarations: each declaration's expressions are walked
iteratively, each expression once per query, and every constant met (and a projection's structure) is a
declaration reached; with `fields`, an inductive also leads to its constructors, as edges.py does.
"""
import array
import collections
import json
import mmap
import os
import pathlib
import sys

import orjson

K_OTHER, K_CONST, K_APP, K_LAM, K_FORALL, K_LET, K_PROJ = range(7)
DKIND = ["thm", "def", "opaque", "axiom", "quot", "inductive", "ctor", "recursor"]


class Out:
    """Append-only int arrays flushed to files in chunks."""

    def __init__(self, path, code):
        self.f = open(path, "wb")
        self.a = array.array(code)

    def add(self, x):
        self.a.append(x)
        if len(self.a) >= 1 << 22:
            self.flush()

    def flush(self):
        self.a.tofile(self.f)
        del self.a[:]

    def close(self):
        self.flush()
        self.f.close()


def ingest(d):
    d.mkdir(parents=True, exist_ok=True)
    ek, ea, eb = Out(d / "e.kind", "b"), Out(d / "e.a", "i"), Out(d / "e.b", "i")
    lc_id, lc_v = Out(d / "let.id", "i"), Out(d / "let.c", "i")
    npre, noff = Out(d / "n.pre", "i"), Out(d / "n.off", "q")
    nblob = open(d / "n.blob", "wb")
    dn, dk, dt, dv = Out(d / "d.name", "i"), Out(d / "d.kind", "b"), Out(d / "d.type", "i"), Out(d / "d.value", "i")
    ctors = {}                                  # inductive name id -> constructor name ids
    npre.add(0); noff.add(0)                    # name 0 is the anonymous name
    next_e, next_n, off, lines = 0, 1, 0, 0

    def decl(name, kind, t, v=-1):
        dn.add(name); dk.add(kind); dt.add(t); dv.add(v)

    for line in sys.stdin.buffer:
        lines += 1
        o = orjson.loads(line)
        if "ie" in o:
            i = o["ie"]
            if i != next_e:
                raise SystemExit(f"expression ids out of order at line {lines}: {i}, expected {next_e}")
            next_e += 1
            if (x := o.get("app")) is not None:
                ek.add(K_APP); ea.add(x["fn"]); eb.add(x["arg"])
            elif (x := o.get("lam")) is not None:
                ek.add(K_LAM); ea.add(x["type"]); eb.add(x["body"])
            elif (x := o.get("forallE")) is not None:
                ek.add(K_FORALL); ea.add(x["type"]); eb.add(x["body"])
            elif (x := o.get("const")) is not None:
                ek.add(K_CONST); ea.add(x["name"]); eb.add(-1)
            elif (x := o.get("letE")) is not None:
                ek.add(K_LET); ea.add(x["type"]); eb.add(x["value"]); lc_id.add(i); lc_v.add(x["body"])
            elif (x := o.get("proj")) is not None:
                ek.add(K_PROJ); ea.add(x["struct"]); eb.add(x["typeName"])
            elif (x := o.get("mdata")) is not None:
                ek.add(K_APP); ea.add(x["expr"]); eb.add(-1)
            else:
                ek.add(K_OTHER); ea.add(-1); eb.add(-1)
        elif "in" in o:
            i = o["in"]
            if i != next_n:
                raise SystemExit(f"name ids out of order at line {lines}: {i}, expected {next_n}")
            next_n += 1
            x = o.get("str") or o.get("num")
            comp = x["str"] if "str" in x else str(x["i"])
            b = comp.encode("utf-8")
            npre.add(x["pre"]); nblob.write(b); off += len(b); noff.add(off)
        elif "il" in o or "meta" in o:
            continue
        elif (x := o.get("thm")) is not None:
            decl(x["name"], 0, x["type"], x["value"])
        elif (x := o.get("def")) is not None:
            decl(x["name"], 1, x["type"], x["value"])
        elif (x := o.get("opaque")) is not None:
            decl(x["name"], 2, x["type"], x["value"])
        elif (x := o.get("axiom")) is not None:
            decl(x["name"], 3, x["type"])
        elif (x := o.get("quot")) is not None:
            decl(x["name"], 4, x["type"])
        elif (x := o.get("inductive")) is not None:
            for t in x["types"]:
                decl(t["name"], 5, t["type"])
                ctors[t["name"]] = t["ctors"]
            for c in x["ctors"]:
                decl(c["name"], 6, c["type"])
            for r in x["recs"]:
                decl(r["name"], 7, r["type"])
        else:
            raise SystemExit(f"unknown record at line {lines}: {line[:200]!r}")
        if lines % 50_000_000 == 0:
            print(f"  {lines:,} lines, {next_e:,} expressions, {next_n:,} names", file=sys.stderr, flush=True)
    for o_ in (ek, ea, eb, lc_id, lc_v, npre, noff, dn, dk, dt, dv):
        o_.close()
    nblob.close()
    (d / "ctors.json").write_text(json.dumps({str(k): v for k, v in ctors.items()}))
    (d / "counts.json").write_text(json.dumps({"lines": lines, "expressions": next_e, "names": next_n}))
    print(f"{lines:,} lines, {next_e:,} expressions, {next_n:,} names", file=sys.stderr)


class Index:
    def __init__(self, d):
        def mm(name, code):
            f = open(d / name, "rb")
            if os.path.getsize(d / name) == 0:
                return memoryview(b"").cast(code)
            return memoryview(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)).cast(code)
        self.ek, self.ea, self.eb = mm("e.kind", "b"), mm("e.a", "i"), mm("e.b", "i")
        self.letc = dict(zip(mm("let.id", "i"), mm("let.c", "i")))
        self.npre, self.noff = mm("n.pre", "i"), mm("n.off", "q")
        self.nblob = mm("n.blob", "B")
        self.dn, self.dk, self.dt, self.dv = mm("d.name", "i"), mm("d.kind", "b"), mm("d.type", "i"), mm("d.value", "i")
        self.ctors = {int(k): v for k, v in json.loads((d / "ctors.json").read_text()).items()}
        self.decl_of = {n: i for i, n in enumerate(self.dn)}       # name id -> declaration index
        self._names = {}

    def name(self, n):
        """The full dotted string of name id n."""
        parts = []
        while n and n not in self._names:
            parts.append(bytes(self.nblob[self.noff[n - 1]:self.noff[n]]).decode("utf-8"))
            n = self.npre[n]
        s = self._names.get(n, "")
        for p in reversed(parts):
            s = f"{s}.{p}" if s else p
        return s

    def by_name(self, wanted):
        """Declaration index for each wanted full name present in the export."""
        wanted, out = set(wanted), {}
        for i, n in enumerate(self.dn):
            s = self.name(n)
            if s in wanted:
                out[s] = i
        return out

    def cone(self, starts, fields, targets=(), stop=frozenset()):
        """Declarations reachable from `starts`, and for each target reached, the path from a start. A
        declaration in `stop` is reached but not walked through: with the other statements' declarations as
        `stop`, what is reached is what the starts use directly."""
        ek, ea, eb, letc, dt, dv, dk, dn = self.ek, self.ea, self.eb, self.letc, self.dt, self.dv, self.dk, self.dn
        seen_e = bytearray(len(ek))
        prev = {s: None for s in starts}
        q = collections.deque(starts)
        while q:
            di = q.popleft()
            if di in stop:
                continue
            stack = [e for e in (dt[di], dv[di]) if e >= 0]
            refs = []
            while stack:
                e = stack.pop()
                if seen_e[e]:
                    continue
                seen_e[e] = 1
                k = ek[e]
                if k == K_APP or k == K_LAM or k == K_FORALL:
                    stack.append(ea[e])
                    if eb[e] >= 0:
                        stack.append(eb[e])
                elif k == K_CONST:
                    refs.append(ea[e])
                elif k == K_LET:
                    stack.append(ea[e]); stack.append(eb[e]); stack.append(letc[e])
                elif k == K_PROJ:
                    stack.append(ea[e]); refs.append(eb[e])
            if fields and dk[di] == 5:
                refs.extend(self.ctors.get(dn[di], ()))
            for n in refs:
                j = self.decl_of.get(n)
                if j is not None and j not in prev:
                    prev[j] = di
                    q.append(j)
        paths = {}
        for t in targets:
            if t in prev:
                p, y = [], t
                while y is not None:
                    p.append(self.name(dn[y]))
                    y = prev[y]
                paths[t] = p[::-1]
        return prev, paths


    def mentions(self, names):
        """For up to 8 constants, the declarations whose value (and, separately, type) mentions each. One linear
        pass: an expression is defined before any that uses it, so a flag per expression is the OR of its
        operands' flags and its own constant."""
        ids = {}
        for i, n in enumerate(self.dn):
            s = self.name(n)
            if s in names:
                ids[n] = 1 << len(ids)
        flag = bytearray(len(self.ek))
        ek, ea, eb, letc = self.ek, self.ea, self.eb, self.letc
        for e in range(len(ek)):
            k = ek[e]
            if k == K_CONST:
                flag[e] = ids.get(ea[e], 0)
            elif k == K_APP or k == K_LAM or k == K_FORALL:
                f = flag[ea[e]]
                if eb[e] >= 0:
                    f |= flag[eb[e]]
                flag[e] = f
            elif k == K_LET:
                flag[e] = flag[ea[e]] | flag[eb[e]] | flag[letc[e]]
            elif k == K_PROJ:
                flag[e] = flag[ea[e]] | ids.get(eb[e], 0)
        out = {self.name(n): {"in_value": [], "in_type": []} for n in ids}
        for di in range(len(self.dn)):
            for where, e in (("in_value", self.dv[di]), ("in_type", self.dt[di])):
                if e >= 0 and flag[e]:
                    for n, b in ids.items():
                        if flag[e] & b and self.dn[di] != n:
                            out[self.name(n)][where].append(self.name(self.dn[di]))
        return out


    def conclusion(self, e):
        """The body under every leading ∀ (premise or binder) of a type: its conclusion, as an expression id.
        Identical expressions share an id in the export, so two theorems with the same conclusion (a closed
        proposition such as `VWin`, or one under the same binders) have the same id here."""
        while e >= 0 and self.ek[e] == K_FORALL:
            e = self.eb[e]
        return e


def builders(ix, of):
    """Every theorem whose conclusion is that of one of `of`, other than `of` themselves. A conclusion that is
    not a proposition of its own (a bare sort such as `Prop`, a bound variable) is skipped: it matches every
    declaration of that shape. Returns (matches, skipped names)."""
    want, skipped = {}, []
    for n, di in of.items():
        c = ix.conclusion(ix.dt[di])
        if c < 0 or ix.ek[c] == K_OTHER:
            skipped.append(n)
            continue
        want.setdefault(c, []).append(n)
    own = set(of.values())
    out = collections.defaultdict(list)
    if want:
        for di in range(len(ix.dn)):
            if ix.dk[di] == 0 and di not in own:
                c = ix.conclusion(ix.dt[di])
                if c in want:
                    out[di] = want[c]
    return out, skipped


def users_of_both(m, a_names, b_names):
    """Declarations whose value mentions one of A's declarations and one of B's: A and B applied side by side.
    `m` is the output of Index.mentions for (at least) these names."""
    ua = {u for n in a_names if n in m for u in m[n]["in_value"]}
    ub = {u for n in b_names if n in m for u in m[n]["in_value"]}
    return sorted(ua & ub)


def query(d, qfile):
    """questions.json: {"present": [names], "mentions": [names, at most 8], "cones": [{"label", "from": [names],
    "targets": {stmt: [names]}, "fields": bool}]}. Answers which names the export has, which declarations mention
    each of `mentions`, and for each cone which targets it reaches, with a path, and its size."""
    ix = Index(d)
    qs = json.loads(pathlib.Path(qfile).read_text())
    mentioned = ix.mentions(set(qs["mentions"])) if qs.get("mentions") else {}
    allnames = set(qs.get("present", []))
    for c in qs.get("cones", []):
        allnames |= set(c["from"]) | set(c.get("stop", ()))
        for ns in c["targets"].values():
            allnames |= set(ns)
    found = ix.by_name(allnames)
    out = {"present": {n: n in found for n in qs.get("present", [])}, "mentions": mentioned, "cones": []}
    for c in qs.get("cones", []):
        starts = [found[n] for n in c["from"] if n in found]
        tdecl = {found[n]: s for s, ns in c["targets"].items() for n in ns if n in found}
        stop = frozenset(found[n] for n in c.get("stop", ()) if n in found) - set(starts)
        prev, paths = ix.cone(starts, c.get("fields", True), tdecl, stop)
        print(f"  cone {c['label']}: {len(prev):,} declarations", file=sys.stderr, flush=True)
        reached = {}
        for t, p in paths.items():
            reached.setdefault(tdecl[t], p)
        out["cones"].append({"label": c["label"], "starts_found": [n for n in c["from"] if n in found],
                             "starts_missing": [n for n in c["from"] if n not in found], "cone_size": len(prev),
                             "reached": reached,
                             "not_reached": sorted(s for s in c["targets"] if s not in reached),
                             "targets_absent_from_export": sorted(s for s, ns in c["targets"].items()
                                                                  if not any(n in found for n in ns))})
    # "alternatives": [{"label", "of": [A's names], "targets": {stmt: [names]}}]: theorems proving the same
    # conclusion as one of A's, whether they reach each target (fields followed), and who applies A and B together.
    out["alternatives"] = []
    alts = qs.get("alternatives", [])
    if alts:
        names = set()
        for c in alts:
            names |= set(c["of"]) | {n for ns in c["targets"].values() for n in ns}
        found = ix.by_name(names)
        # Who mentions each name: one linear pass per 8 names, for every source at once.
        pool, m = sorted(n for n in names if n in found), {}
        for k in range(0, len(pool), 8):
            m.update(ix.mentions(set(pool[k:k + 8])))
            print(f"  mentions pass {k // 8 + 1} of {(len(pool) + 7) // 8} done", file=sys.stderr, flush=True)
    for c in alts:
        of = {n: found[n] for n in c["of"] if n in found}
        bl, skipped = builders(ix, of)
        tdecl = {found[n]: s for s, ns in c["targets"].items() for n in ns if n in found}
        res = {"label": c["label"], "of_found": sorted(of), "conclusion_not_a_proposition": skipped,
               "builders": {}, "side_by_side": {}}
        print(f"  alternatives {c['label']}: {len(bl)} theorems with the same conclusion"
              f" ({len(skipped)} of its names skipped)", file=sys.stderr, flush=True)
        for b, concl_of in sorted(bl.items(), key=lambda x: ix.name(ix.dn[x[0]]))[:40]:
            _, paths = ix.cone([b], True, tdecl)
            res["builders"][ix.name(ix.dn[b])] = {"same_conclusion_as": concl_of,
                                                   "reaches": sorted({tdecl[t] for t in paths})}
        res["builders_total"] = len(bl)
        for s, ns in c["targets"].items():
            res["side_by_side"][s] = users_of_both(m, list(of), [n for n in ns if n in found])
        out["alternatives"].append(res)
    json.dump(out, sys.stdout, indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "ingest":
        ingest(pathlib.Path(sys.argv[2]))
    else:
        query(pathlib.Path(sys.argv[2]), sys.argv[3])
