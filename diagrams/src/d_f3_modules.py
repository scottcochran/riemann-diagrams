"""F3 — The proof as code: the blueprint's chapters against the formalisation's modules.

`lean-facts.json` is the blueprint's index of the formal proof: one entry for each Lean declaration a statement
names, with its kind, module, file and lines. This poster reads that index the other way round. The matrix puts
the blueprint's nine chapters against the formalisation's modules, so that the paper's organisation and the
code's can be compared; the cards are the formalisation's own tree, namespace by namespace; the tables give each
chapter's footprint in the code and the fan-out from one statement to its declarations. The build fails if the
declaration count, the kinds, the module count, the per-chapter counts or the statements without a declaration
differ from what is recorded here, or if any declaration is named by more than one statement."""
import collections

import bp
from bp import code, names
from chapter import band
from lib import Canvas

ID, SLUG = "F3", "modules"

W = 3400
G = 64
S = 13.5
NCOLS = 5
SHORT = {
    "main-theorems": "Main theorems", "architecture": "Outline", "chap-zero-free": "Zero-free",
    "chap-families": "Families", "chap-theta": "Theta", "chap-heights": "Heights", "chap-sha": "Sha",
    "chap-galois": "Galois", "chap-literature": "Literature",
}
N_DECLS = 1194
KINDS = {"theorem": 827, "definition": 326, "structure": 40, "inductive": 1}
N_MODULES2 = 35
NO_LEAN = ["rem-local-parameters-weak", "rem-points-to-check", "thm-theta-inputs"]
# Declarations named by each chapter's statements.
EXPECTED = {
    "main-theorems": 32, "architecture": 25, "chap-zero-free": 78, "chap-families": 136, "chap-theta": 180,
    "chap-heights": 100, "chap-sha": 101, "chap-galois": 97, "chap-literature": 445,
}
TOP_N = 12


