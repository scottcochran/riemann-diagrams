"""F10 — Between the pins: what changed in the formal proof from the commit the blueprint pins to the mirror's head.

Reads src/lean-drift.json (bp.read_drift): the proof's closure at MIRROR_PIN, from Sutherland's export, against its
closure at MIRROR_COMMIT, from the mirror's build cache, closed from the same five theorems of Main.lean and compared
by name. Names are sorted by kind, because the compiler's auxiliaries and private names change with the Lean version
as well as with the proof. Laid out: the two closures by kind; the blueprint's Lean names in each tree; the
user-written names that left the closure and joined it, by namespace; and the statements whose Lean lost the most.
The build fails if the counts differ from what is recorded here."""
import collections

import bp
from chapter import band
from lib import Canvas

ID, SLUG = "F10", "drift"

W = 3400
G = 64
S = 13.5
SHORT = {
    "main-theorems": "Main theorems", "architecture": "Outline", "chap-zero-free": "Zero-free",
    "chap-families": "Families", "chap-theta": "Theta", "chap-heights": "Heights", "chap-sha": "Sha",
    "chap-galois": "Galois", "chap-literature": "Literature",
}
KINDS = ("user", "aux", "private")
KIND_WORD = {"user": "User-written", "aux": "Auxiliary", "private": "Private"}
# The counts, as the file gives them.
BY_KIND = {"left": {"user": 8324, "aux": 199833, "private": 1605}, "joined": {"user": 659, "aux": 20022, "private": 193811}, "stayed": {"user": 795187, "aux": 183627, "private": 81274}}
USER_LEFT = {"total": 8324, "still_compiled": 7693, "gone": 631}
NAME_STATUS = {"in both closures": 1170, "compiled later, not used": 1, "gone from the later tree": 5, "compiled later, no longer used": 8, "in neither tree": 9, "a library name, not compared": 1}
TOP_N = 14
STATUS = {(True, True, True): "in both closures", (True, False, True): "compiled later, no longer used",
          (True, False, False): "gone from the later tree", (False, False, False): "in neither tree",
          (False, False, True): "compiled later, not used", (False, True, True): "new in the later closure"}
LIBRARY = "a library name, not compared"


def status_of(v):
    return LIBRARY if v["library"] else STATUS[(v["earlier"], v["later"], v["compiled_later"])]


