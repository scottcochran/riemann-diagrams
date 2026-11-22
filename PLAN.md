# Development plan

Written 2026.11.22, after the two posters R1 and R2 and the Graphviz diagrams the README records, and updated the
same day as Phase 1, the five chapter posters that follow it, Phases 2, 3 and 5 were done. It is a plan, not a
record: nothing below is built unless the README says so. Four of its first five phases are done; what is left
is Phase 4, which waits on a machine, two hand steps under Phase 5, Phase 6, other frames to draw the same
sources in, and the decisions under "Open" at the end.

## Goal

Diagrams that let a reader see Alpöge's proof of the Riemann Hypothesis as a structure: what is claimed, what
the claim reduces to, which arguments carry it, and what each argument rests on. Every diagram is generated from
the riemann-blueprint and the mirror of the formal proof, and its build fails when those sources no longer say
what the diagram draws.

R1 shows the top of the tree (the five theorems and the chain of reductions), R2 the map of the chapters, R3 to
R8 the inside of each stage chapter, lemma by lemma, and T1 and T2 one chain each through the whole, read as a
proof, and F1 the definitions in a frame of their own. What is drawn is now every statement of the blueprint but
the published-results chapter, and CI rebuilds all eleven posters from the pinned sources on every push. The next
level is to make the edges true (Phase 4).

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
   every proof status reads absent. Every poster says so, and no diagram claims that a statement is proved.
6. **Standard library only** for the posters, so that anyone with Python 3.12 can regenerate them.

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

Everything here rests on edges resolved from source text. The blueprint tool's `extract` command, run against
built oleans, would replace them with the real reference graph and fill in each statement's proof status.

- Needs the mirror built: the community build cache (about 5 GB) or a clean build (hours, about 100 GB of
  disk), and a machine with a lot of memory for the extraction. Not a laptop job.
- When the mirror's Comparator run finishes and its notes record a result, R1's band 5 is the first thing to
  update, and a status pill on every card the second.

**Done when** `lean-facts.json` carries statuses, the posters show them, and R1's "Judged" card reports a
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

  Before 1.0, releases stay at `0.x`, and a MAJOR change may take a MINOR. 1.0 waits on Phase 4, and on the
  first open decision below: the posters must not be published more widely than this repository until the
  quoting question is settled, and a release of a private repository is not wider.
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
  tree. It also exposes the fan-out: 358 statements name two or more declarations, one names 23, 281 name none.
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
`architecture/sec-outline-interfaces/` (`INTERFACES`), and the count of definitions. The what-is-new poster
and the chapter-against-module matrix are next.

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
  than it was.
- **The edges are wrong in places.** A chapter poster laid out around a wrong edge draws a wrong argument with
  confidence. Phase 4 is the fix. Until then, the dashed arrows are the symptom to watch: in three chapters a
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
2. **The height of the big chapter posters.** Theta is 16k pixels, Galois 14k. Decide once, for all six, between
   a second poster per big chapter and a denser row of short cards; the reader who has read them at zoom should
   decide, and a poster split by section is the natural cut if it comes to that.
3. **A poster for the published-results chapter.** 163 statements, nearly all of them leaves, so the chapter
   builder would draw a wide, flat grid that says little. R2's literature table already names the results the
   proof leans on most. A poster of the top twenty, with the chapters that cite each, is the likely form if one
   is wanted at all.
4. **This plan** was kept out of the repository until 2026.11.22, when it went in with the decisions above still
   open, so that its history records them being taken. It stays at the root, beside the README, as tla-kit's
   does; a `decisions/` directory is for the records those decisions produce, if they are written up.
5. **Whether to cut `v0.1.1`.** Taken 2026.11.22: cut, from the commit this entry goes in at, as the first
   release untouched after its run. It ships the same twenty SVGs as `v0.1.0` with the same checksums; its tag
   message says so, and that a reader of `v0.1.0` has nothing to re-read. The reason it exists is the previous
   release's hand edits (Phase 5's done note), not anything a reader sees.
