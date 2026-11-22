# Diagrams of the Lean proof of the Riemann Hypothesis

Generated SVG posters of the proof, drawn for teaching. They adapt to light and dark, and are meant to be
opened on their own and zoomed.

| Id | Diagram | What it shows |
|----|---------|---------------|
| R1 | [`Main.lean`, theorem by theorem](R1-main-theorems-2026.11.22.svg) | The five theorems of `Main.lean`, the definitions they are stated with, the chain of reductions from `GRH, half-plane form` down to the theorems the chapters prove, and those theorems. Each node is one blueprint statement: the Lean signature from `lean-facts.json`, the statement in words, its proof as bullets, and what it uses and is used by. Arrows are the proof uses between the drawn statements. Also `Main.lean` and `Statements.lean` as the mirror states them, the five stages of the proof, a table of statements by depth, and what has been checked of the formal proof. |
| T1 | [The deepest chain](T1-trace-deepest-2026.11.22.svg) | One chain of eleven statements from a local lattice count, the statement farthest from the main theorems, up to the Riemann Hypothesis, as full cards in reading order: a proof, left to right. |
| T2 | [The chain to Landau's theorem](T2-trace-landau-2026.11.22.svg) | The analytic end of the proof in six steps, from Landau's theorem of 1905 up to the Riemann Hypothesis. |
| R2 | [The proof, chapter by chapter](R2-chapters-2026.11.22.svg) | The nine chapters of the blueprint as cards: the Lean signature of the theorem each one proves, its introduction, its sections with statement counts, and which chapters it uses. Arrows are the chapter `uses` edges. Also the blueprint's own list of points to check first, and the twelve published results the proof cites most. |
| R3 | [The zero-free chapter, lemma by lemma](R3-zero-free-2026.11.22.svg) | All 24 statements of the blueprint's chapter "From prime sums to the zero-free half-plane", the analytic half of the proof, as cards. Solid arrows are the proof uses inside the chapter; two dashed arrows are the hypotheses the chapter theorem takes rather than proves, which the build checks against the proof's text. Also what the chapter uses from outside, and the five section introductions in the chapter's own words. |
| R4 | [Families of definite unitary groups, every statement](R4-families-2026.11.22.svg) | the 44 statements that build the families the zero-free argument runs over. Laid out by `src/chapter.py` from the chapter's own edges: a card sits above the cards whose proofs use it, section heads and the chapter theorem get full cards, the rest short ones. |
| R5 | [Theta lifts, periods and the Siegel–Weil formula, every statement](R5-theta-2026.11.22.svg) | the 61 statements about the theta lifts that join a family's members, the chapter's largest. Laid out by `src/chapter.py` from the chapter's own edges: a card sits above the cards whose proofs use it, section heads and the chapter theorem get full cards, the rest short ones. |
| R6 | [Heights and the covolume bound, every statement](R6-heights-2026.11.22.svg) | the 32 statements of the Arakelov argument that bounds the lattices' covolumes. Laid out by `src/chapter.py` from the chapter's own edges: a card sits above the cards whose proofs use it, section heads and the chapter theorem get full cards, the rest short ones. |
| R7 | [The Tate–Shafarevich bound, every statement](R7-sha-2026.11.22.svg) | the 35 statements from Kato's Euler system to the bound, with three results the main proof names as hypotheses. Laid out by `src/chapter.py` from the chapter's own edges: a card sits above the cards whose proofs use it, section heads and the chapter theorem get full cards, the rest short ones. |
| R8 | [Galois representations, every statement](R8-galois-2026.11.22.svg) | the 38 statements that attach Galois representations to polarized pairs. Laid out by `src/chapter.py` from the chapter's own edges: a card sits above the cards whose proofs use it, section heads and the chapter theorem get full cards, the rest short ones. |
| F3 | [The proof as code](F3-modules-2026.11.22.svg) | The blueprint's nine chapters against the formalisation's modules, read from `lean-facts.json`, the blueprint's index of the 1194 Lean declarations its statements name. A matrix of chapters against the 35 second-level modules, so the paper's organisation and the code's can be compared; the formalisation's own tree as one card per namespace; each chapter's footprint in the code (declarations, kinds, modules, files, lines spanned); and the fan-out from one statement to its declarations, with the twelve statements that name the most. The declaration count, the kinds, the module count, the per-chapter counts and the three statements without a declaration are checked, and the build fails if a declaration is named by two statements. |
| F2 | [What is new](F2-new-2026.11.22.svg) | The proof organised by provenance: the 200 statements the blueprint marks new in Alpöge's proof. Too many for a card each, so the poster works one level up: each chapter is a card holding only its new work (its sections by provenance, the new statements nothing new builds on, what its new work takes and gives), with arrows between chapters labelled with the number of proof uses between their new statements; a chapter-by-chapter matrix of those counts; every section by provenance, which is where the new work concentrates; the twenty published and modified results the new statements lean on most; and the new lemmas that published results' proofs use. The counts, the chapter pairs and the tops are checked. |
| F1 | [What the stages pass to each other](F1-definitions-2026.11.22.svg) | A different frame: the 24 definitions of the blueprint rather than its theorems. Each is a card with its Lean declaration, the definition in words, and the chapter that makes it; a definition stands above the definitions stated in terms of it, and the 18 arrows are those `uses` edges. The table at the foot counts, for each definition, the statements of each chapter that use it, with the chapter that makes it marked, so the flow of objects between the stages can be read off. The three definitions the outline names as the interfaces between stages are checked and set out in the outline's own words. |

## Map mode

`diagrams/map/` holds the same thirteen posters built with `--map`: nothing of the blueprint's text and nothing of the
formal proof's source is quoted. Each card keeps the statement's title, id, kind, provenance, Lean name and file
location, every edge, and a count of the paragraphs the blueprint spends on it; the section and chapter cards
keep their titles and counts. The map set is the form that can be published while the quoting question in
`PLAN.md` is open, and it is a third to a half the height of the reader set. The build and the checks are the
same; only the quotations are left out, and a map poster says so in its subtitle and its brand line.

## Where the content comes from

The diagrams are a second reading of the blueprint, and the generator is strict about it. At build time it reads
the [riemann-blueprint](../../riemann-blueprint/) (every drawn statement's front matter, body and proof, the
chapter and section files, and `lean-facts.json`) and the
[mirror](../../leanprover-community/riemann-hypothesis/) (`src/Main.lean`, `src/Statements.lean`,
`comparator.json`), and fails if:

- the blueprint checkout is at another commit than the one the diagrams were written against (`BP_COMMIT` in
  `src/bp.py`), pins the mirror at another commit (`MIRROR_PIN`), or the mirror checkout is at another commit
  than `MIRROR_COMMIT`;
- the proof uses between the drawn statements (R1, R3 to R8), the `uses` between chapters (R2), the `uses`
  between definitions (F1), the proof uses between the new statements of different chapters and the tops of the
  new work (F2), the declaration, kind, module and per-chapter counts of `lean-facts.json` (F3), or the chain
  (T1, T2) are not exactly the arrows or the path listed in the diagram's `EXPECTED`; or the results that proofs name in their text without
  listing them as uses (`HYPOTHESES`, R3 to R8) are not the ones recorded;
- a theorem of `Main.lean` is carried by no drawn node, or `comparator.json` names other theorems;
- a drawn Lean declaration has no signature in `lean-facts.json`;
- the theorem drawn for a chapter is not the first result at that chapter's root;
- a title or a signature does not fit its card, or two texts overlap.

Signatures, file lines, uses, used-by, statement counts, depths and citation counts are computed. The italic line
of a node is the blueprint's own statement and the bullets are its proof, abridged where marked with an ellipsis,
with links shown as ids and LaTeX rewritten in plain Unicode. Anything no file states is marked on the diagram as
the diagram's own.

No Lean was built, for the blueprint or for the diagrams. The blueprint's `uses` edges were resolved from the
source text and some are wrong; this is written on both posters.

## Regenerating

```bash
uv run python diagrams/gen-diagrams.py        # all; or: uv run python diagrams/gen-diagrams.py R3
uv run python diagrams/gen-diagrams.py --map  # the map set, into diagrams/map/
```

The generator needs only the standard library, on Python 3.12 or later. The output is deterministic: unchanged
inputs give unchanged bytes, so a diff in an SVG after regenerating means the blueprint or the mirror has moved
under a diagram. Any `WARNING` or `ERROR` line is a failure. After a change, look at the result in both themes.

To move the diagrams to a newer blueprint, bump `BP_COMMIT` (and `MIRROR_PIN` if the blueprint re-pinned the
mirror, and `MIRROR_COMMIT` if `Main.lean` is read from a newer mirror) in `src/bp.py`, regenerate, and fix
whatever the checks report.

The sources are expected as sibling checkouts, `../riemann-blueprint` and `../leanprover-community/riemann-hypothesis`;
`RIEMANN_BLUEPRINT` (the `blueprint/` directory) and `RIEMANN_MIRROR` point elsewhere.

## In CI

`.github/workflows/posters.yml` checks out the blueprint and the mirror at the three pins above, regenerates every
poster in both forms with Python 3.12, and fails if the generator prints a `WARNING` or `ERROR`, if any committed SVG differs
from the regenerated one, or if a poster is regenerated that is not committed. So a pull request that moves a pin
without regenerating fails, and one that regenerates passes. The mirror is checked out sparse, with only the
three files the generator reads.

## Layout

```
gen-diagrams.py              the generator
src/lib.py                   the drawing library: measured and wrapped text, cards, tables, arrows, two themes
src/fonts/, metrics.py       the Noto faces every poster embeds, and their advance widths (see Fonts, below)
src/bp.py                    reads the blueprint, the Lean facts and the mirror; Markdown and LaTeX to rich text;
                             the Lean card; the arrow router
src/d_r1_main_theorems.py    R1
src/d_r2_chapters.py         R2
src/d_r3_zero_free.py        R3, laid out by hand
src/chapter.py               the chapter poster: layout from the chapter's edges, the cards, the bands
src/d_r4_families.py …       R4 to R8: one short module per chapter, holding its EXPECTED edges and HYPOTHESES
src/trace.py                 the trace poster: one chain from the main theorems to a statement, as cards
src/d_t1_deepest.py, d_t2_landau.py   T1 and T2, each holding the chain it expects
src/d_f1_definitions.py      F1: the definitions, their EXPECTED uses, the INTERFACES, the packing of the grid
src/d_f2_new.py              F2: the new statements by chapter and section; EXPECTED pair counts, TOPS, COUNTS
src/d_f3_modules.py          F3: chapters against Lean modules from lean-facts.json; N_DECLS, KINDS, NO_LEAN, EXPECTED
```

`lib.py` is the drawing library of the TOPAK diagram family (Apache-2.0, same author), with the brand, the date
and the fonts changed. `bp.py` is new here: the source is a blueprint, and the arrows are routed rather than
placed by hand, because a proof graph has many of them.

## Fonts

Every poster carries its fonts: Noto Sans (regular, bold, italic) for the text, Noto Sans Mono (regular, bold)
for code and Lean, and Noto Sans Math for the symbols the other two lack, each subset to about 500 characters
and embedded as WOFF2 in the poster's `<style>`. A poster so looks the same on every machine, opened on its own,
on GitHub Pages or inside an `<img>`, at about 175 KB of base64 per poster. The arrows of code are drawn from
Noto Sans Math too: Noto Sans Mono's are a third of an em tall.

`src/metrics.py` holds the advance width of every character in every face, so text is wrapped and boxed at the
width the browser draws it; kerning and ligatures are left out of the subsets to keep that exact. Measured in
Chromium over all twenty-two posters, no line of 14,965 differs from its computed width by more than 0.7 px.
A character outside the subsets is a WARNING, which fails the posters check, rather than a silent fallback to a
system font.

`tools/build-fonts.py` writes `src/fonts/*.woff2` and `src/metrics.py` from the Noto sources in google/fonts,
pinned by commit and SHA-256 in the script. It needs fontTools and Brotli; the generator does not, since it only
base64-encodes the committed files. Run it to add characters (its `WANT`) or change a face, then regenerate the
posters:

```
uv run --with fonttools==4.68.0 --with brotli==1.2.0 python tools/build-fonts.py SRC_DIR
```

The fonts are under the SIL Open Font License 1.1, Copyright 2022 The Noto Project Authors
(`src/fonts/OFL.txt`); each WOFF2 file keeps that notice in its name table.
