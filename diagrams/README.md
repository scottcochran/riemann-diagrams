# Diagrams of the Lean proof of the Riemann Hypothesis

Generated SVG posters of the proof, drawn for teaching. They adapt to light and dark, and are meant to be
opened on their own and zoomed.

| Id | Diagram | What it shows |
|----|---------|---------------|
| R1 | [`Main.lean`, theorem by theorem](R1-main-theorems-2026.11.22.svg) | The five theorems of `Main.lean`, the definitions they are stated with, the chain of reductions from `GRH, half-plane form` down to the theorems the chapters prove, and those theorems. Each node is one blueprint statement: the Lean signature from `lean-facts.json`, the statement in words, its proof as bullets, and what it uses and is used by. Arrows are the proof uses between the drawn statements. Also `Main.lean` and `Statements.lean` as the mirror states them, the five stages of the proof, a table of statements by depth, and what has been checked of the formal proof. |
| R2 | [The proof, chapter by chapter](R2-chapters-2026.11.22.svg) | The nine chapters of the blueprint as cards: the Lean signature of the theorem each one proves, its introduction, its sections with statement counts, and which chapters it uses. Arrows are the chapter `uses` edges. Also the blueprint's own list of points to check first, and the twelve published results the proof cites most. |
| R3 | [The zero-free chapter, lemma by lemma](R3-zero-free-2026.11.22.svg) | All 24 statements of the blueprint's chapter "From prime sums to the zero-free half-plane", the analytic half of the proof, as cards. Solid arrows are the proof uses inside the chapter; two dashed arrows are the hypotheses the chapter theorem takes rather than proves, which the build checks against the proof's text. Also what the chapter uses from outside, and the five section introductions in the chapter's own words. |
| R4 | [Families of definite unitary groups, every statement](R4-families-2026.11.22.svg) | the 44 statements that build the families the zero-free argument runs over. Laid out by `src/chapter.py` from the chapter's own edges: a card sits above the cards whose proofs use it, section heads and the chapter theorem get full cards, the rest short ones. |
| R5 | [Theta lifts, periods and the Siegel–Weil formula, every statement](R5-theta-2026.11.22.svg) | the 61 statements about the theta lifts that join a family's members, the chapter's largest. Laid out by `src/chapter.py` from the chapter's own edges: a card sits above the cards whose proofs use it, section heads and the chapter theorem get full cards, the rest short ones. |
| R6 | [Heights and the covolume bound, every statement](R6-heights-2026.11.22.svg) | the 32 statements of the Arakelov argument that bounds the lattices' covolumes. Laid out by `src/chapter.py` from the chapter's own edges: a card sits above the cards whose proofs use it, section heads and the chapter theorem get full cards, the rest short ones. |
| R7 | [The Tate–Shafarevich bound, every statement](R7-sha-2026.11.22.svg) | the 35 statements from Kato's Euler system to the bound, with three results the main proof names as hypotheses. Laid out by `src/chapter.py` from the chapter's own edges: a card sits above the cards whose proofs use it, section heads and the chapter theorem get full cards, the rest short ones. |
| R8 | [Galois representations, every statement](R8-galois-2026.11.22.svg) | the 38 statements that attach Galois representations to polarized pairs. Laid out by `src/chapter.py` from the chapter's own edges: a card sits above the cards whose proofs use it, section heads and the chapter theorem get full cards, the rest short ones. |

## Where the content comes from

The diagrams are a second reading of the blueprint, and the generator is strict about it. At build time it reads
the [riemann-blueprint](../../riemann-blueprint/) (every drawn statement's front matter, body and proof, the
chapter and section files, and `lean-facts.json`) and the
[mirror](../../leanprover-community/riemann-hypothesis/) (`src/Main.lean`, `src/Statements.lean`,
`comparator.json`), and fails if:

- the blueprint checkout is at another commit than the one the diagrams were written against (`BP_COMMIT` in
  `src/bp.py`), or pins the mirror at another commit;
- the proof uses between the drawn statements (R1, R3 to R8), or the `uses` between chapters (R2), are not
  exactly the arrows listed in the diagram's `EXPECTED`; or the results that proofs name in their text without
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
```

The generator needs only the standard library, on Python 3.12 or later. The output is deterministic: unchanged
inputs give unchanged bytes, so a diff in an SVG after regenerating means the blueprint or the mirror has moved
under a diagram. Any `WARNING` or `ERROR` line is a failure. After a change, look at the result in both themes.

To move the diagrams to a newer blueprint, bump `BP_COMMIT` (and `MIRROR_PIN` if the blueprint re-pinned the
mirror) in `src/bp.py`, regenerate, and fix whatever the checks report.

## Layout

```
gen-diagrams.py              the generator
src/lib.py, metrics.py       the drawing library: measured and wrapped text, cards, tables, arrows, two themes
src/bp.py                    reads the blueprint, the Lean facts and the mirror; Markdown and LaTeX to rich text;
                             the Lean card; the arrow router
src/d_r1_main_theorems.py    R1
src/d_r2_chapters.py         R2
src/d_r3_zero_free.py        R3, laid out by hand
src/chapter.py               the chapter poster: layout from the chapter's edges, the cards, the bands
src/d_r4_families.py …       R4 to R8: one short module per chapter, holding its EXPECTED edges and HYPOTHESES
```

`lib.py` and `metrics.py` are the drawing library of the TOPAK diagram family (Apache-2.0, same author), with
the brand and date changed. `bp.py` is new here: the source is a blueprint, and the arrows are routed rather than
placed by hand, because a proof graph has many of them.
