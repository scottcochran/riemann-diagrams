# Development plan

Written 2026.11.22, after the two posters R1 and R2 and the Graphviz diagrams the README records, and updated the
same day as Phase 1, the five chapter posters that follow it, Phases 2, 3, 5, 6 and 7 were done. It is a plan,
not a record: nothing below is built unless the README says so. Phases 1, 2, 3, 5, 6 and 7 are done, Phase 6
with two of its eight posters waiting on things outside this repository, Phase 7 released as `v0.2.1`, the
first release whose posters link; what is left is Phase 4, two hand steps under Phase 5, and the decisions under
"Open" at the end, of which 1 and 6 are taken. Phase 4 began on 2026.11.23: its edge data is done and every
chapter and trace poster shows it; the statuses wait on the mirror's Comparator run. Phase 8, the frames the
formal proof's references make possible, was planned and done the same day: F7 to F10.

## Goal

Diagrams that let a reader see Alpöge's proof of the Riemann Hypothesis as a structure: what is claimed, what
the claim reduces to, which arguments carry it, and what each argument rests on. Every diagram is generated from
the riemann-blueprint and the mirror of the formal proof, and its build fails when those sources no longer say
what the diagram draws.

R1 shows the top of the tree (the five theorems and the chain of reductions), R2 the map of the chapters, R3 to
R8 the inside of each stage chapter, lemma by lemma, and T1 and T2 one chain each through the whole, read as a
proof, F1 the definitions in a frame of their own, F2 the new work by chapter and section, and F3 the chapters
against the Lean modules. What is drawn is now every statement of the blueprint but the published-results
chapter, and CI rebuilds all thirteen posters from the pinned sources on every push. The next level is to make
the edges true (Phase 4).

## Rules the design keeps

1. **Every node is read from the files at build time.** A diagram's own words are marked as its own; everything
   else is the blueprint's or the mirror's, and a build fails rather than draw something stale.
2. **The arrows are checked.** A drawn arrow that the source does not make, or a source edge between drawn
   nodes with no arrow, fails the build. Each diagram lists what it expects, so a change in the blueprint shows up
   as a failing check, not a silent redraw.
3. **The sources are pinned.** `bp.py` records three commits: the blueprint's, the mirror commit the blueprint
   pins, and the mirror commit `Main.lean` is read from. Moving one is a deliberate change: bump the pin,
   regenerate, fix what the checks report, never loosen the checks.
4. **The output is deterministic, and CI holds it to that.** Unchanged inputs give unchanged bytes, so a diff in
   an SVG means a source moved under a diagram, and the workflow fails on the first such byte.
5. **No Lean is built.** The blueprint's edges come from static analysis of the source text and some are wrong;
   every proof status reads absent. Every poster says so, and no diagram claims that a statement is proved. The
   edges are checked against the formal proof's references, read from published files rather than a build
   (`src/lean-edges.json`, Phase 4), and a poster that shows a verdict says where it came from.
6. **Standard library only** for the posters, so that anyone with Python 3.12 can regenerate them.
7. **The page matches the content.** In the light theme the page behind the cards is the mean relative
   luminance of the content, measured once on R2 and applied to every poster (`diagrams/PAGE.md`,
   `tools/measure-page.py`); the dark theme is as the library had it.

## Phases

### Phase 1: R3, one chapter from the inside

The zero-free chapter (`chap-zero-free`, "From prime sums to the zero-free half-plane"): the analytic half of
the proof, 24 statements in five sections. The blueprint says of it that the square root in the core inequality
is the Riemann Hypothesis, so it is where the mathematics is, and it is poster-sized.

- One card per statement of the chapter, as in R1: the Lean signature, the statement, the proof, the uses.
- The arrows are the proof uses within the chapter, laid out as the argument runs: Landau's theorem on windows,
  the auxiliary CM fields, the core inequality, slope data from the family hypotheses, the local link at inert
  primes. The chapter's theorem, `thm-zero-free-from-connected`, at the foot.
- What the chapter imports from the other chapters and from the literature, in a table at the foot, with the
  citing statements: the counterpart of R2's literature table, for one chapter.
- Layout is by hand (a `PLACE` dict and an `EXPECTED` edge list, as R1 and R2), because the point of the poster
  is the shape of the argument, and the router is for correctness, not for exposition.

**Done when** R3 builds clean against the pinned blueprint, its arrows are exactly the chapter's proof uses, and
a reader can follow the chain from Landau's theorem to the chapter's theorem without opening the blueprint.

**Done 2026.11.22**, as `R3-zero-free-2026.11.22.svg` (commit `671ee48`). Two things the plan did not foresee:
the chapter theorem takes its two inputs as hypotheses rather than proving them, so the blueprint has no edge
from `thm-families-connected` or `thm-auxiliary-fields` to it; the poster draws those two as dashed arrows,
checked against the proof's text, with a card that says so. And the chapter has five sections, not the "four
other stage chapters" the plan counted: there are five.

#### 1b: the other five stage chapters

The five posters R4 to R8 (families, theta lifts, heights, the Tate–Shafarevich bound, Galois representations)
were done the same day (commit `a0e0579`), but not as the plan said. Five hand layouts of 32 to 61 cards would
have cost more than they taught, so `src/chapter.py` lays a chapter out from its own edges: a card's row is one
above the highest card whose proof uses it, a row wider than the grid sends its most flexible cards upward, and a
card sits under the cards that use it where it can. Each chapter's module is a few lines: its `EXPECTED` edges
and its `HYPOTHESES`, both recorded as literals and checked at build time, as R3's are. R3 keeps its hand layout
and is the exposition the computed ones are measured against.

The short-card decision the risks below asked for was taken here: section heads and the chapter theorem get full
cards, every other statement a short one (four signature lines, one proof paragraph, a trimmed footer). The
posters are still tall, 9.7k to 16k pixels, with theta the outlier; the floor is each chapter's longest
dependency chain, ten to twelve rows. A second poster for theta, or a row of short cards side by side, are the
next options if that height is too much.

### Phase 2: the build in CI

