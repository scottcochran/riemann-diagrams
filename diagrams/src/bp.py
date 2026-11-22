"""Reading the blueprint, the Lean facts and the mirror at build time, and drawing a Lean node.

Everything a diagram says about a statement is derived here from the files, strictly: a blueprint checkout at
another commit than the one the diagrams were written against, a Lean name without a signature in lean-facts.json,
a Main.lean theorem that no drawn node carries, or a title that does not fit its card raises, so the generator prints
ERROR instead of drawing something stale.

  load()                     the blueprint as a graph (blueprint_graph.Graph), after the commit checks
  read_mirror()              the five theorems of Main.lean and the Prop definitions of Statements.lean
  body(g, id) / proof(g, id) the Markdown of a statement and of its proof
  rich(md)                   blueprint Markdown to the drawing library's rich text, LaTeX simplified to Unicode
  lean_block(sig, cols)      a Lean signature wrapped to a column count, for the formula panel
  node(canvas, ...)          a card: title, pill, Lean panel, the statement in italics, the proof as bullets, footer
  arrows(canvas, ...)        the arrows between cards, routed through the lanes and gutters of a grid
"""
import json
import os
import pathlib
import re
import subprocess
import sys
from xml.sax.saxutils import escape

import lib
from lib import MONO, MONO_EM, fill, fs, render_line, wrap

ROOT = pathlib.Path(__file__).resolve().parents[2]          # riemann-diagrams
sys.path.insert(0, str(ROOT / "graphs"))
from blueprint_graph import Graph, default_blueprint_dir, MAIN_LEAN_THEOREMS  # noqa: E402

BLUEPRINT = pathlib.Path(default_blueprint_dir())
MIRROR = pathlib.Path(os.environ.get("RIEMANN_MIRROR") or ROOT.parent / "leanprover-community" / "riemann-hypothesis")

# The state the diagrams were written against: the blueprint's commit, the mirror commit it pins in its lakefile,
# and the mirror commit Main.lean and Statements.lean are read from. The build fails if a checkout is at another
# commit; bump these after reading what changed. CI checks the sources out at exactly these (.github/workflows).
BP_COMMIT = "137d976"
MIRROR_PIN = "8c90877c"
MIRROR_COMMIT = "2dea990069"

# Map mode: no text of the blueprint and no Lean source is quoted. Each card keeps the statement's title, id,
# kind, provenance, Lean name and location, and every edge. Set by gen-diagrams.py --map, before the modules load.
MAP = os.environ.get("RIEMANN_MAP") == "1"
NOT_QUOTED = ("Not quoted in map mode: the blueprint's text and the proof's source stay their authors'. The "
              "blueprint link below has both.")


MAP_KEY = [
    "**Title and pill.** The title is the blueprint's; the pill gives the kind and the provenance: **new** in "
    "Alpöge's proof, **modified** from a published result, or **published** as it stands. `Main.lean` marks the "
    "theorems the Comparator config names.",
    "**The line in italics** gives the statement's id and how many paragraphs the blueprint spends on its "
    "statement and its proof. The text itself is not quoted: it is the blueprint's authors', and the blueprint "
    "link in the footer has it. The Lean signature is not quoted either, for the same reason; the footer gives "
    "the declaration's name, file and line in the mirror.",
    "**Stated with**, **Proof uses** and **Used by** are the blueprint's edges, in full. **An arrow from A to B**: "
    "the proof of B uses A, and the arrow takes A's colour.",
]


def prose(s):
    """A quotation of the blueprint, or None in map mode."""
    return None if MAP else s


PROV_ACCENT = {"new": "green", "modified": "amber", "published": "blue", None: "grey"}
PROV_LABEL = {"new": "new in Alpöge's proof", "modified": "modified from the literature", "published": "published",
              None: "unlabelled"}
PROV_SHORT = {"new": "new", "modified": "modified", "published": "published", None: "unlabelled"}
RESULTS = ("theorem", "proposition", "lemma", "corollary")


