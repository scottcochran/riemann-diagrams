# The other sources for a blueprint

Every poster reads its statements, its arrows and its Lean names from the
[riemann-blueprint](https://github.com/chrisflav/riemann-blueprint), and checks the arrows against Sutherland's
export of the formal proof ([EDGES.md](EDGES.md)). This document asks whether another published source would do
better as the blueprint, and says what each one offers. It is derived from the pages named below as they were
read on 2026.11.24, and from the blueprint's history at `BP_COMMIT`. These are young projects that change
daily, so the counts and judgements here are only as good as that reading. Nothing below was built or checked
against the Lean except where it says so.

The short version: none of the six sources replaces the riemann-blueprint. It is the only one with
statement-level prose, Lean names, `uses` edges, a pinned commit and a licence for its text. Two of the others
are worth reading beside it: a dominator tree computed from the kernel export, which checks the blueprint's
choice of nodes, and a human-written account of the proof in a different frame. The blueprint has not moved
since the pin, but its README's count of "461 statements in four chapters" is out of date (section 3).

## 1. What the posters need from a source

The poster set rests on five things. A source that lacks one of them cannot replace the blueprint, though it
may still check it.

1. **Statements a reader can read.** Each card quotes a statement and its proof in mathematical prose.
2. **Lean names for each statement.** A card's foot names its declaration, file and line, and F3, F9 and F10
   need the fan-out from a statement to its declarations.
3. **Explicit `uses` edges between statements.** Every arrow on a poster is one, and the build fails on a drawn
   arrow the source does not make.
4. **A pinned commit of both the source and the Lean it describes.** `bp.py` pins three (`BP_COMMIT`,
   `MIRROR_PIN`, `MIRROR_COMMIT`).
5. **A licence for what is quoted.** The blueprint's prose is CC BY 4.0 by its author's grant ([NOTICE](../NOTICE)).

## 2. The sources

| Source | What it is | Has 1–5 | Against the blueprint |
|---|---|---|---|
| [riemann-blueprint](https://github.com/chrisflav/riemann-blueprint) (the source in use) | 416 statements in nine chapters at `137d976`, one Markdown file each with TOML front matter, plus `lean-facts.json`. Edges resolved from identifiers in the Lean source text, without a build. | all five | — |
| [jae-63/rh-alpoge-blueprint](https://github.com/jae-63/rh-alpoge-blueprint) | A prose `BLUEPRINT.md` with a hand-drawn spine of the top layers, 14 "pillars" of declarations, and a map of the announcement's 20-item timeline to Lean names. Edges from names found in declaration bodies; "Nothing here was compiled." | 1 in part, 2 as text; no edge file committed, no pin | Worse. The same text matching as the blueprint, at coarser grain, against an unpinned clone of a different mirror. Three commits, all of 2026.11.20. |
| [tanclary/riemann-blueprint](https://github.com/tanclary/riemann-blueprint) | A reduction of the formal proof (9.27 million of its 17.37 million lines kept), checked by con-ron against MIT's challenge file, with a 245-line `Blueprint.lean` of 35 "spine" declarations and `data/dom_top300.tsv`: the top 300 nodes of the dominator tree of the kernel export, each with its immediate dominator, depth, size, Lean name, module and lines. | 2 and a tree of 3; no prose, no upstream pin; MIT licence | A check, not a replacement. The blueprint chose its nodes as declarations through which at least 1,000 others are reached only, read from source text; this tree is the same idea computed exactly from the kernel. |
| [Statements of the Lean RH project](https://andrewodesky.com/rh/) | A site of 1,722 Lean theorems, each with "Depends on", "Cites" and "Used by" lists, a share of the proof, and review counts. | 1, 2 and 3 as HTML | Different coverage, not usable as input: no download, and the pages read do not say how the lists were made. |
| [Rubinstein's guide to the proof for ζ](https://www.math.uwaterloo.ca/~mrubinst/alpoge_claude_grh/) | A human account in the style of classical analytic number theory: v1 of 164 pages (2026.11.21), a v2 working draft of 265 pages (2026.11.22), both with LaTeX source. RH follows from a main inequality (M) and two estimates for Dirichlet characters, and (M) is reduced to thirteen numbered hypotheses. | 1; 2 and 3 unknown | A different frame, not a graph. Its architecture is not the blueprint's nine chapters. The PDFs could not be read as text, so this row is from the index page. |
| [The treemap](https://pengowray.github.io/riemann-zeta-proof-visualizer/) | Modules sized by lines, with the module import graph, from the mirror `1337isnot1337/riemann-hypothesis` at `6193bb5`. Its map of the proof's steps is jae-63's. | none | Worse. Imports only: every module but `Main.lean` is imported by another, so the import graph says little about logical dependency. |

The mirror itself, [leanprover-community/riemann-hypothesis](https://github.com/leanprover-community/riemann-hypothesis),
publishes no blueprint and no dependency export. Its `verification/static-scan.txt` counts risky constructs and
carries no edges. `export-targets.txt` with `lake env leanexport` would give the exact references, but needs a
build of many hours; Sutherland's export, which [EDGES.md](EDGES.md) reads, is that output already made.

## 3. The blueprint's README and its tree

The blueprint's README says "461 statements in four chapters". At `BP_COMMIT` the tree holds 416 statements in
nine chapters, which is what the posters draw. The README's head is the pin: the blueprint has no commit after
`137d976`. The figure is not a typo for 416. It was right when the line was written and was not updated through
three later changes:

| Commit | Change | Statements | Chapters |
|---|---|---|---|
| `9dfd606` | the README line is written | 463 (461 without the 2 remarks) | 4 |
| `b6bcc22` | coverage audit adds the missed objects | 487 | 4 |
| `6bc1a9b` | folds nodes that only restated their parent | 429 | 4 |
| `137d976` | reorganises by stage into nine chapters (`BP_COMMIT`) | 416 | 9 |

A statement here is a file whose TOML front matter has `kind` one of theorem, proposition, lemma, corollary,
definition or remark, as `graphs/blueprint_graph.py` counts them; proofs, sections, chapters and the 209
references are not counted. The README also still describes four chapters (main theorems, outline, common
foundations, published results) where the tree has `main-theorems`, `architecture` and seven stage chapters.

The README names a plan that would fix the blueprint's main weakness at the source: run
`lake exe blueprint extract` against built oleans, then `blueprint check --lean`, to confirm or correct the
edges and names and fill in the statuses. If that lands, F7's verdicts become a check of the check, and the pin
bump that follows will be large.

## 4. What follows for this repository

- **Keep the riemann-blueprint as the source.** Nothing else meets section 1.
- **Keep Sutherland's export as the ground truth for edges.** None of these sources improves on it.
- **Read tanclary's dominator tree against the blueprint's nodes.** Where the kernel's dominators and the
  blueprint's statements disagree is a verdict on the blueprint's choice of what deserves a box, as F7 is on its
  arrows. It would need a derived file pinned by hash, as Phase 8 has it, and the tree is not pinned to an
  upstream commit, so the first step is to establish which tree it was computed from.
- **Watch Rubinstein's guide.** Once v2 settles, its (M) and thirteen hypotheses are a second, human-written
  frame for a poster of their own.

## 5. How this was gathered

The six sources were read through their web pages on 2026.11.24, by summary rather than in full where a page was
long; their numbers are their own and were not checked here. The two PDFs, Rubinstein's guide and Alpöge's
announcement, were not readable as text. Section 3 alone was checked: the blueprint was cloned, its README read
at each commit, and its statements counted from the front matter at the four commits in the table.