A GitHub Actions workflow that checks out the blueprint at the pinned commit and the mirror at its pinned
commit, regenerates every poster, and fails on any byte difference from the committed SVGs.

- Needs the blueprint and the mirror as sibling checkouts, as `bp.py` expects, or an environment variable for
  each. The mirror is large; CI needs only `src/Main.lean`, `src/Statements.lean` and `comparator.json`, so a
  sparse checkout.
- The Graphviz diagrams stay out of CI: they need the `dot` binary and are not deterministic across Graphviz
  versions.

**Done when** a pull request that moves a pin without regenerating fails, and one that regenerates passes. All
eight posters are deterministic, verified by rebuilding three times, so the byte comparison is ready to be run.

**Done 2026.11.22**, as `.github/workflows/posters.yml` (commits `eff9716` and the version bump after it). The
mirror commit that `Main.lean` is read from is now a third pin in `bp.py`, `MIRROR_COMMIT`, beside the blueprint
commit and the mirror commit the blueprint pins, and all three print at ten characters so that checkouts with
different object counts agree. The workflow resolves the two short pins through the GitHub API, checks the
blueprint out whole and the mirror sparse (three files, blobs on demand), regenerates with Python 3.12, and fails
on a `WARNING`, an `ERROR` or a byte that differs. Python 3.12 and 3.14 were checked to give the same bytes.
Tested both ways: the run on `main` passes; on a throwaway branch with the blueprint pin moved one commit back
and nothing regenerated, seven of the eight posters refused to build because the blueprint's edges no longer
matched their recorded arrows, and the run failed at "Regenerate the posters".

### Phase 3: traces as cards

The one Graphviz diagram the posters do not replace: a single chain from `riemannHypothesis` down to one leaf,
drawn as cards instead of boxes. A `--to` option as `trace_proof.py` has, so that any statement's chain from the
main theorems can be drawn.

**Done when** the deepest chain and the chain to Landau's theorem render as posters, and the Graphviz traces can
be retired from the README. With R3 to R8 in place, a trace is a column cut through them, so the card and the
router it needs exist; only the module is missing.

**Done 2026.11.22**, as `T1-trace-deepest-2026.11.22.svg` and `T2-trace-landau-2026.11.22.svg`, from
`src/trace.py` and a module per chain holding the path it expects. A trace is laid out as text, five full cards
to a row, from the deepest statement to the `Main.lean` theorem, so that it reads as a proof in the order the
other posters are read. The `--to` option stayed with the Graphviz script, which still prints a chain; a new
trace poster is a six-line module. The three Graphviz trace images are retired from the README.

### Phase 4: real edges and statuses

Everything here rested on edges resolved from source text. Phase 4 checks each of them against the references
of the formal proof, and shows the proof's status once one is recorded. The plan was to run the blueprint tool's
`extract` command against built oleans, on a machine with a lot of memory; that turned out not to be needed.

- **The edge data: done 2026.11.23.** The references are read from Sutherland's export of the published proof at
  `MIRROR_PIN`, which holds exactly what the five main theorems depend on. They are cross-checked against every
  compiled module of the mirror at `MIRROR_COMMIT`, from its public build cache. Both runs need only a laptop
  and an external disk, and no Lean is built; `tools/lean-edges/` has the scripts and the steps.
  `src/lean-edges.json` gives a verdict on every blueprint arrow. Its hash is pinned (`LEAN_EDGES_SHA256`), and
  the build checks that it was read from `BP_COMMIT` and `MIRROR_PIN`. `diagrams/EDGES.md` writes up the method
  and the findings.
- **The posters: done.** R3 holds all 17 of its arrows to the verdict `direct`, which every one has. A card,
  "Against the formal proof", reads the chapter against the file: the dashed hypotheses, the uses no arrow
  draws, and the statement uses the cards list. R4 to R8 and the traces followed as Phase 8a, each with the
  verdicts it expects, and an arrow the proof does not bear out drawn in a style of its own.
- **The statuses.** When the mirror's Comparator run finishes and its notes record a result, R1's band 5 is the
  first thing to update, and a status pill on every card the second.

**Done when** every chapter and trace poster shows the verdicts on its arrows, and R1's "Judged" card reports a
recorded result rather than its absence.

### Phase 5: releases

A poster is cited the way an image digest is cited in tla-kit: a reader of R3 wants to say which R3, drawn from
which blueprint, and to fetch that one later after the tree has moved on. The tree cannot keep every drawing,
because a poster's file name carries its date and a regeneration at a new pin replaces it. A release keeps it.

- **A release is an annotated `vMAJOR.MINOR.PATCH` tag on `main`, pushed by the custodian, never moved or
  reused.** The tag message is the release's opening: the kind of move, what changed, and one line saying which
  posters a reader must re-read. The workflow refuses a tag that is unannotated, off `main`, or not the
  custodian's, as tla-kit's does. A `v*` tag ruleset on GitHub (block deletion, update and non-fast-forward)
  is the backstop; the workflow cannot create it, so it is a hand step in the repository settings.
- **A published release is not edited.** Its assets and notes are what the workflow wrote from the tag, so
  that "release X, run Y" names one thing. A release found wrong gets a successor tag whose message says what
  was wrong; it is not patched in place. `v0.1.0` is the one exception, made before this rule was written (see
  its done note).
- **The number says what moved**, adapted from tla-kit's ADR-0014 to what a release can change for a reader:

  | Part | When it changes | What a reader of a cited poster has to do |
  |---|---|---|
  | MAJOR | The checks change: what a poster is verified against (the rules above), or Phase 4 replaces text-resolved edges with extracted ones | Re-read every poster: the arrows may mean something else |
  | MINOR | A source pin moves (`BP_COMMIT`, `MIRROR_PIN`, `MIRROR_COMMIT`), or a poster is added or removed | Re-read the posters the tag message names; the others are the same drawing at a new date |
  | PATCH | Layout, wording or library changes; no pin moves and every `EXPECTED` and `HYPOTHESES` list is unchanged | Nothing: the same statements and arrows, drawn again |

  Before 1.0, releases stay at `0.x`, and a MAJOR change may take a MINOR. 1.0 waits on Phase 4. The first open
  decision below was settled on 2026.11.22, so a release may be wider than this repository.