def ranked(counter, n=None):
    """(key, count) by count descending then key, so that ties do not depend on insertion order."""
    items = sorted(counter.items(), key=lambda t: (-t[1], str(t[0])))
    return items if n is None else items[:n]


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    lf = g.lean_facts
    if set(SHORT) != g.chapters:
        raise ValueError("F3: SHORT must name exactly the blueprint's chapters")
    chapters = sorted(g.chapters, key=lambda ch: (g.nodes[ch].get("order", 0), ch))

    def chap(k):
        return g.nodes[k]["_chapter"]

    named_by = {}
    for k in sorted(g.statements):
        for x in g.nodes[k].get("lean", []):
            if x in named_by:
                raise ValueError(f"F3: {x} is named by {named_by[x]} and {k}; the poster assumes one statement each")
            if x not in lf:
                raise ValueError(f"F3: {k} names {x}, which lean-facts.json does not record")
            named_by[x] = k
    if len(lf) != N_DECLS or set(lf) != set(named_by):
        raise ValueError(f"F3: lean-facts.json has {len(lf)} declarations, {len(named_by)} named; written for {N_DECLS}, all named")
    kinds = collections.Counter(v["kind"] for v in lf.values())
    if dict(kinds) != KINDS:
        raise ValueError(f"F3: declaration kinds are {dict(kinds)}, written for {KINDS}")
    for x, v in lf.items():
        if not v.get("module") or not v.get("range"):
            raise ValueError(f"F3: {x} has no module or range in lean-facts.json")
    no_lean = sorted(k for k in g.statements if not g.nodes[k].get("lean"))
    if no_lean != NO_LEAN:
        raise ValueError(f"F3: statements without a declaration are {no_lean}, written for {NO_LEAN}")
    per_chapter = collections.Counter(chap(k) for x, k in named_by.items())
    if dict(per_chapter) != EXPECTED:
        raise ValueError(f"F3: declarations per chapter are {dict(per_chapter)}, written for {EXPECTED}")

    def mod(x):
        return lf[x]["module"]

    def top(x, n):
        return ".".join(mod(x).split(".")[:n])

    def lines(x):
        r = lf[x]["range"]
        return r["endLine"] - r["startLine"] + 1

    def src(x):
        """The file under the proof's src/, or the dependency's path under .lake/packages/."""
        f = lf[x]["range"]["file"]
        return f.split("/src/", 1)[1] if "/src/" in f and not f.startswith(".lake/packages/mathlib") else f

    decls = sorted(lf)
    t1 = collections.Counter(top(x, 1) for x in decls)
    t2 = collections.Counter(top(x, 2) for x in decls)
    if len(t2) != N_MODULES2:
        raise ValueError(f"F3: {len(t2)} second-level modules, written for {N_MODULES2}")
    M = collections.Counter((chap(named_by[x]), top(x, 2)) for x in decls)
    MS = collections.defaultdict(set)
    for x in decls:
        MS[(chap(named_by[x]), top(x, 2))].add(named_by[x])
    n_modules = len({mod(x) for x in decls})
    n_files = len({lf[x]["range"]["file"] for x in decls})
    n_lines = sum(lines(x) for x in decls)
    fan = collections.Counter(len(g.nodes[k].get("lean", [])) for k in g.statements)
    pairs = collections.Counter(tuple(sorted(lf[x]["kind"] for x in g.nodes[k]["lean"]))
                                for k in g.statements if len(g.nodes[k].get("lean", [])) == 2)
    if pairs[("definition", "theorem")] * 2 <= fan[2]:
        raise ValueError(f"F3: {pairs[('definition', 'theorem')]} of the {fan[2]} statements naming two declarations "
                         "name a definition and a theorem, no longer a majority; re-read the fan-out sentence of "
                         "the key card")

    c = Canvas(ID, "The proof as code: the blueprint's nine chapters against the formalisation's modules, and what "
               "each statement stands for in Lean",
               f"`lean-facts.json` is the blueprint's index of the formal proof: one entry for each of the "
               f"{len(decls)} Lean declarations a statement names, with its kind, module, file and lines. Every "
               f"declaration is named by exactly one statement, and {len(g.statements) - len(no_lean)} of the "
               f"{len(g.statements)} statements name at least one. This poster reads the index the other way "
               "round. **The matrix** puts the chapters of the blueprint against the modules of the formalisation, "
               "so that the paper's organisation and the code's can be compared: they are not the same tree. "
               "**The cards** are the formalisation's own tree, namespace by namespace, as far as the index sees "
               "it. **The tables** give each chapter's footprint in the code and the fan-out from one statement to "
               "the declarations it stands for. The index covers what the blueprint names, not the whole "
               "formalisation; what a declaration proves, and whether it is proved, is not in it. **No Lean was "
               "built**: see diagram R1, band 5."
               + (" **Map mode**: this poster quotes nothing in either form." if bp.MAP else ""),
               W, f"`riemann-blueprint` at {g.bp_commit} (`lean-facts.json`: every declaration's kind, module, "
               "file and lines; every statement's `lean` list and chapter); `leanprover-community/"
               f"riemann-hypothesis` at {mirror['commit']} (`src/Main.lean`). Every count is the diagram's own; "
               "the namespace cards and the chapter labels are the diagram's own grouping of the index's module "
               "names.",
               state=f"State drawn: riemann-blueprint at {g.bp_commit}, which pins the mirror at {g.mirror_pin}; "
                     f"Main.lean from the mirror at {mirror['commit']}")
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    CW = (WW - 4 * G) / 5

    def colx(i):
        return X0 + i * (CW + G)

    def span(n):
        return n * CW + (n - 1) * G

    # ---------------------------------------------------------------------------------- reading the poster
    y = c.y
    y = band(c, X0, y, "1 · Reading the poster")
    key = [
        "**A module** is a Lean file; its dotted name is its path under `src/`. The matrix groups declarations by "
        "the first two parts of that name, the namespace and the theory under it, and the cards go one part "
        "deeper. A module is one file, so modules and files count the same; a file may hold several declarations.",
        "**A cell of the matrix** counts the declarations in that module that statements of that chapter name. "
        "The last column counts the statements doing the naming. Where a chapter's row is spread across many "
        "modules, the paper's chapter is drawn from several theories of the code; where a module's column is "
        "spread across chapters, one theory of the code serves several chapters.",
        "**Lines spanned** is the sum of each declaration's line range in its file, as the index records it: the "
        "size of the declarations themselves, not of the proofs they depend on.",
        "**Fan-out** is how many declarations one statement names. A statement that names two usually names a "
        "definition and a theorem, the pattern diagram R1 shows for the five theorems of `Main.lean`: a `Prop` "
        "and the theorem that proves it. The index records the pairing; it does not say which is which.",
    ]
    nums = [
        f"**{len(decls)} declarations** in {n_modules} modules and {n_files} files, spanning {n_lines:,} lines: "
        + ", ".join(f"{v} {k}s" for k, v in ranked(kinds)) + ".",
        f"**{len(t1)} namespaces**: " + ", ".join(f"`{k}` {v}" for k, v in ranked(t1)) + ".",
        f"**{len(t2)} theories** at the second level; the three largest, "
        + ", ".join(f"`{k}` ({v})" for k, v in ranked(t2, 3))
        + f", hold {sum(v for _, v in ranked(t2, 3)) * 100 // len(decls)}% of the declarations.",
        f"**{len(g.statements) - len(no_lean)} of {len(g.statements)} statements** name a declaration; the three "
        "that do not are " + names(no_lean) + ". **Each declaration is named by one statement**; none is shared.",
        f"**Fan-out**: " + ", ".join(f"{fan[n]} name {n}" for n in sorted(fan)) + f". Of the {fan[2]} that name two, "
        + ", ".join(f"{v} name a {a} and a {b}" if a != b else f"{v} name two {a}s" for (a, b), v in ranked(pairs))
        + ".",
        f"**One declaration carries a docstring** in the index: " + ", ".join(
            code(x) for x in decls if lf[x].get("doc")) + ".",
    ]
    hk = max(c.card(0, 0, span(3), "How to read the poster", key, draw=False, size=S),
             c.card(0, 0, span(2), "The index in numbers", nums, draw=False, size=S))
    c.card(colx(0), y, span(3), "How to read the poster", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(3), y, span(2), "The index in numbers", nums, "teal", h=hk, size=S, tint=False)
    y += hk + 50

    # ---------------------------------------------------------------------------------- the matrix
    y = band(c, X0, y, "2 · Chapters against modules",
             "Rows: the formalisation's modules to the second level, grouped by namespace, largest first. Columns: "
             "the blueprint's chapters in its order. A cell counts the declarations of that module named by "
             "statements of that chapter.")
    mcols = [("Module", 460, {"mono": True}), ("Decls", 110, {"bold": True})]
    cw = (WW - 460 - 110 - 150 - 100) / len(chapters)
    mcols += [(SHORT[ch], cw) for ch in chapters] + [("Statements", 150), ("Files", 100)]
    mrows = []
    for ns, n_ns in ranked(t1):
        mods = [(m, v) for m, v in ranked(t2) if m.split(".")[0] == ns]
        mrows.append({"group": f"{ns}: {n_ns} declarations in {len(mods)} " + ("theory" if len(mods) == 1 else "theories"),
                      "accent": "grey"})
        for m, v in mods:
            cells = [m, str(v)]
            for ch in chapters:
                cells.append(str(M[(ch, m)]) if M[(ch, m)] else "")
            cells.append(str(len({k for ch in chapters for k in MS[(ch, m)]})))
            cells.append(str(len({lf[x]["range"]["file"] for x in decls if top(x, 2) == m})))
            mrows.append(cells)
    mrows.append(["Declarations named by the chapter", str(len(decls))]
                 + [str(per_chapter[ch]) for ch in chapters]
                 + [str(len(g.statements) - len(no_lean)), str(n_files)])
    y += c.table(X0, y, mcols, mrows, size=S) + 50

    # ---------------------------------------------------------------------------------- the tree
    y = band(c, X0, y, "3 · The formalisation's own tree, as far as the index sees it",
             f"One card per namespace, largest first: its theories with their declarations, sub-modules and "
             "kinds, and the chapters whose statements name them most.")
    cards = []
    for ns, n_ns in ranked(t1):
        xs = [x for x in decls if top(x, 1) == ns]
        bullets = []
        for m, v in [(m, v) for m, v in ranked(t2) if m.split(".")[0] == ns]:
            ys = [x for x in xs if top(x, 2) == m]
            sub = len({top(x, 3) for x in ys})
            kk = collections.Counter(lf[x]["kind"] for x in ys)
            chs = collections.Counter(chap(named_by[x]) for x in ys)
            short = m.split(".", 1)[1] if "." in m else "(the namespace itself)"
            bullets.append(f"**{short}** {v}: " + ", ".join(f"{n_} {k}{'s' if n_ > 1 else ''}" for k, n_ in ranked(kk))
                           + (f" in {sub} sub-modules" if sub > 1 else "")
                           + "; named by " + ", ".join(f"{SHORT[ch]} {n_}" for ch, n_ in ranked(chs, 3))
                           + (" …" if len(chs) > 3 else ""))
        files = {lf[x]["range"]["file"] for x in xs}
        root = sorted({src(x).split("/")[0] for x in xs})
        dep = [r for r in root if r.startswith(".lake")]
        foot = [("**Under** " + ", ".join(f"`src/{r}`" for r in root if r not in dep)
                 + (" · a dependency, under `.lake/packages/`, not the proof's own tree" if dep else "")).replace("**Under**  ·", "**Under**"),
                f"**{len(files)} files**, {sum(lines(x) for x in xs):,} lines spanned",
                "**Named by** " + ", ".join(f"{SHORT[ch]} {n_}" for ch, n_ in ranked(collections.Counter(chap(named_by[x]) for x in xs)))]
        cards.append(dict(name=ns, pill=f"{n_ns} declarations", bullets=bullets, foot=foot, formula=[],
                          accent="teal" if ns == "Development" else "grey", title_mono=True))
    for i in range(0, len(cards), NCOLS):
        chunk = cards[i:i + NCOLS]
        hh = max(bp.node(c, 0, 0, CW, draw=False, **kw) for kw in chunk)
        for j, kw in enumerate(chunk):
            bp.node(c, colx(j), y, CW, h=hh, **kw)
        y += hh + 30
    y += 20

    # ---------------------------------------------------------------------------------- the chapters
    y = band(c, X0, y, "4 · Each chapter's footprint in the code",
             "What the statements of each chapter stand for in Lean, counted from the index.")
    crows = []
    for ch in chapters:
        st = sorted(k for k in g.statements if chap(k) == ch)
        xs = [x for k in st for x in g.nodes[k].get("lean", [])]
        kk = collections.Counter(lf[x]["kind"] for x in xs)
        with_lean = sum(1 for k in st if g.nodes[k].get("lean"))
        mods = collections.Counter(top(x, 2) for x in xs)
        crows.append([f"{g.nodes[ch].get('order')}. {g.nodes[ch]['title']}", str(len(st)), str(with_lean), str(len(xs)),
                      str(kk["theorem"]), str(kk["definition"]), str(kk["structure"] + kk["inductive"]),
                      f"{len(xs) / with_lean:.1f}" if with_lean else "—", str(len(mods)),
                      str(len({lf[x]["range"]["file"] for x in xs})), f"{sum(lines(x) for x in xs):,}",
                      ", ".join(f"`{m}` {v}" for m, v in ranked(mods, 3))])
    crows.append(["**All chapters**", str(len(g.statements)), str(len(g.statements) - len(no_lean)), str(len(decls)),
                  str(kinds["theorem"]), str(kinds["definition"]), str(kinds["structure"] + kinds["inductive"]),
                  f"{len(decls) / (len(g.statements) - len(no_lean)):.1f}", str(len(t2)), str(n_files), f"{n_lines:,}", ""])
    ccols = [("Chapter", 520), ("Stmts", 90), ("With Lean", 110), ("Decls", 90), ("Theorems", 110), ("Defs", 90),
             ("Structs", 100), ("Per stmt", 100), ("Theories", 100), ("Files", 90), ("Lines", 110),
             ("Theories named most", WW - 520 - 90 - 110 - 90 - 110 - 90 - 100 - 100 - 100 - 90 - 110)]
    y += c.table(X0, y, ccols, crows, size=S) + 50

    # ---------------------------------------------------------------------------------- fan-out
    y = band(c, X0, y, "5 · From one statement to its declarations",
             f"The {TOP_N} statements that name the most declarations, with the theories those declarations sit in; "
             "and the fan-out of the whole blueprint.")
    frows = []
    for k in sorted(g.statements, key=lambda k: (-len(g.nodes[k].get("lean", [])), k))[:TOP_N]:
        xs = g.nodes[k]["lean"]
        kk = collections.Counter(lf[x]["kind"] for x in xs)
        mods = collections.Counter(top(x, 2) for x in xs)
        frows.append({"cells": [k, g.nodes[k]["title"], SHORT[chap(k)], bp.PROV_SHORT[g.nodes[k].get("provenance")],
                                str(len(xs)), ", ".join(f"{v} {a}{'s' if v > 1 else ''}" for a, v in ranked(kk)),
                                ", ".join(f"`{m}` {v}" for m, v in ranked(mods, 4)) + (" …" if len(mods) > 4 else "")],
                      "accent": bp.PROV_ACCENT[g.nodes[k].get("provenance")]})
    fcols = [("Statement", 380, {"mono": True}), ("Title", 560), ("Chapter", 130), ("Provenance", 120),
             ("Decls", 80), ("Kinds", 330), ("Theories", WW - 380 - 560 - 130 - 120 - 80 - 330 - 700)]
    fh = c.table(X0, y, fcols, frows, size=S)
    hrows = [[str(n), str(fan[n]), f"{fan[n] * 100 // len(g.statements)}%"] for n in sorted(fan)]
    hh = c.table(X1 - 640, y, [("Declarations named", 260), ("Statements", 200), ("Share", 180)], hrows, size=S)
    return c