# ------------------------------------------------------------------------------------------------ reading
def git_at(path, pin, what):
    """The commit of a checkout, ten characters, checked against `pin`; a dirty tree gets a trailing +. A fixed
    length, not git's --short, so that two checkouts with different object counts print the same."""
    out = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True)
    if out.returncode:
        raise ValueError(f"{path}: not a git checkout")
    full = out.stdout.strip()
    if not full.startswith(pin):
        raise ValueError(f"{what} is at {full[:10]}, the diagrams were written against {pin}")
    dirty = subprocess.run(["git", "-C", str(path), "status", "--porcelain"], capture_output=True, text=True).stdout
    return full[:10] + ("+" if dirty.strip() else "")


def load():
    if not BLUEPRINT.is_dir():
        raise ValueError(f"no blueprint at {BLUEPRINT}; set RIEMANN_BLUEPRINT")
    rev = git_at(BLUEPRINT.parent, BP_COMMIT, "the blueprint")
    lake = (BLUEPRINT.parent / "lakefile.toml").read_text(encoding="utf-8")
    pin = re.search(r'name = "tree"\ngit = ".*?riemann-hypothesis"\nrev = "(\w+)"', lake)
    if not pin or not pin.group(1).startswith(MIRROR_PIN):
        raise ValueError(f"the blueprint pins the mirror at {pin and pin.group(1)}, the diagrams expect {MIRROR_PIN}")
    g = Graph(str(BLUEPRINT))
    if not g.lean_facts:
        raise ValueError("no lean-facts.json beside the blueprint: no Lean signatures to draw")
    g.bp_commit, g.mirror_pin = rev, MIRROR_PIN
    return g


def read_mirror():
    """The theorems of Main.lean and the Prop definitions of Statements.lean, checked against comparator.json."""
    main = (MIRROR / "src" / "Main.lean").read_text(encoding="utf-8").splitlines()
    theorems = []
    for i, l in enumerate(main):
        m = re.match(r"theorem (\w+) : ([\w.]+) := (.+)$", l)
        if m:
            theorems.append({"name": m.group(1), "prop": m.group(2), "proof": m.group(3), "line": i + 1, "src": l})
        elif l.strip() and not l.startswith("import"):
            raise ValueError(f"Main.lean:{i + 1}: cannot parse {l!r}")
    stmts = (MIRROR / "src" / "Statements.lean").read_text(encoding="utf-8").splitlines()
    props, cur = {}, None
    for i, l in enumerate(stmts):
        m = re.match(r"def (\w+) : Prop :=", l)
        if m:
            cur = m.group(1)
            props[cur] = {"lines": [l], "line": i + 1}
        elif cur and l.strip():
            props[cur]["lines"].append(l)
        else:
            cur = None
    cfg = json.loads((MIRROR / "comparator.json").read_text(encoding="utf-8"))
    if cfg["theorem_names"] != [t["name"] for t in theorems]:
        raise ValueError("comparator.json does not name the theorems of Main.lean in order")
    for t in theorems:
        if t["prop"] not in props and t["prop"] != "RiemannHypothesis":
            raise ValueError(f"Main.lean: {t['name']} is stated with {t['prop']}, which Statements.lean does not define")
    if set(theorems[i]["name"] for i in range(len(theorems))) != set(MAIN_LEAN_THEOREMS):
        raise ValueError("Main.lean's theorems are not the ones blueprint_graph.MAIN_LEAN_THEOREMS maps to nodes")
    return {"theorems": theorems, "props": props, "axioms": cfg["permitted_axioms"],
            "commit": git_at(MIRROR, MIRROR_COMMIT, "the mirror")}


def _text_after_front_matter(path):
    text = path.read_text(encoding="utf-8")
    return text.split("+++", 2)[2].strip()


def body(g, oid):
    return _text_after_front_matter(BLUEPRINT / g.nodes[oid]["_path"])