- **The workflow builds from the tag as CI does**, then does what CI does not: it writes `pins.json` (the three
  pins, the commits they resolve to, the generator's Python version, the tag) and `SHA256SUMS` over everything,
  and creates the GitHub release with the SVGs, the two files and notes. No PNG renders: every browser draws an
  SVG, and a render of these tall posters at a legible width (4000 px wide, body text about 14 px) is 2 to 15 MB a
  poster, 120 MB for the twenty; halving the width halves the bytes and makes the text unreadable. The Graphviz
  outputs stay out of releases too, since `dot` is not deterministic across versions; they are in the tree as
  committed.
- **The notes record what a reader needs to check a citation**: the kind of move; the three pins with links to
  the blueprint and mirror commits; one row per poster with its statement count and the number of arrows, so a
  reader can see what moved between releases without opening the SVGs; the CI run on `main` at the tagged
  commit; and the tag message. A script, `tools/release-notes.py`, writes them from the tag and the tree, as
  `tools/pins.py` and `tools/ci/release-notes.sh` do in tla-kit.
- **Attestation waits.** GitHub's artifact attestations need a public repository or an enterprise plan. When the
  repository is public, the workflow attests the SVG bundle, and the notes carry the `gh attestation verify`
  line.
- **Cadence:** a release when a pin moves, when a poster is added or removed, or when the checks change. Not
  on every push: a wording fix waits for the next move, unless it changes what a poster says. Posters that
  land as a phase are released together when the phase is done (Phase 6), not one by one.
- **The first release**, `v0.1.0`, is the ten posters R1 to R8, T1 and T2 at blueprint `137d976` and mirror
  `2dea990069`, from the commit the plan went in at or the one after it.

**Done when** `v0.1.0` is published from a tag by the workflow, its `SHA256SUMS` matches the committed SVGs at
the tagged commit, and a tag that is unannotated or off `main` is refused.

**Done 2026.11.22.** `v0.1.0` was cut from `c6a6c6c` by `.github/workflows/release.yml`: the tag checks, the
posters check reused from `posters.yml` as a called workflow, then `pins.json`, `SHA256SUMS` and the release with
both sets as files. All twenty SVG checksums in the published
`SHA256SUMS` match the committed files. The generator now writes `manifest.json` beside each set, with every
poster's card and arrow counts, and `tools/release-notes.py` writes the notes from the tag message, the pins and
the manifests. One fault found on the first run: the checkout action fetches a tag peeled to its commit, so the
notes opened with the commit message; the workflow now re-fetches the annotated tag, and `v0.1.0`'s notes were
regenerated and replaced in place, the tag untouched. The first run also shipped the PNG renders as a 105 MB
tarball; the renders were dropped the same day (commit `e2ff184`, see above), the tarball removed from `v0.1.0`,
and its line taken out of the published `SHA256SUMS`, whose twenty SVG lines and `pins.json` line are unchanged.
So `v0.1.0`'s notes and checksum file were edited by hand twice after run 45018046898; the twenty SVGs were
not, and are byte-identical to `main` at `e2ff184`. The rule above ("a published release is not edited") is
the lesson. The tag was not moved: its message says nothing about renders, and the posters it names are the
posters. A `v0.1.1` from `e2ff184`, whose every asset the workflow wrote, is available if the hand edits are
felt to taint the citation; it would ship the same twenty files with the same checksums, so it is a choice,
not a need, and is left open below. The refusal of a bad tag was not tested on this run, since the plan's
test of a moved pin without regeneration already exercised the called check. Still to do by hand: the `v*`
tag ruleset.

`v0.1.1` was cut the same day from `2a58aff` (run 45019565926, 22 assets, nothing touched after it): the same
twenty SVGs with the same checksums as `v0.1.0`, matching the committed files; its tag message says why it
exists. Open decision 5 records the choice.

`v0.2.0` was cut the same day from `1de0cf2` (run 45033058428): 34 assets, the 32 SVGs of both sets with
checksums matching the committed files, `pins.json` and `SHA256SUMS`, and the notes from the tag message. The
release job passed; the Pages deploy that follows it failed, and failed twice more when run by hand: the site
artifact was uploaded each time, and the deploy step, in the same job, listed the run's artifacts and found
none. The artifact had grown from 476 KB at `v0.1.1` to 5 MB with the fonts and the six posters, and the
listing raced the registration. The fix splits `pages.yml` into a build job that uploads and a deploy job
that publishes, as GitHub's own Pages workflow does, with the configure step in the deploy job, which holds
the `pages` permission (the first split had it in build, and failed once more). With that in, run 45035596381
published `v0.2.0` to Pages by hand: the site's `pins.json` names the tag and its index lists all sixteen
posters of both sets. The release itself was not touched.

### Phase 6: other frames

Every poster so far sits in one frame: the blueprint's `uses` graph, laid out as an argument from the main
theorems down. The sources at the current pins carry other frames, and one deeper level, that none of the ten
posters touches. Each item below is one poster, built by the existing reader from the blueprint and
`lean-facts.json`; none needs Lean built except the last, which is Phase 4's.

- **Definitions as the joints between stages.** The blueprint has 24 definitions, and the architecture chapter's
  interfaces section names three as the contracts between chapters: polarised Galois representations, the Sha
  bound, local parameters. A dataflow poster: the definitions in the middle, the chapters around them, an arrow
  for "this chapter produces this object" and one for "this chapter consumes it". It shows what passes between
  stages, not who proves what.
- **What is new.** Provenance splits the 416 theorem-like statements into 200 new, 61 modified, 142 published
  and 13 unmarked. A poster of the new statements alone, published inputs collapsed to ports on the edge, shows
  where the proof's novelty concentrates and how the new pieces lean on each other. Today provenance is a colour
  on each card; here it is the organising principle.
- **The proof as literature.** The published-results chapter has 142 statements in 16 sections (class field
  theory, L-functions, Galois cohomology, p-adic Hodge theory, ...), and the reference list 209 entries from
  Riemann 1859 to Bhatt–Scholze 2023. A timeline poster places each cited result by year and links it to the
  chapters that use it. The upward cone of one result, "if this paper were wrong, what falls", is the same data
  read in reverse: T1 and T2 descend from the top, this ascends from a leaf. Takes open decision 3 with it.
- **The proof as code.** `lean-facts.json` gives a module for each of the 1194 declarations: 460 in
  `Development.AbelianVarietyTheory`, 327 in `Development.AutomorphicArithmetic`, 134 in `Development.WeilBound`,
  then the formalism, companion, ground, reciprocity and positivity theories. A matrix of blueprint chapter
  against Lean module shows how the paper's organisation maps onto the formalisation's, which is not the same
  tree. It also exposes the fan-out: 358 statements name two or more declarations, one names 23. (The entry
  first said 281 name none; that counted references and sections. Of the 416 statements, 3 name none, and
  `lean-facts.json` holds exactly the declarations the statements name, each named by one statement.)
- **Depth as geometry.** A radial poster, rings by distance from the main theorem and sectors by chapter, is the
  Graphviz depth graphs' measure in a frame where all 416 statements fit one page with meaning: it shows how far
  each chapter reaches down.
- **Sections as the middle level.** Between 9 chapters and 416 statements sit 58 sections. A poster per chapter
  with sections as nodes and edges rolled up to section level is R2 one step down, and the first cut to try for
  the big chapters whose height is open decision 2.
- **Change between pins.** The blueprint reorganised twice in its first days, and releases are tied to pin
  moves. A diff poster between two pins (statements added, removed, renamed; edges changed) makes a MINOR
  release's "re-read these" line visible rather than stated. Needs the reader to load two checkouts.
- **The deeper level: declarations under a statement.** Below a card lies the Lean declaration graph, which
  theorem's proof term uses which. `lean-facts.json` gives each declaration's location but not its dependencies,
  so this waits on Phase 4. When it lands, two posters follow: a blueprint edge drawn against the formal edges
  beneath it, agreeing or not; and one statement opened to its declarations with the dependencies among them.

Order: the definitions poster and the what-is-new poster first, as new frames cheap to build that answer
questions the set cannot (what flows between stages; where the original work sits); the chapter-against-module
matrix third, the only frame that puts the paper and the formalisation side by side. The rest as wanted.

**Done when** the three named posters build under the same checks as R1 to T2, in both sets, and the README
and `diagrams/README.md` record them. One MINOR release, `v0.2.0`, once the phase is done, carrying the three
posters together; no release per poster. Decided 2026.11.22, after F1 landed without one.

**Started 2026.11.22.** The definitions poster is `F1-definitions-2026.11.22.svg`, `src/d_f1_definitions.py`,
in both sets. Two things differ from the entry above. The consumption is drawn as a table, not as arrows: 24
definitions reach nine chapters by 44 (definition, chapter) pairs, and 44 arrows into nine small cards through
the grid's gutters would have been a thicket; the table has a cell per pair, with the making chapter marked,
and the same counts stand in each card's footer. And the grid gained a frame of its own: the 14 definitions
joined by a `uses` edge are laid out by `chapter.layout`, the families chapter's tower from auxiliary field
data to family data running down seven rows, and the 10 that no edge touches fill the emptiest rows. The
build checks the 18 definition-to-definition edges (`EXPECTED`), the three interface definitions under
`architecture/sec-outline-interfaces/` (`INTERFACES`), and the count of definitions.

The what-is-new poster is `F2-new-2026.11.22.svg`, `src/d_f2_new.py`, in both sets (9 chapter
cards, 11 arrows). It is not the poster the entry above describes: 200 new statements with 263
proof-use edges among them and chains 16 long are three times R5, and a card each would not be legible. So it
works one level up, the chapters as cards holding only their new work, with the proof uses between the new
statements of different chapters as labelled arrows and as a 9 × 9 matrix, every section by provenance as the
map of where the new work sits, the twenty inputs the new work leans on most, and the 24 new lemmas that
published results' proofs use. Two findings the data forced into the design: proof uses among new statements
run upward against R2's chapter order in five chapter pairs (the outline's local-parameters theorem, used by
the Sha and Galois chapters, is most of it), so those are listed and counted rather than drawn; and the
published-results chapter has two new lemmas of its own. The build checks the provenance counts (`COUNTS`),
the cross-chapter pair counts (`EXPECTED`), the 16 tops of the new work (`TOPS`), and the provenance of the
three interface definitions. The arrow router gained per-edge labels for it; the other posters are unchanged
to the byte.

