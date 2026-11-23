"""F7 — The blueprint against the Lean: every arrow checked against the formal proof, chapter by chapter.

Reads src/lean-edges.json (bp.read_edges), the verdict on each blueprint arrow from the published proof's
references, and lays it out by chapter: a matrix of the arrows borne out between each pair of chapters, a matrix
of the uses the Lean makes that the blueprint draws no arrow for, the statements the disagreements concentrate
in, the statements that use most beyond their arrows, and each statement's depth from the main theorems in the
blueprint against its depth in the Lean. The build fails if the counts by verdict, the statements the
disagreements concentrate in, or the depth moves differ from what is recorded here."""
import collections

import bp
from chapter import band
from lib import Canvas

ID, SLUG = "F7", "verdicts"

W = 3400
G = 64
S = 13.5
SHORT = {
    "main-theorems": "Main theorems", "architecture": "Outline", "chap-zero-free": "Zero-free",
    "chap-families": "Families", "chap-theta": "Theta", "chap-heights": "Heights", "chap-sha": "Sha",
    "chap-galois": "Galois", "chap-literature": "Literature",
}
BORNE = ("direct", "hypothesis", "through")
NOT = ("beside", "apart")
NOLEAN = ("no-lean-source", "no-lean-target")
# The arrows by verdict, as the file gives them.
COUNTS = {"direct": 1549, "hypothesis": 157, "through": 54, "beside": 19, "apart": 148, "no-lean-source": 74,
          "no-lean-target": 3}
# The statements most of the arrows not borne out leave from, with how many; every other has at most OTHERS_MAX.
CONCENTRATED = {"prop-theta-integrals-along-towers": 53, "thm-kato-zeta-integral": 37}
OTHERS_MAX = 4
# Depth: how many statements the Lean puts each number of rungs deeper (+) or shallower (-) than the blueprint.
MOVES = {-3: 3, -2: 24, -1: 82, 0: 146, 1: 28, 2: 112, 3: 11}
TOP_N = 12


def ranked(counter, n=None):
    items = sorted(counter.items(), key=lambda t: (-t[1], str(t[0])))
    return items if n is None else items[:n]