def proof(g, oid):
    """The proof's Markdown, or None when the blueprint has no proof file for the statement."""
    p = BLUEPRINT / g.nodes[oid]["_path"]
    p = p.parent.with_suffix(".proof.md") if p.name == "_section.md" else p.with_suffix(".proof.md")
    return _text_after_front_matter(p) if p.exists() else None


# ------------------------------------------------------------------------------------------------ Markdown to rich text
_MACROS = [
    (r"\\tfrac\s*(\d)(\d)", r"\1/\2"), (r"\\[td]?frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)"),
    (r"\\(?:mathrm|operatorname|text|mathbb|mathcal|mathbf|widehat|overline|bar|hat)\{([^{}]*)\}", r"\1"),
    (r"\\big[lr]?|\\Big[lr]?|\\left|\\right|\\,|\;|\\!|\\quad|\\qquad|\\ ", " "),
    (r"\\Re\b", "Re"), (r"\\Im\b", "Im"), (r"\\log\b", "log"), (r"\\cos\b", "cos"), (r"\\sin\b", "sin"),
    (r"\\exp\b", "exp"), (r"\\deg\b", "deg"), (r"\\det\b", "det"), (r"\\dim\b", "dim"), (r"\\min\b", "min"),
    (r"\\max\b", "max"), (r"\\rec\b", "rec"), (r"\\Res\b", "Res"), (r"\\Gal\b", "Gal"), (r"\\GL\b", "GL"),
    (r"\\U\b", "U"), (r"\\bmod\b", "mod"), (r"\\pmod\b", "mod"), (r"\\le\b", "≤"), (r"\\leq\b", "≤"),
    (r"\\ge\b", "≥"), (r"\\geq\b", "≥"), (r"\\neq\b", "≠"), (r"\\ne\b", "≠"), (r"\\to\b", "→"),
    (r"\\rightarrow\b", "→"), (r"\\mapsto\b", "↦"), (r"\\times\b", "×"), (r"\\in\b", "∈"), (r"\\notin\b", "∉"),
    (r"\\subset\b", "⊂"), (r"\\subseteq\b", "⊆"), (r"\\cup\b", "∪"), (r"\\cap\b", "∩"), (r"\\sum\b", "Σ"),
    (r"\\prod\b", "Π"), (r"\\int\b", "∫"), (r"\\infty\b", "∞"), (r"\\equiv\b", "≡"), (r"\\pm\b", "±"),
    (r"\\asymp\b", "≍"), (r"\\ll\b", "≪"), (r"\\gg\b", "≫"), (r"\\sim\b", "~"), (r"\\cdot\b", "·"),
    (r"\\cdots\b", "⋯"), (r"\\dots\b", "…"), (r"\\ldots\b", "…"), (r"\\lfloor\b", "⌊"), (r"\\rfloor\b", "⌋"),
    (r"\\langle\b", "⟨"), (r"\\rangle\b", "⟩"), (r"\\mid\b", "|"), (r"\\forall\b", "∀"), (r"\\exists\b", "∃"),
    (r"\\circ\b", "∘"), (r"\\otimes\b", "⊗"), (r"\\oplus\b", "⊕"), (r"\\partial\b", "∂"), (r"\\nabla\b", "∇"),
    (r"\\Q\b", "ℚ"), (r"\\Z\b", "ℤ"), (r"\\C\b", "ℂ"), (r"\\R\b", "ℝ"), (r"\\N\b", "ℕ"), (r"\\A\b", "𝔸"),
    (r"\\Qp\b", "ℚ_p"), (r"\\Ql\b", "ℚ_l"), (r"\\Qlbar\b", "ℚ̄_l"), (r"\\Qbar\b", "ℚ̄"), (r"\\Fq\b", "𝔽_q"),
    (r"\\alpha\b", "α"), (r"\\beta\b", "β"), (r"\\gamma\b", "γ"), (r"\\Gamma\b", "Γ"), (r"\\delta\b", "δ"),
    (r"\\Delta\b", "Δ"), (r"\\varepsilon\b", "ε"), (r"\\epsilon\b", "ε"), (r"\\zeta\b", "ζ"), (r"\\eta\b", "η"),
    (r"\\theta\b", "θ"), (r"\\Theta\b", "Θ"), (r"\\iota\b", "ι"), (r"\\kappa\b", "κ"), (r"\\lambda\b", "λ"),
    (r"\\Lambda\b", "Λ"), (r"\\mu\b", "μ"), (r"\\nu\b", "ν"), (r"\\xi\b", "ξ"), (r"\\pi\b", "π"), (r"\\Pi\b", "Π"),
    (r"\\rho\b", "ρ"), (r"\\sigma\b", "σ"), (r"\\Sigma\b", "Σ"), (r"\\tau\b", "τ"), (r"\\phi\b", "φ"),
    (r"\\varphi\b", "φ"), (r"\\Phi\b", "Φ"), (r"\\chi\b", "χ"), (r"\\psi\b", "ψ"), (r"\\Psi\b", "Ψ"),
    (r"\\omega\b", "ω"), (r"\\Omega\b", "Ω"), (r"\\ell\b", "ℓ"), (r"\\hbar\b", "ħ"),
]