The chapter-against-module poster is `F3-modules-2026.11.22.svg`, `src/d_f3_modules.py`, in both sets (10
namespace cards, no arrows). The survey for it corrected the entry above: `lean-facts.json` is the blueprint's
index of the formal proof, exactly the 1194 declarations the 416 statements name, each named by one statement,
3 statements naming none; it is not a census of the formalisation. The poster says so. Its matrix is chapters
against the 35 second-level modules under 10 namespaces, grouped by namespace; the three largest theories hold
77% of the declarations, and the literature chapter alone names 445 of the 1194. Then the formalisation's tree
as cards, each chapter's footprint (declarations, kinds, modules, files, lines spanned), and the fan-out, with
the finding that 200 of the 416 statements name exactly two declarations, 130 of those a definition and a
theorem, the `Prop`-and-proof pattern R1 shows for `Main.lean`. The build checks the declaration count,
the kinds, the module count, the per-chapter counts, the three statements without a declaration, and that no
declaration is named twice. With F3 the three named posters are in, and the phase's done-when is met: `v0.2.0`
is the next step, from `c042157` or later.

One fault found by CI on F3's first commit, and a rule from it: `Graph.statements` is a Python set, so a
`Counter` built by iterating it orders equal counts by the process's hash seed, and `most_common()` then differs
between machines while every local run agrees with itself. Every ranking now sorts by count then name, the
statements are iterated sorted, and a new poster is regenerated under two `PYTHONHASHSEED` values before it is
committed. The posters check prints the diff lines it finds, not only the stat.

