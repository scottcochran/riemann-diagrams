# riemann-diagrams: could it map Masullo's paper? A reading of `riemann-masullo` and its progress map, 2026.11.23

> **Provenance note.** Written 2026.11.23 by the assistant, at the custodian's direction to write the session up
> as a derived document in this repository. It was written on branch `ccr-3cce512c-weh5x7`, after `bbcc963`.
>
> The custodian had asked Qwen whether riemann-diagrams can be adapted to map A. M. Masullo's *The Music of the
> Primes*, pasted Qwen's reply, and asked for an opinion of it. The assistant answered first from this repository
> and one web search, then, when asked, read the Masullo formalisation itself:
> - [`mccorvie/riemann-masullo`](https://github.com/mccorvie/riemann-masullo) at `5c81fc0` (committed
>   2026.11.23 19:10 UTC), a shallow clone, read and not built;
> - its [progress map](https://claude.ai/artifact/CtQyX8qfYAF822bgHJHHE3) as fetched the same day: generated
>   19:06:04 UTC from that repository's `d37dfd7`, page sha256 `6b97f362…934d`. The page was not rendered. Its
>   data object and the generator that writes it (`scripts/progress/build.py`, `template.html`) were read.
>
> Every number below about that project is the map's or its README's, not a count made here. Both move: the map
> is rebuilt about every 20 minutes. The annex beside this file,
> [`riemann-diagrams-masullo-map-annex-2026.11.23/`](riemann-diagrams-masullo-map-annex-2026.11.23/), holds
> Qwen's reply, the script that read the map's data, and its output. Nothing was built, drawn or changed in
> either project. It decides nothing.

## 1. The question

Qwen's answer, in short: yes, and "the repo barely needs to change", because the generator reads only a
blueprint directory, so the work is to author a Masullo blueprint. It named four blockers (scale and provenance;
no verification floor and no state for a false statement; edges resolved from source text on a moving draft; no
counterpart for F3 and F4), and proposed that the honest adaptation is diagnostic: errata as coloured nodes on the
dependency wheel, to show how deep each disputed step sits and what rests on it.

## 2. What the Masullo project is

**F-1. It is a Lean 4 formalisation of the whole draft, pinned to one PDF.** The manuscript of 2026.11.20
(940 pp., sha256 `e039d3f6…7bf5`) is mirrored in `paper/`, with a Markdown transcription in `transcription/`.
The library follows the paper's table of contents, a file or directory per section. Its README says every
section of its three waves is stated in Lean; Chapters 8 and 14 and Appendix E are left for later. Code is
Apache-2.0; the manuscript is its author's and not covered.

**F-2. It has the Alpöge challenge's Comparator setup, with two targets more.** `Statements.lean`,
`Challenge.lean`, `Main.lean` and `comparator.json` name seven theorems: Mathlib's `RiemannHypothesis`, the four
statements copied verbatim from the Alpöge challenge, and GRH for Dedekind zeta functions and for Hecke
L-functions of every number field. The README says Comparator rejects `Main.lean` for `sorryAx`, as it should
while anything is open.

**F-3. A statement that is false as printed is kept in Lean, with its refutation.** The printed claim goes into
a `…_Printed.lean` file as a proposition under the `Printed.` namespace, with a proof of its negation where one
is found; the repaired statement goes into the section's main file, marked as a deviation. The map counts 887
`Printed.` declarations, 545 of them theorems.

**F-4. `ERRATA.md` has 748 live entries, and 28 steps with no known repair.**

| Kind | Entries | Checked |
|---|---|---|
| F, false as printed | 272 | 84 by a Lean proof resting on nothing open, 187 by two agents in turn, 1 by the integrator |
| I, imprecise, inconsistent or wrongly justified | 401 | two agents in turn |
| M, placeholder or missing piece | 50 | two agents in turn |
| R, report on a part not stated in Lean | 25 | two agents in turn |

The 28 steps are in Chapters 5 (3), 6 (2), 7 (8), 10 (4), 11 (3) and 12 (6), and in §1.4 (2), where the paper
argues its main claim. Among them: §12.3, which is a heading and a note to include the section; and the uniform
bound of §1.4.3, false as printed. Chapter 13 does not yet state its main theorem. The file says most entries
were first reported by an AI agent and that **no entry has been reviewed by a specialist**.

## 3. What the progress map is

**F-5. One self-contained page, generated from the built library and the issue tracker.** `build.py` runs
`lake build`, reads the issues with `gh`, checks its totals against each other, and writes one HTML file that
holds its whole data model as a JSON object. At `d37dfd7`:

| | |
|---|---|
| Sections (stated / blocked / being stated) | 107 (86 / 20 / 1) |
| Paper items (definitions, lemmas, theorems, by number) | 1,617 |
| Theorems in Lean, the project's own, helpers included | 11,015 |
| of them proved | 10,704 |
| of them proved and resting on no `sorry` | 9,882 |
| of them open | 311 (112 claimed) |
| Theorems that carry a paper reference (proved) | 3,801 (3,497) |
| Definitions | 1,756 |

Vendored third-party Lean (4,069 theorems) is shown apart and is not in these totals. By chapter, with the
errata placed by page:

| Chapter | Sections | Theorems | Proved | No `sorry` below | F | I | M | R | No repair |
|---|---|---|---|---|---|---|---|---|---|
| App. A | 6 | 581 | 573 | 573 | 13 | 17 | 0 | 0 | 0 |
| App. B | 9 | 707 | 681 | 666 | 24 | 33 | 8 | 1 | 0 |
| App. C | 8 | 971 | 971 | 971 | 11 | 22 | 4 | 0 | 0 |
| App. D | 6 | 1313 | 1311 | 1305 | 4 | 16 | 3 | 0 | 0 |
| App. E | 18 | 29 | 0 | 0 | 0 | 0 | 3 | 3 | 0 |
| Ch. 1 | 1 | 125 | 121 | 111 | 9 | 8 | 1 | 1 | 2 |
| Ch. 2 | 5 | 562 | 562 | 562 | 3 | 17 | 1 | 0 | 0 |
| Ch. 3 | 5 | 811 | 811 | 811 | 3 | 3 | 0 | 1 | 0 |
| Ch. 4 | 6 | 642 | 636 | 614 | 8 | 8 | 2 | 0 | 0 |
| Ch. 5 | 6 | 1182 | 1130 | 921 | 28 | 54 | 5 | 0 | 3 |
| Ch. 6 | 3 | 346 | 332 | 286 | 16 | 25 | 1 | 0 | 2 |
| Ch. 7 | 7 | 975 | 915 | 725 | 59 | 61 | 3 | 0 | 8 |
| Ch. 8 | 4 | 65 | 0 | 0 | 0 | 1 | 0 | 5 | 0 |
| Ch. 9 | 3 | 373 | 373 | 373 | 11 | 12 | 5 | 2 | 0 |
| Ch. 10 | 5 | 851 | 835 | 711 | 43 | 40 | 2 | 0 | 4 |
| Ch. 11 | 5 | 532 | 516 | 363 | 25 | 41 | 4 | 1 | 3 |
| Ch. 12 | 5 | 315 | 310 | 276 | 12 | 39 | 3 | 2 | 6 |
| Ch. 13 | 2 | 46 | 45 | 32 | 2 | 4 | 1 | 0 | 0 |
| Ch. 14 | 3 | 7 | 0 | 0 | 0 | 0 | 3 | 9 | 0 |

(Two entries fall in no section. The other 582 theorems are the project's general lemmas, 578, and four in a
file that belongs to no section.)

**F-6. Its edges are the real ones.** `scripts/progress/Deps.lean` loads the built `.olean` files with proof
terms visible and lists, for every constant, the project constants in its type and in its body. The page holds
64,878 edges of the first kind and 57,799 of the second, over 17,204 declarations, and 144 "needs" edges between
sections. Nothing is resolved from source text.

**F-7. Its views, as its template draws them.**
- **Overview:** section cards on a grid, a lane per chapter, with the "needs" arrows and a proved/stated bar on
  each card. A switch colours the grid by problems found instead: a heat scale by count, and a mark on a section
  that has a step with no known repair.
- **A section:** a glyph per declaration, grouped under the paper item it states. A theorem's glyph says proved,
  proved but resting on something open, claimed, or open; a `Printed.` theorem is drawn as a refutation. Edges
  are dashed for "used in a statement" and solid for "used only in a proof". Each glyph links to its source line
  at the commit.
- **Problems:** the errata entries of the section, each with its page and the `Printed.` declarations it names
  (259 of the 748 name one the map found), and the table of steps with no known repair.
- **Pace:** proof issues filed and closed over time, and merged pull requests by contributor (1,488, from 78
  accounts other than the owner's).

## 4. Qwen's reply against the two repositories

| Qwen said | Found |
|---|---|
| The generator reads only the blueprint; `RIEMANN_BLUEPRINT` redirects it | True of the reader (`graphs/blueprint_graph.py:41`, `diagrams/src/bp.py:135`) |
| So "the repo barely needs to change" | False for the posters. `d_f2_new.py:42` fixes the provenance counts and fails on others; R3 to R8 are a hand-laid module per chapter of Alpöge's proof; each trace holds the chain it expects. The three Graphviz graphs would follow a new blueprint; the posters would be written again |
| `Main.lean`, `Statements.lean`, `comparator.json`, `paper/`, `transcription/` exist | True (F-2) |
| No verification floor to report | True in R1's sense: Comparator rejects. But the map reports a proof state per theorem (F-5) |
| Erratum F30, Theorem 5.2.4.1(1)–(2), p. 239, on enlargement of S | True, `ERRATA.md` line 138 at `5c81fc0` |
| No state for a false statement; adding one is "the only genuine change" | This repository has none. Upstream has one (F-3), and `PLAN.md` Phase 4 already plans statuses here |
| Edges would be resolved from source text | Not there: they are read from proof terms (F-6) |
| The draft should be pinned by sha256 | It is (F-1) |
| "Conrad's note that the method can't be judged until it's closer to completion" | Not found. `ERRATA.md` quotes the author's preface: he and Brian Conrad know of "several glitches here and there" |
| "There is no Masullo formalisation to put beside" F3 | False, and against the reply's own second paragraph |
| Nobody has extracted the paper's references | The bibliography is transcribed (`transcription/chapters/bibliography.md`). Which statement cites which is not recorded anywhere that was read |
| The useful adaptation is diagnostic: errata on the dependency picture | The map does this at the level of sections and of single declarations (F-7) |

## 5. What the assistant got wrong

- **It doubted three of Qwen's details that were true.** Its first answer said the file list, erratum F30 and the
  Conrad remark might be invented. The first two are exact. It had searched the web and not opened the
  repository.
- **It said "nobody has written a Masullo blueprint" as the bulk of the work.** True, but beside the point: the
  map's data model already holds what a blueprint would (sections, items, declarations, edges, states, errata),
  and from better evidence.
- **Its first answer gave errata counts from secondary write-ups** (about 660; 245 false as printed), a day old.
  The file had 748 entries, 272 of them false as printed.

## 6. What this means for riemann-diagrams

**F-8. Qwen's blockers 2 to 4 are solved upstream.** States per theorem, a state for a false statement, edges
from proof terms and a pinned draft all exist in `riemann-masullo`. A blueprint written by hand for this
repository's reader would be a worse copy of data that project already publishes.

**F-9. A port would mostly repeat the map.** What the map does not draw, and this repository's posters do:
- **A cone per unrepaired step.** The map shows what a declaration uses and what uses it, one step at a time,
  and marks a theorem "resting on something open". It has no picture of everything, across sections, that rests
  on one of the 28 steps, up to the seven targets. F4's cones do that for references here.
- **The whole paper on one page by depth.** F6's wheel, for 1,617 paper items or 3,801 paper theorems where
  F6 holds 409.
- **A fixed, citable drawing.** The map is replaced at each refresh, about every 20 minutes. A poster here is dated,
  checksummed and released from a tag.

**F-10. The input would be the map's data, not a blueprint.** That means a second reader beside `bp.py`, over
the JSON object `build.py` writes or over the outputs of `Deps.lean` and `ERRATA.md` directly, and new poster
modules. `lib.py`, the layout code and the release discipline carry over; `bp.py`'s model and the sixteen
posters do not. The scale differs by an order: 17,204 declarations and about 123,000 edges against 416
statements and 2,004.

**F-11. Not computed here.** No cone was computed and nothing was drawn. The map's data does not tie a
no-repair step to a declaration directly: a step names errata entries, and an entry names `Printed.`
declarations, only for 259 of 748. Which Lean statement stands for each of the 28 steps would have to be settled
first, from the Lean, where the README says each is "a named statement left unproved".

**F-12. The caution a poster would owe its reader.** A drawing of errata gives them the look of findings. The
errata are agent-reported and agent-checked; 84 are Lean-checked refutations; none is a specialist's. A poster
would have to say so as plainly as this repository's README says what its graph is not.

## 7. What the custodian may decide

1. **Whether to do anything.** The map answers most of what Qwen proposed. Leaving it there is a complete
   answer.
2. **If something: which one drawing.** The cone of the 28 steps (F-9, first item) is the one the map lacks and
   the one a reader of the dispute would use. The wheel is the second.
3. **Where it would live.** In this repository as a second target, in a repository of its own, or offered to
   `riemann-masullo` as a view of its own data. The last keeps one source of numbers.
4. **Whether to ask first.** The map, its generator and the errata are the `riemann-masullo` project's, under
   Apache-2.0; the manuscript is its author's. A drawing made from them would quote paper item numbers, Lean
   names and errata summaries, as this repository quotes Alpöge's proof under `NOTICE`.