def latex(s):
    """A LaTeX run as readable Unicode. Not typesetting: enough to read the statement off a poster."""
    s = s.replace("\\\\", " ")
    s = s.replace("\\#", "#").replace("\\{", "\x03").replace("\\}", "\x04")   # escaped braces survive the strip
    for pat, rep in _MACROS:
        s = re.sub(pat, rep, s)
    s = re.sub(r"[\^_]\{([^{}]*)\}", lambda m: ("^" if m.group(0)[0] == "^" else "_") + (
        m.group(1) if len(m.group(1)) <= 1 else "(" + m.group(1) + ")"), s)
    s = re.sub(r"\\([A-Za-z]+)", r"\1", s)          # an unknown macro keeps its name
    s = s.replace("{", "").replace("}", "").replace("\x03", "{").replace("\x04", "}")
    return " ".join(s.split())


def rich(md, join=" "):
    """Blueprint Markdown (one paragraph) to rich text: links as code, maths as code, emphasis dropped."""
    s = " ".join(md.split())
    s = re.sub(r"\$\$(.+?)\$\$", lambda m: " `" + latex(m.group(1)) + "` ", s)
    s = re.sub(r"\$(.+?)\$", lambda m: "`" + latex(m.group(1)) + "`", s)
    s = re.sub(r"\[([A-Za-z0-9][\w-]*)\]", r"`\1`", s)
    s = re.sub(r"(?<![*\w])\*(?!\*)([^*]+?)\*(?!\*)", r"\1", s)
    s = re.sub(r"``+", "`", s)
    s = re.sub(r"` +`", " ", s)
    return " ".join(s.split())


def paragraphs(md):
    """Paragraphs of a Markdown body; a numbered or bulleted item is a paragraph of its own."""
    out = []
    for block in re.split(r"\n\s*\n", md.strip()):
        for item in re.split(r"\n(?=\s*(?:\d+\.|[-*])\s)", block):
            item = re.sub(r"^\s*(?:\d+\.|[-*])\s+", "", item.strip())
            if item:
                out.append(item)
    return out


def abridge(s, limit):
    """Cut rich text at a sentence end under `limit` characters, never inside a code run."""
    if len(s) <= limit:
        return s
    cut = max(s.rfind(". ", 0, limit), s.rfind("; ", 0, limit))
    cut = cut + 1 if cut > limit // 3 else s.rfind(" ", 0, limit)
    head = s[:cut]
    if head.count("`") % 2:
        head = head[:head.rfind("`")].rstrip()
    return head.rstrip(" ,;:") + " …"