def bfs(roots, nxt):
    """Breadth-first depth from `roots` over nxt(k) -> iterable of successors."""
    d, frontier = {r: 0 for r in roots}, sorted(roots)
    while frontier:
        new = []
        for a in frontier:
            for b in sorted(nxt(a)):
                if b not in d:
                    d[b] = d[a] + 1
                    new.append(b)
        frontier = sorted(new)
    return d


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    lean = bp.read_edges(g)
    if set(SHORT) != g.chapters:
        raise ValueError("F7: SHORT must name exactly the blueprint's chapters")
    chapters = sorted(g.chapters, key=lambda ch: (g.nodes[ch].get("order", 0), ch))

    def chap(k):
        return g.nodes[k]["_chapter"]

    arrows = [(a, b, v) for a, us in sorted(lean.raw["arrows"].items()) for b, v in sorted(us.items())]
    counts = collections.Counter(v for _, _, v in arrows)
    if {k: counts[k] for k in COUNTS} != COUNTS or set(counts) - set(COUNTS):
        raise ValueError(f"F7: the arrows by verdict are {dict(counts)}, written for {COUNTS}")
    not_by = collections.Counter(a for a, _, v in arrows if v in NOT)
    top = dict(ranked(not_by, len(CONCENTRATED)))
    if top != CONCENTRATED or max(n for k, n in not_by.items() if k not in CONCENTRATED) != OTHERS_MAX:
        raise ValueError(f"F7: the arrows not borne out leave most from {ranked(not_by, 4)}, written for "
                         f"{CONCENTRATED} and at most {OTHERS_MAX} from any other")
    undrawn = {a: sorted(lean.undrawn(a)) for a in sorted(g.statements)}
    n_undrawn = sum(len(v) for v in undrawn.values())

    roots = g.roots()
    bd, _ = g.depths(roots)
    fd = bfs(roots, lean.formal)
    st = sorted(g.statements)
    both = [k for k in st if k in bd and k in fd]
    moves = collections.Counter(fd[k] - bd[k] for k in both)
    if dict(moves) != MOVES:
        raise ValueError(f"F7: the depth moves are {dict(sorted(moves.items()))}, written for {MOVES}")
    only_bp = [k for k in st if k in bd and k not in fd]
    only_lean = [k for k in st if k in fd and k not in bd]
    judged = sum(counts[v] for v in BORNE + NOT)
    borne = sum(counts[v] for v in BORNE)

    c = Canvas(ID, "The blueprint against the Lean: every arrow checked against the formal proof, chapter by "
               "chapter",
               f"The blueprint draws {len(arrows):,} arrows between its statements, read from its source text. "
               "Each was checked against the references of the published formal proof: does the Lean of the "
               "statement that uses reach the Lean of the statement used? The references were read from Andrew "
               "Sutherland's export of the proof, which holds exactly what the five main theorems depend on, and "
               "cross-checked against the mirror's build cache; `diagrams/EDGES.md` gives the method. **Of the "
               f"{judged:,} arrows that can be judged, {borne:,} are borne out.** This poster lays the verdicts "
               "out by chapter, shows where the rest concentrate, lists what the Lean uses that the blueprint "
               "does not draw, and compares each statement's depth from the main theorems in the two graphs. The "
               "chapter posters draw the same verdicts arrow by arrow. **No Lean was built**: see diagram R1, "
               "band 5." + (" **Map mode**: this poster quotes nothing in either form." if bp.MAP else ""),
               W, f"`riemann-blueprint` at {g.bp_commit} (every statement's chapter and `uses`; the depths); "
               "`diagrams/src/lean-edges.json`, the verdicts on the blueprint's arrows from Sutherland's export of "
               f"the proof at {g.mirror_pin} (sha256 {lean.export_sha256[:12]}…), cross-checked against the mirror "
               "at c900e67c2f; `leanprover-community/riemann-hypothesis` at "
               f"{mirror['commit']} (`src/Main.lean`). Every count is the diagram's own.",
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
        "**An arrow** A → B of the blueprint says that A uses B, in its statement or its proof. Here it is "
        "counted in A's row and B's column: rows are the chapters that use, columns the chapters used.",
        "**Borne out**: A's Lean reaches B's, directly through helper declarations no statement names, as a "
        "hypothesis through the fields of a structure A takes, or only by way of other statements. **Not borne "
        "out**: A's Lean never reaches B's. Of these, **beside** means a proof that uses both applies them "
        "together, and **apart** means not even that. **Cannot be judged**: A or B names no Lean that the proof "
        "contains.",
        "**Uses with no arrow** are the statements A's Lean uses directly that the blueprint gives A no arrow "
        "to. The Lean is more explicit than prose: many are definitions a statement is phrased in.",
        "**Depth** is the breadth-first distance from the three theorems nothing uses, along the blueprint's "
        "arrows (as on F6) or along the Lean's direct uses.",
    ]
    cross = lean.raw["cross_check"]
    nums = [
        f"**{len(arrows):,} arrows** between {len(lean.raw['arrows'])} statements that use: "
        + ", ".join(f"{counts[v]:,} {v}" for v in COUNTS) + ".",
        f"**{borne:,} of {judged:,} judged** are borne out ({borne * 100 // judged}%): {counts['direct']:,} "
        f"directly, {counts['hypothesis']} as hypotheses, {counts['through']} by way of other statements.",
        f"**{n_undrawn:,} uses with no arrow**, made by {sum(1 for v in undrawn.values() if v)} statements.",
        f"**{len(lean.raw['lean_not_in_proof'])} statements** name Lean that the proof does not contain, "
        f"{sum(map(len, lean.raw['lean_not_in_proof'].values()))} names in all; `diagrams/EDGES.md` lists "
        "them.",
        f"**The cross-check** against the mirror at c900e67c2f differs on "
        f"{sum(map(len, cross['differs'].values()))} arrows.",
    ]
    hk = max(c.card(0, 0, span(3), "How to read the poster", key, draw=False, size=S),
             c.card(0, 0, span(2), "The verdicts in numbers", nums, draw=False, size=S))
    c.card(colx(0), y, span(3), "How to read the poster", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(3), y, span(2), "The verdicts in numbers", nums, "teal", h=hk, size=S, tint=False)
    y += hk + 50

    # ---------------------------------------------------------------------------------- the arrows matrix
    y = band(c, X0, y, "2 · The arrows, chapter against chapter",
             "Each cell gives the arrows from statements of the row's chapter to statements of the column's that "
             "are borne out, over those that can be judged, and in bold how many are not. The last columns total "
             "the row.")
    cell = collections.defaultdict(collections.Counter)
    for a, b, v in arrows:
        cell[(chap(a), chap(b))][v] += 1
    lab_w, tail = 300, [("Arrows", 120), ("Borne out", 140), ("Not", 90), ("No Lean", 120), ("Share", 110)]
    cw = (WW - lab_w - sum(w for _, w in tail)) / len(chapters)
    mcols = [("Uses ↓ · used →", lab_w)] + [(SHORT[ch], cw) for ch in chapters] + tail
    mrows = []
    for r in chapters:
        cells, tot = [f"**{SHORT[r]}**"], collections.Counter()
        for col in chapters:
            x = cell[(r, col)]
            tot.update(x)
            j = sum(x[v] for v in BORNE + NOT)
            nb = sum(x[v] for v in NOT)
            cells.append("" if not j else f"{j - nb}/{j}" + (f", **{nb} not**" if nb else ""))
        j = sum(tot[v] for v in BORNE + NOT)
        nb = sum(tot[v] for v in NOT)
        cells += [str(sum(tot.values())), str(j - nb), str(nb) if nb else "", str(sum(tot[v] for v in NOLEAN) or ""),
                  f"{(j - nb) * 100 // j}%" if j else "—"]
        mrows.append(cells)
    mrows.append([f"**All**"] + [""] * len(chapters)
                 + [str(len(arrows)), str(borne), str(judged - borne), str(sum(counts[v] for v in NOLEAN)),
                    f"{borne * 100 // judged}%"])
    y += c.table(X0, y, mcols, mrows, size=S) + 50

    # ---------------------------------------------------------------------------------- the undrawn matrix
    y = band(c, X0, y, "3 · What the Lean uses that the blueprint does not draw, chapter against chapter",
             "Each cell counts the uses from statements of the row's chapter to statements of the column's that "
             "the Lean makes and no arrow records.")
    ucell = collections.Counter((chap(a), chap(b)) for a, bs in undrawn.items() for b in bs)
    ucols = [("Uses ↓ · used →", lab_w)] + [(SHORT[ch], cw) for ch in chapters] + [("Total", 120),
                                                                                    ("Statements", 140)]
    urows = []
    for r in chapters:
        cells = [f"**{SHORT[r]}**"] + [str(ucell[(r, col)]) if ucell[(r, col)] else "" for col in chapters]
        cells += [str(sum(ucell[(r, col)] for col in chapters)),
                  str(sum(1 for a, bs in undrawn.items() if bs and chap(a) == r))]
        urows.append(cells)
    urows.append(["**All**"] + [str(sum(ucell[(r, col)] for r in chapters)) for col in chapters]
                 + [str(n_undrawn), str(sum(1 for v in undrawn.values() if v))])
    y += c.table(X0, y, ucols, urows, size=S) + 50

    # ---------------------------------------------------------------------------------- where the trouble is
    y = band(c, X0, y, "4 · Where the arrows not borne out concentrate, and who uses most beyond its arrows",
             f"Left: the statements with the most arrows the Lean does not bear out. {len(not_by)} statements have "
             f"at least one; two hold {sum(CONCENTRATED.values())} of the {judged - borne}. Right: the statements "
             "whose Lean makes the most uses no arrow records.")
    half = (WW - G) / 2
    lrows = []
    for k, n in ranked(not_by, TOP_N):
        mine = [v for a, _, v in arrows if a == k]
        lrows.append({"cells": [k, SHORT[chap(k)], str(len(mine)), str(sum(v in BORNE for v in mine)),
                                str(sum(v == "beside" for v in mine)), str(sum(v == "apart" for v in mine))],
                      "accent": "red" if k in CONCENTRATED else "grey"})
    lcols = [("Statement", half - 560, {"mono": True}), ("Chapter", 140), ("Arrows", 100), ("Borne out", 120),
             ("Beside", 100), ("Apart", 100)]
    lh = c.table(X0, y, lcols, lrows, size=S)
    rrows = []
    for k, bs in sorted(undrawn.items(), key=lambda t: (-len(t[1]), t[0]))[:TOP_N]:
        by = collections.Counter(SHORT[chap(b)] for b in bs)
        rrows.append([k, SHORT[chap(k)], str(len(bs)), ", ".join(f"{ch_} {n}" for ch_, n in ranked(by, 3))])
    rcols = [("Statement", half - 700, {"mono": True}), ("Chapter", 140), ("No arrow", 110), ("In chapters", 450)]
    rh = c.table(X0 + half + G, y, rcols, rrows, size=S)
    y += max(lh, rh) + 50

    # ---------------------------------------------------------------------------------- depth
    y = band(c, X0, y, "5 · Depth from the main theorems: the blueprint's against the Lean's",
             f"{len(both)} statements are reached in both graphs. A row is a depth in the blueprint, a column a "
             "depth in the Lean; a cell counts the statements at both. The diagonal is where the two agree.")
    maxb, maxf = max(bd[k] for k in both), max(fd[k] for k in both)
    xt = collections.Counter((bd[k], fd[k]) for k in both)
    dw = (WW * 0.62 - 260 - 120) / (maxf + 1)
    dcols = [("Blueprint ↓ · Lean →", 260)] + [(str(j), dw) for j in range(maxf + 1)] + [("Total", 120)]
    drows = []
    for i in range(maxb + 1):
        cells = [f"**{i}**"] + [(f"**{xt[(i, j)]}**" if i == j else str(xt[(i, j)])) if xt[(i, j)] else ""
                                for j in range(maxf + 1)]
        drows.append(cells + [str(sum(xt[(i, j)] for j in range(maxf + 1)))])
    dh = c.table(X0, y, dcols, drows, size=S)
    mx = X0 + WW * 0.62 + G
    mw = X1 - mx
    mrows2 = [[f"{m:+d}" if m else "0", str(moves[m]),
               "deeper in the Lean" if m > 0 else "shallower in the Lean" if m < 0 else "the same depth"]
              for m in sorted(moves)]
    mh = c.table(mx, y, [("Move", 110), ("Statements", 140), ("", mw - 250)], mrows2, size=S)
    far = sorted((k for k in both if abs(fd[k] - bd[k]) >= 3), key=lambda k: (-(fd[k] - bd[k]), k))
    note = [f"**{moves[0]} of {len(both)}** statements sit at the same depth in both graphs. The Lean puts "
            f"{sum(n for m, n in moves.items() if m > 0)} deeper, {moves.get(2, 0)} of them by two, and "
            f"{sum(n for m, n in moves.items() if m < 0)} shallower.",
            f"**Moved three or more**: " + ", ".join(f"`{k}` ({bd[k]} → {fd[k]})" for k in far) + ".",
            f"**Reached in one graph only**: in the blueprint's, " + (", ".join(f"`{k}`" for k in only_bp) or "none")
            + "; in the Lean's, " + (", ".join(f"`{k}`" for k in only_lean) or "none") + "."]
    nh = c.card(mx, y + mh + 24, mw, "The moves", note, "teal", size=S, tint=False)
    y += max(dh, mh + 24 + nh) + 30
    return c