A second rule, from writing `diagrams/TEXT.md`: a sentence on a poster that reads the data is computed or
guarded. Four were neither: F1's tallest tower (now computed), F2's heaviest flows (the pairs computed, the
reading behind `HEAVIEST`), F3's fan-out pattern (behind a majority check), and R1's band 5, which paraphrases
the mirror's `verification/NOTES.md`; the generator now reads that file and fails if it no longer hashes to
`NOTES_SHA256`, and CI checks it out with the other three mirror files.

**The rest of the phase, on a branch (`phase6-rest`), from 2026.11.22.** The literature poster is
`F4-literature-2026.11.22.svg`, `src/d_f4_literature.py`, in both sets. The reference list turned out richer
than the entry above assumed: every entry carries author, title, journal and year, and 196 statements carry a
`source` line citing entries, 90 of them more than one, so the timeline is drawn from the entries and the
citations from the source lines, not from `uses` edges, which never point at a reference. Two findings: 35 of
the 209 entries are cited by no statement, and the upward cones of 172 of the 174 cited references reach a
theorem of `Main.lean`, so the Riemann Hypothesis rests, by the blueprint's own edges, on nearly every source
it names; the two exceptions are Casselman–Shalika 1980 and Shintani 1976. This settles open decision 3: the
published-results chapter has its poster, as the literature rather than as a grid of 163 leaves. The build
checks the reference count, the year range, the number of citing statements and the four most-cited references.