# ------------------------------------------------------------------------------------------------ Lean
def lean_block(sig, cols, max_lines=9):
    """A Lean signature as formula lines (indent, text, is_comment), wrapped at `cols` characters. A wrapped line
    continues four columns in from the line it came from."""
    out = []
    for src in sig.splitlines():
        src = src.rstrip()
        if not src:
            continue
        ind = len(src) - len(src.lstrip(" "))
        line, cur, cont = [], ind, ind
        words = []
        for w in src.strip().split(" "):          # an identifier longer than the panel is broken where it must be
            while len(w) > cols - ind - 4:
                words.append(w[:cols - ind - 4])
                w = w[cols - ind - 4:]
            words.append(w)
        for w in words:
            if line and cur + 1 + len(w) > cols:
                out.append((cont, " ".join(line), False))
                cont = ind + 4
                line, cur = [w], cont + len(w)
            else:
                cur += (1 if line else 0) + len(w)
                line.append(w)
        out.append((cont, " ".join(line), False))
    if len(out) > max_lines:
        rest = len(out) - (max_lines - 1)
        out = out[:max_lines - 1] + [(out[max_lines - 1][0], f"… {rest} more lines", True)]
    return out


def lean_lines(lines, cols, max_lines=12):
    return lean_block("\n".join(lines), cols, max_lines)


def columns(w, pad=16, fpad=11, fsize=13.5):
    """How many monospace characters fit the formula panel of a card of width w."""
    return int((w - 2 * pad - 2 * fpad) / (MONO_EM * fsize))


# ------------------------------------------------------------------------------------------------ drawing
def mono_width(s, size):
    return len(s) * MONO_EM * size


def mono_line(x, y, s, size, color="ink", bold=False, italic=False):
    """A line of code-font text. Registers itself for the overlap check."""
    lib.TEXT_BOXES.append((x, y - size * 0.75, x + mono_width(s, size), y + size * 0.2, s))
    b = ' font-weight="bold"' if bold else ""
    it = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="{size}"{b}{it} '
            f'xml:space="preserve" {fill(color)}>{escape(s)}</text>')


def formula_width(formula, size):
    return max(mono_width(" " * ind + t, size) for ind, t, _ in formula) if formula else 0