def fmt(n):
    return f"{n:,}"


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    d = bp.read_drift(g)
    bk, ul, uj = d["by_kind"], d["user_left"], d["user_joined"]
    if bk != BY_KIND:
        raise ValueError(f"F10: the closures by kind are {bk}, written for {BY_KIND}")
    if {k: ul[k] for k in ("total", "still_compiled", "gone")} != USER_LEFT:
        raise ValueError(f"F10: the user-written names that left are {ul}, written for {USER_LEFT}")
    ln = d["lean_names"]
    status = collections.Counter(status_of(v) for v in ln.values())
    if dict(status) != NAME_STATUS:
        raise ValueError(f"F10: the blueprint's Lean names are {dict(status)}, written for {NAME_STATUS}")

    def chap(k):
        return g.nodes[k]["_chapter"]

    gt = d["git"]
    c = Canvas(ID, "Between the pins: what changed in the formal proof from the blueprint's commit to the mirror's "
               "head",
               f"The blueprint pins the mirror at {g.mirror_pin}; the posters read `Main.lean` from the mirror at "
               f"{mirror['commit']}, {gt['commits']} commits later. The proof moved in between. This poster "
               "compares the two: everything the five theorems of `Main.lean` depend on at the earlier commit, "
               "from Andrew Sutherland's export, against the same at the later one, from the mirror's build cache, "
               "declaration by declaration, by name. Most of the difference is in names the compiler makes, "
               "which change with the Lean version (4.33 then, 4.37 now) as well as with the proof; the poster "
               "sorts them out, and counts what someone wrote apart. `diagrams/EDGES.md` gives the method. **No "
               "Lean was built**: see diagram R1, band 5."
               + (" **Map mode**: this poster quotes nothing in either form." if bp.MAP else ""),
               W, f"`riemann-blueprint` at {g.bp_commit} (every statement's chapter and `lean` list); "
               "`diagrams/src/lean-drift.json`, from Sutherland's export of the proof at "
               f"{g.mirror_pin} (sha256 {d['proof']['export_sha256'][:12]}…) and the mirror's build cache at "
               f"{d['later']['mirror'][:10]} (receipt sha256 {d['later']['receipt_sha256'][:12]}…), with the "
               "mirror's git history between them; `leanprover-community/riemann-hypothesis` at "
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
        "**A closure** is every declaration of the project that the five theorems of `Main.lean` depend on, "
        "through types and proofs. The earlier one is read from the export, the later from the build cache "
        "closed from the same five theorems; library declarations (Mathlib, core) are left out of both.",
        "**Left** means in the earlier closure and not the later; **joined**, the reverse; **stayed**, in both. "
        "A declaration renamed counts as one that left and one that joined: names are all the comparison sees.",
        "**User-written** names are the ones someone typed. **Auxiliary** names are made by the compiler "
        "(`_proof_1`, `match_2`), and **private** names carry their module's path. Both change when the compiler "
        "or a file's place changes, with no change to the mathematics.",
    ]
    nums = [
        f"**{gt['commits']} commits** between the pins, from {gt['earlier_date'][:10]} to "
        f"{gt['later_date'][:10]}. `git diff --no-renames` counts {gt['diff_src'].split(',')[0]} under `src/`, "
        "moves included.",
        f"**The closures**: {fmt(d['closures']['earlier'])} declarations then, {fmt(d['closures']['later'])} "
        "now.",
        f"**User-written names** that left: {fmt(ul['total'])}, of which {fmt(ul['still_compiled'])} the later "
        f"tree still compiles but no longer uses, and {fmt(ul['gone'])} it no longer has. Joined: "
        f"{fmt(uj['total'])}.",
        f"**The blueprint's {len(ln):,} Lean names**: " + ", ".join(f"{n:,} {s}" for s, n in
                                                                  sorted(status.items(), key=lambda t: -t[1])) + ".",
    ]
    hk = max(c.card(0, 0, span(3), "How to read the poster", key, draw=False, size=S),
             c.card(0, 0, span(2), "The drift in numbers", nums, draw=False, size=S))
    c.card(colx(0), y, span(3), "How to read the poster", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(3), y, span(2), "The drift in numbers", nums, "teal", h=hk, size=S, tint=False)
    y += hk + 50

    # ---------------------------------------------------------------------------------- by kind
    y = band(c, X0, y, "2 · The two closures, by kind of name",
             "Left, joined and stayed, for each kind of name. The compiler's names account for almost all of the "
             "movement: auxiliaries left in about the numbers private names joined.")
    kw = WW * 0.55
    kcols = [("Kind", 260), ("Left", (kw - 260) / 4), ("Joined", (kw - 260) / 4), ("Stayed", (kw - 260) / 4),
             ("Share that stayed", (kw - 260) / 4)]
    krows = []
    for k in KINDS:
        before = bk["left"][k] + bk["stayed"][k]
        krows.append([f"**{KIND_WORD[k]}**", fmt(bk["left"][k]), fmt(bk["joined"][k]), fmt(bk["stayed"][k]),
                      f"{bk['stayed'][k] * 100 // before}%" if before else "—"])
    tot = {s: sum(bk[s].values()) for s in ("left", "joined", "stayed")}
    krows.append(["**All**", fmt(tot["left"]), fmt(tot["joined"]), fmt(tot["stayed"]),
                  f"{tot['stayed'] * 100 // (tot['left'] + tot['stayed'])}%"])
    kh = c.table(X0, y, kcols, krows, size=S)
    nx = X0 + kw + G
    note = [f"Of the {fmt(bk['left']['user'] + bk['stayed']['user'])} user-written names in the earlier closure, "
            f"{fmt(bk['stayed']['user'])} are in the later one.",
            f"Of the {fmt(ul['total'])} that left, {fmt(ul['still_compiled'])} are still compiled at the later "
            f"commit, so the proof stopped using them; {fmt(ul['gone'])} are gone, deleted or renamed.",
            "Auxiliaries and private names are not compared one to one: the later compiler may give the same "
            "auxiliary a private name, so a count that left on one row can reappear on the next."]
    nh = c.card(nx, y, X1 - nx, "What the counts say", note, "teal", size=S, tint=False)
    y += max(kh, nh) + 50

    # ---------------------------------------------------------------------------------- the blueprint's names
    y = band(c, X0, y, "3 · The blueprint's Lean names in each tree",
             "Every Lean name the blueprint gives a statement, by whether the earlier closure holds it, the later "
             "closure holds it, and the later tree compiles it; a library name (Mathlib's) is not compared, since "
             "the cache holds the project's modules only. All but those in both closures are listed.")
    srows = [[s, fmt(n)] for s, n in sorted(status.items(), key=lambda t: -t[1])]
    sh = c.table(X0, y, [("Status", 380), ("Names", 120)], srows, size=S)
    lx = X0 + 500 + G
    lrows = []
    for n, v in sorted(ln.items(), key=lambda t: (status_of(t[1]), t[1]["statement"], t[0])):
        s = status_of(v)
        if s != "in both closures":
            lrows.append({"cells": [v["statement"], SHORT[chap(v["statement"])], n, s],
                          "accent": "red" if "gone" in s or "neither" in s else "grey" if s == LIBRARY else "amber"})
    lw = X1 - lx
    lh = c.table(lx, y, [("Statement", 520, {"mono": True}), ("Chapter", 160), ("Lean name", lw - 520 - 160 - 380,
                                                                                 {"mono": True}),
                         ("Status", 380)], lrows, size=S)
    y += max(sh, lh) + 50

    # ---------------------------------------------------------------------------------- by namespace
    y = band(c, X0, y, "4 · User-written names that left the closure, and that joined it, by namespace",
             "To the second level of the name, largest first.")
    half = (WW - G) / 2
    lft = sorted(ul["namespaces"].items(), key=lambda t: (-t[1], t[0]))
    jn = sorted(uj["namespaces"].items(), key=lambda t: (-t[1], t[0]))

    def rows(items):
        out = [[k, fmt(v)] for k, v in items[:TOP_N]]
        if len(items) > TOP_N:
            out.append([f"… and {len(items) - TOP_N} more namespaces", fmt(sum(v for _, v in items[TOP_N:]))])
        return out
    ah = c.table(X0, y, [("Left: namespace", half - 160, {"mono": True}), ("Names", 160)], rows(lft), size=S)
    bh = c.table(X0 + half + G, y, [("Joined: namespace", half - 160, {"mono": True}), ("Names", 160)], rows(jn),
                 size=S)
    y += max(ah, bh) + 50

    # ---------------------------------------------------------------------------------- the statements
    st = d["statements"]
    y = band(c, X0, y, "5 · The statements whose Lean lost the most",
             "Left: the statements whose Lean, at the earlier commit, reached the most user-written helpers that "
             "have since left the closure. Right: by chapter, how many statements lost any. A helper reached from "
             "several statements counts under each.")
    tw = WW * 0.62
    trows = []
    for k, v in sorted(st.items(), key=lambda t: (-t[1]["left"], t[0]))[:TOP_N]:
        trows.append([k, SHORT[chap(k)], fmt(v["user_helpers"]), fmt(v["left"]),
                      f"{v['left'] * 100 / v['user_helpers']:.1f}%" if v["user_helpers"] else "—"])
    th = c.table(X0, y, [("Statement", tw - 160 - 200 - 140 - 140, {"mono": True}), ("Chapter", 160),
                         ("Helpers then", 200), ("Left", 140), ("Share", 140)], trows, size=S)
    chapters = sorted(g.chapters, key=lambda ch: (g.nodes[ch].get("order", 0), ch))
    cx = X0 + tw + G
    cw = X1 - cx
    crows = []
    for ch in chapters:
        ks = [k for k in st if chap(k) == ch]
        crows.append([f"**{SHORT[ch]}**", str(len(ks)), str(sum(1 for k in ks if st[k]["left"]))])
    ch_h = c.table(cx, y, [("Chapter", cw - 170 - 210), ("Statements", 170), ("Lost any", 210)], crows, size=S)
    y += max(th, ch_h) + 30
    return c