The sections poster is `F5-sections-2026.11.22.svg`, `src/d_f5_sections.py`, in both sets: one poster, not one
per chapter as the entry said, since the nine bands stack to 14k pixels, the height of R5, and a reader wants
the chapters in one reading order. Each band is laid out by `chapter.layout` from the section-to-section proof
uses, with the arrows labelled by their counts; two pairs of sections use each other (the Sha chapter's root
against three of its sections, and the literature's p-adic Hodge against its Galois cohomology), and the
lighter direction is listed, not drawn, chosen by the same heaviest-first rule. Cross-chapter uses are counted
on the cards and left to R2. The build checks the section and unit counts, the per-chapter pair and edge
counts, and the pairs that point upward. On open decision 2: this is the middle level the entry proposed as
the first cut for the big chapters' height, and it is itself as tall as R5, so the decision stands open.

The wheel is `F6-depth-2026.11.22.svg`, `src/d_f6_depth.py`, in both sets: 409 of the 416 statements on
eleven rings by breadth-first depth from the three roots, in nine sectors by chapter, each a dot in its
provenance colour with its id set along the radius, and the chains of T1 and T2 traced through the rings. The
drawing library had nothing radial, so the module draws the wheel itself: rings, sectors, rotated ids, and a
placement rule, since an id is longer than the ring spacing and a ring's labels reach into the next ring's
band. Each ring's dots go into the gaps between the angles of the ring inside, no two closer than the pitch of
the labels, and a sector is widened until every ring of it fits; the sector widths are therefore the diagram's
own, not the chapters' sizes, and the poster says so. The rotated ids are outside the overlap check, which
knows only upright text; the README says so. Seven statements no edge reaches are listed, not drawn. The build
checks the depth histogram, the unreached statements and that the two chains are chains in the blueprint.

With F4, F5 and F6 the phase's buildable posters are in. The two that remain, change between pins and the
declarations under a statement, wait on a blueprint move and on Phase 4.

**Done 2026.11.22**, six of eight: F1 to F6 build in both sets under the same checks as R1 to T2, and the
READMEs record them. Change between pins waits on the first pin move; the declarations under a statement
wait on Phase 4. `v0.2.0` is cut from the commit this note goes in at, carrying the six posters and, since
every file changed, the embedded fonts, the grey page and the sentence guards of the same day.

### Phase 7: links

The Pages site serves each poster as `image/svg+xml`, opened on its own, and there an SVG `<a>` works: a reader
can click from a card to the statement it names. Today nothing on a poster is a link, so every id in a footer
is a name to look up by hand. This phase makes the ids links, in both sets, without changing what is drawn.
Tested in Chromium on 2026.11.22: an SVG opened on its own scrolls to the element `poster.svg#id` names, both
from the address bar and from an `<a>` inside it. Firefox and Safari are untested.

- **Each statement card carries its blueprint id** as the `id` of a group around it, so that
  `R3-zero-free-2026.11.22.svg#thm-landau-windows` lands on the card. A statement drawn on more than one poster
  has the same id on each.
  Done 2026.11.22: `bp.node` takes an `anchor`, `statement_card` passes the statement's id, and R2's and F2's
  chapter cards and F5's section cards pass theirs; a build fails on an id drawn twice or an anchor that is
  not an XML name; each manifest entry lists its poster's anchors. The chapter-root cards of F5, R1's
  `Statements.lean` card and F3's namespace cards have no blueprint id and no anchor.
- **Ids link to the card that draws them.** An id in a Stated with, Proof uses or Used by footer links to its
  card on the same poster when there is one, else to its card on the poster that draws it in full (R1 and the
  traces into R3 to R8), else to the blueprint (below). A chapter card on
  R2 or F2 links to that chapter's poster. The targets are computed from the posters' own card lists at build
  time, not written by hand.
  Done in part 2026.11.22, the links within a poster: `Canvas.link` runs over the finished poster, and a code
  run whose text is exactly one of the poster's anchors becomes `<a href="#id">` around its `<tspan>`, so
  footers, card text and keys link alike; a build fails on a link to no card. The links to other posters done
  2026.11.22: the set's `manifest.json`, which lists every poster's anchors, is the registry; an id with no card
  on the poster links to the first poster in `lib.HOME_ORDER` (R3 to R8, F1, R1, T1, T2, F5, R2, F2) that
  anchors it, by a relative href; a chapter card on R2 or F2 links to the chapter poster that anchors all its
  statements; a build fails on a link to a card no poster of the set draws. When a run moves a poster's
  anchors it updates the manifest and asks for a second run. The links out done 2026.11.22, below.
- **The rest link out, at the pins.** An id with no card on any poster links to the blueprint; the Lean line to
  the declaration in `leanprover-community/riemann-hypothesis` at `MIRROR_COMMIT`, at the file and line
  `lean_location` gives (`…/blob/<commit>/<file>#L<line>`). Which blueprint target to use is open decision 6.
  Done 2026.11.22, decision 6 taken for the pinned file: `bp.load` sets `lib.EXTERNAL`, every blueprint id to
  its file at `BP_COMMIT` (`…/blob/<full sha>/blueprint/<path>`), and `lib.PINNED`, the three prefixes a link
  out may have; a code run naming an id no poster draws links there. The Lean name and location at the foot of
  a card link to `…/blob/<full sha>/<file>#L<line>` in the mirror at `MIRROR_COMMIT`, the one declaration under
  `.lake/` excepted; a card's blueprint path links to its file, a chapter card's to its directory. The rich text
  gained a link run, `[[@url|text]]`, for a run the code splitter breaks into pieces.
- **Each set links only within itself.** A map poster never links to a reader poster, so that following a link
  from the set that may be published never opens the text that may not.
- **A release's SVGs stay the tree's SVGs, byte for byte.** That is what a release pins: `SHA256SUMS` is checked
  against the committed files (Phase 5), and the Pages job refuses a site that differs from the release. So no
  workflow may rewrite a poster's links on the way out, and the links have to resolve, as committed, in both
  layouts a poster is read in: the tree's (`diagrams/`, `diagrams/map/`, which the site copies) and the release's
  (one flat list of assets, the map set renamed `map-*.svg`; a GitHub release has no directories). Today they
  disagree, and a link written for the tree would do worse than break in a downloaded release: from
  `map-R1-….svg`, a relative `R3-zero-free-….svg` opens the reader R3 beside it, the quoted text the map set
  exists to leave out. The fix is to make the two layouts agree: the generator names the map posters
  `map-*.svg` in the tree too, in `diagrams/map/`. Then a map poster links to `map-R3-….svg` and a reader to
  `R3-….svg`, and each resolves within its own set in the tree, on the site and in a release alike. The release
  workflow and the Pages check copy files as they are, without renaming; the asset names `v0.1.x` cited do not
  change; only the tree's and the site's map paths gain the prefix, which the README and the Pages index follow.
  This rename lands first, on its own, before any poster carries a link. Done 2026.11.22: the generator writes
  `diagrams/map/map-*.svg`, the release and Pages workflows copy without renaming, and the release notes read the
  name from the manifest. The map SVGs are byte for byte what they were; only their names moved.
- **Links that leave the set cannot be pinned by a relative path**, so they are absolute: the
  mirror at `MIRROR_COMMIT`, the blueprint as open decision 6 settles, and never the Pages site, which holds one
  release at a time and would send a reader of an old release to the current posters. Done 2026.11.22, as above: the full shas, not the pins.
- **The library.** `Canvas.card` takes an `href` and an `anchor`, and wraps the card in `<a>`; the id runs in
  footers are `<a>` elements inside the `<text>`, which SVG allows. Plain `href`, not `xlink:href`. Neither
  changes a measured width, so the overlap checks hold unchanged. The embedded `<style>` gains a hover rule (a
  heavier card border, an underlined id), since an SVG link otherwise looks like any other text. The root
  `<svg>` loses `role="img"`, which hides its links from a screen reader and the keyboard; its `<title>` and
  `<desc>` stay.
  Done in part 2026.11.22: the id runs are `<a>` inside `<text>` with a plain `href`, the style has the hover
  rule for them, and the root `<svg>` has lost `role="img"`. `bp.node` takes an `href`, which wraps the card's
  frame, title and pill in `<a>` (not the body: its id runs are links of their own, and SVG does not nest
  `<a>`), with a heavier border and an underlined title on hover; R2's and F2's chapter cards use it.
  `Canvas.card`, the plain card, takes none.
- **The build checks the links**, as it checks the arrows: every relative `href` names a file in the set's
  manifest, every fragment is an `id` in that file, every id is a blueprint id, and every external link is at a
  pinned commit. A poster with a broken link fails the build.
  Done 2026.11.22: `Canvas.check` holds every `href`: a fragment to an anchor of the poster, a relative path to a
  poster of the set and to its anchor, an absolute one to a `lib.PINNED` prefix.
- **What it does not do.** A poster inside an `<img>`, as the README embeds R1, or in GitHub's file viewer, draws
  the same and links nowhere. The README points to the Pages site for reading.
- **The target is framed.** Done 2026.11.25, after the plugin's linking-posters: every anchored card and every
  poster's header (`top`, which R2's and F2's chapter cards now link to) has a halo, shown by `:target` and
  without its pulse under reduced motion, and `check-links.py` with `require_targets` and `frame_classes` holds
  every link to a target and every target framed. The content of every poster is unchanged, and every poster's
  bytes changed.

**Done when** every footer id and Lean line on all sixteen posters is a link, in both sets, the link check
runs in CI and in the release workflow, a map poster's links resolve to map posters in a downloaded release
and on the site, the release's `SHA256SUMS` still matches the committed files with no step between, and the README
and `diagrams/README.md` say where links work. A PATCH release, since no pin, `EXPECTED` or `HYPOTHESES` list
moves and the drawing is the same: the next after `v0.2.0`, or with it if Phase 6's release has not been cut.
Done 2026.11.22, in five pull requests, the map rename first: the READMEs say where links work and where they
do not, and `v0.2.1` is the release.

Added 2026.11.22, after the release: on F4 every reference's title links to the paper, by its DOI where it has
one, else a stable scan (numdam, EuDML, arXiv, the Internet Archive, the Clay Institute for Riemann 1859) or
its zbMATH record, and the id beneath keeps linking to the blueprint's entry. The links are the diagram's own,
in `diagrams/src/papers.toml`: 130 from Crossref, each verified against the DOI's own record; 46 from zbMATH
Open, which Crossref misses for the older literature; 32 settled by hand, with a note where the choice needs
one; the blueprint's one `url`. The build fails on a reference without a paper, an entry that is not a
reference, or a link out that is neither pinned nor a paper. The proper home for the links is a `doi` field
in the blueprint's reference files; until the blueprint carries one, the table here stands in.

### Phase 8: what the formal proof shows

Phase 4's verdicts (`src/lean-edges.json`, `diagrams/EDGES.md`) let the set draw the proof as the Lean has it,
not only as the blueprint draws it. This phase turns them into five frames, in order of what a reader learns.

One rule covers the data. A poster reads only files in this repository, with the standard library (rules 1
and 6). Frames 8a and 8b read `lean-edges.json` alone. 8c to 8e each need a derived file beside it, which
`tools/lean-edges/` writes from the export. Each such file is pinned by hash in `bp.py`, as `LEAN_EDGES_SHA256`
is, checked against `BP_COMMIT` and `MIRROR_PIN`, and described in `EDGES.md`. A derived file holds facts about
statements, not the declaration graph, and stays well under a megabyte.

- **8a: verdicts on every chapter and trace poster.** R4 to R8 do what R3 does. Each module lists the verdicts
  its arrows have (`VERDICTS`: every arrow `direct` but the ones named), and the build fails on another.
  `bp.arrows` draws an arrow by its verdict: `beside` and `apart` get styles of their own, the legend lists
  only the styles a poster uses, and nothing changes for an arrow that is borne out. Each chapter poster gets
  the card "Against the formal proof", or a band where the grid has no room. T1 and T2 give each link of their
  chain its verdict and say whether the chain holds in the Lean. The dashed arrows of R7 and R8 come first:
  the risks below name them as the edges to check.
  **Done when** every chapter and trace poster shows its verdicts, which is the edge half of Phase 4's "done
  when".
  Done 2026.11.23. `chapter.build` and `trace.build` take `VERDICTS`, and R4 to R8, T1 and T2 list theirs. The
  chapter modules also list `HYPOTHESES_LEAN`, what the Lean does with each dashed arrow's source, and the build
  checks both. `bp.VERDICT_STYLE` draws `through` thin, `beside` grey dotted, `apart` red dotted, and an arrow
  with no Lean at one end faint dotted; `bp.verdict_legend` adds only the styles a poster uses. Each chapter
  poster has a full-width card "Against the formal proof" under its key, and each trace's chain card says
  whether the chain holds. Both traces hold: each has one link borne out only by way of other statements. Of
  the chapter posters' drawn arrows, R4 has 4 `apart`, R5 4, R6 6, R7 5 and R8 4. In R7 all five come from
  `thm-hilbert-modular-inputs`; in R8 all four involve `thm-base-change-unitary`.
- **8b: F7, the blueprint against the Lean, chapter by chapter.** A matrix like F3's: a row per chapter that
  uses, a column per chapter used, and in each cell the arrows by verdict and the uses the blueprint does not
  draw. It shows where the blueprint's graph can be trusted, and that most of the trouble sits in a few
  statements. A second band compares depths: each statement's depth from the main theorems in the formal
  graph, against its depth in the blueprint (F6), listing those that move by two or more. Reads
  `lean-edges.json` alone.
  Done 2026.11.23 as `d_f7_verdicts.py`. Two things changed from the plan. Most statements move in depth: 150 by
  two or more, 112 of them two deeper in the Lean. So the depth band is a cross-table of blueprint depth
  against Lean depth, with a count of moves and a list of the 14 that move by three or more. And the matrix is
  two tables, arrows and uses with no arrow, with the statements the trouble concentrates in beside them. The
  build checks the counts by verdict, the two statements that hold 90 of the 167 arrows not borne out (every
  other holds at most 4), and the depth moves.
- **8c: F8, what the proof assumes and what it invokes.** 157 arrows are borne out only through the fields of
  a structure: A takes B as a hypothesis rather than proving or citing it. F8 draws each such package (such as
  `LiteratureCMHypothesis`): its fields, as statements, and the statements that take it. Against F4, the
  literature chapter, it says which published results are hypotheses of the final theorem and which the proof
  applies as lemmas. Needs `lean-hypotheses.json`: per package, its Lean name, the statements its fields
  state, and who takes it.
  Done 2026.11.23 as `d_f8_assumptions.py`, with `tools/lean-edges/hypotheses.py` writing the file. The framing
  changed with the data. The theorems of `Main.lean` are closed, so no published result is a hypothesis of the
  final theorem; every assumption is discharged inside the proof. F8 shows where each enters and where it is
  discharged. There are 8 structures behind the 157 hypothesis arrows, each with its builders and the
  statements that reach them. For every statement's `Prop`, it gives whether a theorem of the proof concludes
  it: outright for 275 of 289, and for all 184 of the literature chapter's. It also gives the export's axioms:
  the three `comparator.json` permits, and no `sorryAx`. The build checks the structures, the counts by class
  and the axioms.
- **8d: where the formal work is.** Per statement, the declarations under its Lean that no other statement
  reaches first, with their count and size. Drawn first as a measure on F2 (new, modified, published) and on
  F6's wheel, then as the deeper frame of Phase 6: one statement opened to its declarations, R3's chapter
  theorem first. Needs `lean-weight.json`, and a file per opened statement.
  Done 2026.11.23 as a poster of its own, F9 (`d_f9_weight.py`), rather than marks on F2 and F6, which keeps
  those two and their checks as they were. `tools/lean-edges/weight.py` writes one file that holds the opened
  statements too. R3's chapter theorem turned out to be glue: 2 helpers of its own and
  48 shared. So F9 opens the statement with the most formal work of its own as well,
  `thm-family-membership-admissible-data`, with 12,225 helpers across 452 namespaces. Statements marked new hold 81% of the
  formal work any single statement owns. The build checks the file's totals, the three heaviest statements and
  the statements opened.
- **8e: drift between the pins.** The export (at `MIRROR_PIN`) and the cache (at `MIRROR_COMMIT`) are about
  230,000 declarations apart, and ten of the blueprint's Lean names are not in the published proof. A poster
  per chapter of what the later tree dropped, and of which blueprint names point at nothing. It is Phase 6's
  "Change between pins" for the Lean. Needs `lean-drift.json`.
  Done 2026.11.23 as one poster, F10 (`d_f10_drift.py`), rather than one per chapter; `tools/lean-edges/drift.py`
  writes the file. Comparing like with like meant closing the cache graph from the same five theorems as the
  export. Names had to be sorted by kind, because the compiler's auxiliaries and private names change with
  the Lean version: 199,833 auxiliaries left and 193,811 private names joined.
  Of the user-written names, 8,324 left the closure, 7,693 of them still compiled
  but unused, and 659 joined. Of the blueprint's Lean names, 5 are gone
  from the later tree. The build checks the counts by kind, the user-written names that left and the names'
  statuses. With 8e, Phase 8 is done.

Order: 8a, then 8b, which need nothing new; then 8c, which has the most to say about the mathematics; 8d and 8e
as wanted. Releases follow Phase 5's table: a batch of 8a's posters changes what they are verified against, a
MAJOR that takes a MINOR before 1.0, and each new poster is a MINOR.

## Risks

- **The blueprint moves.** It is young and reorganised twice in its first days. Every move costs a pin bump and
  a pass over the failing checks. That cost is the design, and the six chapter posters multiply it: six
  `EXPECTED` lists and `HYPOTHESES` lists to keep true, and R3's `PLACE` dict. The computed layouts of R4 to R8
  take a move without hand work; R3 does not.
- **A chapter does not fit a poster.** Decided for now: short cards for everything but the heads (1b above). The
  posters still run to 16k pixels for theta. If that is too tall, the choice is between a second poster per big
  chapter and a denser row of short cards, and it is a choice about the card, so it should be made once for all
  six.
- **A computed layout can mislead.** R4 to R8 place cards by their edges, not by the chapter's exposition. Where
  a row holds cards from several sections, the eye reads a relation the blueprint does not state. The section
  band at the foot of each poster is the corrective; a reader should be told to use it.
- **The quoted text is not this repository's to license.** The blueprint carries no licence file and the formal
  proof was published without one. The NOTICE says so. The plan asked for the question of how much is fair to
  reproduce to be settled before Phase 1 shipped; it was not, and the ten posters now quote the statement, an
  abridged proof and a Lean signature of some 250 statements. The question is open below, and more pressing
  than it was. Settled 2026.11.22 for the blueprint's prose, by its author's
  CC BY 4.0 grant (Open, 1); the Lean signatures remain unlicensed.
- **The edges are wrong in places.** A chapter poster laid out around a wrong edge draws a wrong argument with
  confidence. Phase 4 is the fix: `diagrams/EDGES.md` has what the check found, and R3 is the first poster to
  show it (of its two dashed arrows, the Lean bears out one). R4 to R8 and the traces now show it too, and the
  check answered the question below: the Lean reaches none of the five dashed arrows of R7 and R8. Those
  results are named in the proof text, but the formal proof neither uses them nor takes them as hypotheses. The
  text as it stood: in three chapters a
  proof's text names a result its `uses` list leaves out, and the diagram cannot tell a hypothesis the Lean
  theorem takes from an edge the blueprint's resolution missed. The three in the Tate–Shafarevich chapter and the
  two in Galois representations are the first edges to check against the Lean when Phase 4 runs.
- **Stray files in the tree.** A note saved into `diagrams/` was committed once by staging the directory. Stage
  by name, or keep notes outside the tree.

## Open

Decisions the work so far has raised and not taken. Each is a choice the author should make, not a task.

1. **How much of the blueprint and the proof to quote.** See the licensing risk above. The options run from
   asking the blueprint's authors for a licence, to trimming the cards to the Lean name, the title and the
   blueprint link, which makes the posters maps rather than readers. Both are in hand since 2026.11.22: an
   issue asking for a licence is drafted, and `--map` builds the trimmed form into `diagrams/map/`, checked in
   CI beside the readers. Until the answer comes, the map set is what may be published; the readers stay here.
   Taken 2026.11.22: Christian Merten, the blueprint's author, licensed its prose under CC BY 4.0, by a message
   on Zulip; `NOTICE` records the grant, the reader set may be passed on under it with the attribution kept, and
   the map set stays as the form that quotes nothing. The Lean signatures remain unlicensed.
2. **The height of the big chapter posters.** Theta is 16k pixels, Galois 14k. Decide once, for all six, between
   a second poster per big chapter and a denser row of short cards; the reader who has read them at zoom should
   decide, and a poster split by section is the natural cut if it comes to that.
3. **A poster for the published-results chapter.** 163 statements, nearly all of them leaves, so the chapter
   builder would draw a wide, flat grid that says little. R2's literature table already names the results the
   proof leans on most. Taken 2026.11.22: F4 draws the chapter as the literature, the 209 references by decade
   with their citations and upward cones, and the top twenty-five with the chapters that lean on each; no grid
   of the 163 statements is drawn.
4. **This plan** was kept out of the repository until 2026.11.22, when it went in with the decisions above still
   open, so that its history records them being taken. It stays at the root, beside the README, as tla-kit's
   does; a `decisions/` directory is for the records those decisions produce, if they are written up.
5. **Whether to cut `v0.1.1`.** Taken 2026.11.22: cut, from the commit this entry goes in at, as the first
   release untouched after its run. It ships the same twenty SVGs as `v0.1.0` with the same checksums; its tag
   message says so, and that a reader of `v0.1.0` has nothing to re-read. The reason it exists is the previous
   release's hand edits (Phase 5's done note), not anything a reader sees.
6. **Where a blueprint id links to** (Phase 7). The blueprint site (`riemann.fuxi.merten.dev/#<id>`, which the
   full Graphviz graph already links to) renders the statement for reading, but follows the blueprint's head,
   not `BP_COMMIT`, so a link from an old release can land on a statement that has moved or gone. The
   statement's file in `chrisflav/riemann-blueprint` at `BP_COMMIT` is what the poster was drawn from, and stays
   true, but is raw Markdown and TOML. Rule 3 argues for the pinned file; a reader argues for the site. Taken 2026.11.22: the pinned file, with the
   full sha, for rule 3; a link from an old release stays true, and a reader who wants the rendered statement
   is one click from the site.