def node(c, x, y, w, name, accent, formula, pill=None, say=None, bullets=(), foot=(), h=None, draw=True,
         size=13.5, fsize=13.5, tsize=17, pad=16, dash=None, title_mono=False):
    """A card. formula: lean_block() output. say: a rich string set in italics. bullets and foot: rich strings.
    Returns the height; draw=False measures only."""
    inner = w - 2 * pad
    lead, flead, fpad = round(size * 1.42, 1), round(fsize * 1.5, 1), 11
    pw = lib.text_width(pill, 11.5, bold=True) + 18 + 12 if pill else 0
    while True:                 # a long title is set smaller, down to 15 px, then wrapped to two lines, then fails
        if title_mono:
            tlines = [[(name, "b", None)]]
            tw = mono_width(name, tsize) + pw
        else:
            tlines = wrap(name, inner - pw, tsize, bold=True)
            tw = max(lib.line_width(ln, tsize) for ln in tlines) + pw
        if tw <= inner + 0.5 and len(tlines) <= 2:
            break
        if tsize <= 15:
            raise ValueError(f"node {name}: the title needs {tw:.0f} px or {len(tlines)} lines, the card has {inner:.0f}")
        tsize -= 1
    theight = tsize + (tsize + 4) * (len(tlines) - 1)
    need = formula_width(formula, fsize) + 2 * fpad
    if need > inner + 0.5:
        raise ValueError(f"node {name}: formula needs {need:.0f} px, the card has {inner:.0f}")
    say_lines = wrap(say, inner - 4, size) if say else []
    blines = [wrap(b, inner - lib.width("•  ", size), size) for b in bullets]
    flines = [wrap(f, inner, size - 1) for f in foot]
    panel_h = len(formula) * flead + 2 * fpad - 5 if formula else 0
    hh = pad + theight + 12 + (panel_h + 12 if formula else 0)
    if say_lines:
        hh += len(say_lines) * lead + 8
    for ls in blines:
        hh += len(ls) * lead + 3
    if flines:
        hh += 10 + sum(len(ls) * round((size - 1) * 1.42, 1) + 2 for ls in flines)
    hh += pad - 6
    if h is not None:
        hh = max(h, hh)
    if not draw:
        return hh
    c.blocks.append((x, y, x + w, y + hh, "node " + name))
    c.rect(x, y, w, hh, accent, dash=dash)
    if title_mono:
        c.add(mono_line(x + pad, y + pad + tsize - 3, name, tsize, accent, bold=True))
    else:
        for i, ln in enumerate(tlines):
            c.add(render_line(x + pad, y + pad + tsize - 3 + i * (tsize + 4), ln, tsize, accent, bold=True))
    if pill:
        c.pill(x + w - pad, y + pad - 3, pill, accent, 11.5, anchor="end", solid=True)
    cy = y + pad + theight + 12
    if formula:
        c.add(f'<rect x="{x + pad:.1f}" y="{cy:.1f}" width="{inner:.1f}" height="{panel_h:.1f}" rx="6" '
              f'{fs("bg", "line")} stroke-width="1"/>')
        for i, (ind, t, is_comment) in enumerate(formula):
            ly = cy + fpad + fsize - 1 + i * flead
            lx = x + pad + fpad + ind * MONO_EM * fsize
            c.add(mono_line(lx, ly, t, fsize, "faint" if is_comment else "ink", italic=is_comment))
        cy += panel_h + 12
    if say_lines:
        for ln in say_lines:
            c.add(render_line(x + pad + 2, cy + size - 1, ln, size, "muted").replace(
                "<text ", '<text font-style="italic" ', 1))
            cy += lead
        cy += 8
    for ls in blines:
        for i, ln in enumerate(ls):
            if i == 0:
                c.add(render_line(x + pad, cy + size - 1, [("•", "b", None)], size, accent))
            c.add(render_line(x + pad + lib.width("•  ", size), cy + size - 1, ln, size, "ink"))
            cy += lead
        cy += 3
    if flines:
        fy = y + hh - pad + 6 - sum(len(ls) * round((size - 1) * 1.42, 1) + 2 for ls in flines)
        c.line(x + pad, fy - 6, x + w - pad, fy - 6, "line", sw=1)
        for ls in flines:
            for ln in ls:
                c.add(render_line(x + pad, fy + size - 2, ln, size - 1, "muted"))
                fy += round((size - 1) * 1.42, 1)
            fy += 2
    return hh


def statement_card(g, k, w, drawn, rev, depth, main_names, diagram="R1", max_lines=9, compact=False):
    """The card for one blueprint statement: the Lean panel, the statement in italics, the proof as bullets, and
    the Stated with / Proof uses / Used by / Lean / Blueprint footer. `drawn` says which proof uses have a card."""
    n = g.nodes[k]
    prov = n.get("provenance")
    lean = n.get("lean", [])
    if not lean and n["kind"] != "remark" and not compact and diagram in ("R1", "R3"):
        raise ValueError(f"{diagram}: {k} has no Lean declaration to draw")
    if lean:
        first = lean[0]
        fact = g.lean_facts.get(first)
        if not fact or not fact.get("signature"):
            raise ValueError(f"{diagram}: lean-facts.json has no signature for {first}")
        formula = [] if MAP else lean_block(fact["signature"], columns(w), 4 if compact else max_lines)
    else:
        formula = [(0, "no Lean declaration: the blueprint's own grouping of results", True)]
    is_main = any(x in main_names for x in lean)
    pill = ("Main.lean · " if is_main else "") + f"{n['kind']} · {PROV_SHORT[prov]}"
    pf = proof(g, k)
    if MAP:
        paras = paragraphs(pf) if pf is not None else []
        say = (f"`{k}`: the blueprint states it in {len(paragraphs(body(g, k)))} paragraph(s)"
               + (f" and proves it in {len(paras)}." if pf is not None else "; it gives no proof."))
        bullets = []
    else:
        say = abridge(rich(" ".join(paragraphs(body(g, k))[:2])), 360 if compact else 620)
        bullets = []
        if pf is not None:
            paras = paragraphs(pf)
            keep = 1 if compact else 4
            for p in paras[:keep]:
                bullets.append(abridge(rich(p), 240 if compact else 330))
            if len(paras) > keep:
                bullets.append(f"… and {len(paras) - keep} more paragraphs in the blueprint's proof.")
        elif n["kind"] != "definition":
            bullets.append("The blueprint gives no proof for this statement.")
    su, pu, ub = g.statement_uses(k), g.proof_uses(k), rev[k]
    lim = 4 if compact else 10
    foot = []
    if su or not compact:
        foot.append("**Stated with** " + (names(su, lim) if su else "no other statement"))
    if n["kind"] != "definition":
        hidden = [u for u in pu if u not in drawn]
        foot.append("**Proof uses** " + (names(pu, lim) if pu else "nothing the blueprint names")
                    + (f" · {len(hidden)} of these are not drawn here" if hidden else ""))
    foot.append("**Used by** " + (names(ub, lim) if ub else "no other statement: it is one of the five theorems"))
    if lean:
        where = g.lean_location(first)
        more = (f" · and {len(lean) - 1} more: " + names(lean[1:4]) + (" …" if len(lean) > 4 else "")
                if len(lean) > 1 else "")
        foot.append(f"**Lean** {code(first)} at {code(where)}{more}")
    chap = g.nodes[n["_chapter"]]["title"]
    if compact:
        foot.append(f"Blueprint {code(n['_path'], 44)}")
    else:
        foot.append(f"Blueprint {code(n['_path'], 44)} ({chap}) · depth {depth.get(k, '—')} from the main theorems")
    return dict(name=n["title"], accent=PROV_ACCENT[prov], pill=pill,
                formula=formula, say=say, bullets=bullets, foot=foot,
                dash="6 4" if n["kind"] == "definition" else None)


def names(xs, limit=10):
    """Ids as code runs, the first `limit` of them; the rest become a count."""
    xs = list(xs)
    head = ", ".join(code(x) for x in xs[:limit])
    return head + (f" … and {len(xs) - limit} more" if len(xs) > limit else "")


def code(s, limit=34):
    """A code run that the wrapper can break: a path or dotted name longer than `limit` is split at its separators
    into runs of about `limit` characters, so a long Lean name or file path folds instead of overflowing its card."""
    if len(s) <= limit:
        return f"`{s}`"
    parts = re.split(r"(?<=[/.])", s)
    runs, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) > limit:
            runs.append(cur)
            cur = p
        else:
            cur += p
    if cur:
        runs.append(cur)
    return " ".join(f"`{r}`" for r in runs)


# ------------------------------------------------------------------------------------------------ arrows
def arrows(c, pos, rowof, edges, accent, vg, g, x0, x1, ncols, colx, dashed=(), labels=None):
    """Draw every (a, b) of `edges` as an arrow from the bottom (or top) of card a to the top of card b: a is
    drawn above b, or in the same row. Adjacent cards in a row are joined across the gutter; other pairs in a row
    go over the lane above; cards one row apart go through the lane between; farther pairs drop through a free
    gutter, or round a margin. Edges sharing a lane or a gutter are staggered. `labels`: (a, b) -> text set on
    the arrow's lane segment."""
    labels = labels or {}
    rows = {}
    for k, r in rowof.items():
        rows.setdefault(r, []).append(k)
    top = {r: min(pos[k][1] for k in ks) for r, ks in rows.items()}
    bot = {r: max(pos[k][1] + pos[k][3] for k in ks) for r, ks in rows.items()}

    def cx(k):
        return pos[k][0] + pos[k][2] / 2

    outs, ins = {}, {}
    for a, b in edges:
        outs.setdefault(a, []).append(b)
        ins.setdefault(b, []).append(a)

    def spread(k, others):
        srt = sorted(set(others), key=lambda o: (cx(o), o))
        x, _, w, _ = pos[k]
        return {o: x + w * (i + 1) / (len(srt) + 1) for i, o in enumerate(srt)}

    ex = {a: spread(a, bs) for a, bs in outs.items()}
    en = {b: spread(b, as_) for b, as_ in ins.items()}

    gutter_x = [colx(i) - g / 2 for i in range(1, ncols)]

    def gutter_free(gx, r):
        return all(not (pos[k][0] < gx < pos[k][0] + pos[k][2]) for k in rows.get(r, []))

    plans = []                 # (kind, a, b, data)
    lane_use, gutter_use = {}, {}
    for a, b in edges:
        ra, rb = rowof[a], rowof[b]
        if ra > rb:
            raise ValueError(f"arrow {a} -> {b}: {a} is drawn below {b}")
        if ra == rb:
            xa, _, wa, _ = pos[a]
            xb, _, wb, _ = pos[b]
            if abs(xa + wa + g - xb) < 1 or abs(xb + wb + g - xa) < 1:
                plans.append(("across", a, b, None))
            else:
                lane_use.setdefault(ra - 1, []).append((a, b))
                plans.append(("over", a, b, ra - 1))
        elif rb == ra + 1:
            lane_use.setdefault(ra, []).append((a, b))
            plans.append(("down", a, b, ra))
        else:
            free = [gx for gx in gutter_x if all(gutter_free(gx, r) for r in range(ra + 1, rb))]
            free += [x0 - 28, x1 + 28]
            gx = min(free, key=lambda v: abs(v - ex[a][b]))
            lane_use.setdefault(ra, []).append((a, b))
            lane_use.setdefault(rb - 1, []).append((a, b))
            gutter_use.setdefault(gx, []).append((a, b))
            plans.append(("drop", a, b, gx))

    def lane_y(r, a, b):
        es = sorted(lane_use[r], key=lambda e: (ex[e[0]][e[1]], e))
        i, n = es.index((a, b)), len(es)
        if r < 0 or r not in bot:
            base = top[r + 1] - vg
        else:
            base = bot[r]
        return base + vg * (i + 1) / (n + 1)

    def gx_of(gx, a, b):
        es = sorted(gutter_use[gx])
        i, n = es.index((a, b)), len(es)
        return gx + (i - (n - 1) / 2) * min(10, 56 / n)

    for kind, a, b, data in plans:
        acc = "amber" if (a, b) in dashed else accent(a)
        dash = "7 5" if (a, b) in dashed else None
        lab = {"label": labels[(a, b)], "lpos": 0.5} if (a, b) in labels else {}
        xa, ya, wa, ha = pos[a]
        xb, yb, wb, hb = pos[b]
        if kind == "across":
            yy = ya + 100
            pts = [(xa + wa, yy), (xb, yy)] if xa < xb else [(xa, yy), (xb + wb, yy)]
            c.arrow(pts, acc, dash=dash, **lab)
        elif kind == "over":
            ly = lane_y(data, a, b)
            c.arrow([(ex[a][b], ya), (ex[a][b], ly), (en[b][a], ly), (en[b][a], yb)], acc, dash=dash, **lab)
        elif kind == "down":
            ly = lane_y(data, a, b)
            if abs(ex[a][b] - en[b][a]) < 2:
                c.arrow([(ex[a][b], ya + ha), (en[b][a], yb)], acc, dash=dash, **lab)
            else:
                c.arrow([(ex[a][b], ya + ha), (ex[a][b], ly), (en[b][a], ly), (en[b][a], yb)], acc, dash=dash,
                        **lab)
        else:
            gx = gx_of(data, a, b)
            l1, l2 = lane_y(rowof[a], a, b), lane_y(rowof[b] - 1, a, b)
            c.arrow([(ex[a][b], ya + ha), (ex[a][b], l1), (gx, l1), (gx, l2), (en[b][a], l2), (en[b][a], yb)], acc,
                    dash=dash, **lab)
