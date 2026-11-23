# Where the text on a poster comes from

Every word on a poster is one of four things: a quotation from the blueprint's prose, a value read from the
blueprint's front matter or the Lean facts file, a quotation from the formal proof's source, or a sentence
written for this repository. This document says which is which, what the generator does to each on the way to
the page, and where the line between "read from a source" and "written here" is thinner than it looks. It is
derived from the generator as it stands, `diagrams/src/`; when the two disagree, the code is right and this
document is stale.

The short version: the reader posters (`diagrams/*.svg`) quote the blueprint and the formal proof; the map
posters (`diagrams/map/*.svg`) quote neither; everything else on both sets is either computed from the sources
at build time or written in the poster modules, and the build checks the computed parts, not the written ones.

## 1. Quoted from the blueprint's prose (reader set only)

The riemann-blueprint stores each statement as a Markdown file with TOML front matter, and most proofs as a
sibling `.proof.md`. The reader posters quote from these files:

| What | Where it is drawn | How much |
|---|---|---|
| A statement's body | the italic line of its card | the first two paragraphs, abridged to 620 characters (360 on a short card) |
| A statement's proof | the bullets of its card | up to four paragraphs (one on a short card), each abridged to 330 characters (240 short); a fifth bullet counts the rest |
| A chapter's introduction | R2's chapter cards, the subtitle of R4 to R8 | the first paragraph, abridged to 620 or 900 characters on R2 by card width, 700 on R4 to R8 |
| A section's introduction | band 3 of R3 to R8 | the first paragraph, abridged to 900 characters |
| The outline's list of stages | R2, "The five stages of the proof" | the five paragraphs the generator matches by their first word, each abridged to 460 characters |
| The outline's points to check | R2, "Points to check first" | up to six paragraphs of `rem-points-to-check`, each abridged to 420 characters |
| The interfaces section | F1, "The interfaces, in the outline's own words" | the first paragraph, abridged to 1100 characters |

Four transformations stand between the file and the page, all in `src/bp.py`:

- **Paragraphs.** The body is split at blank lines; a numbered or bulleted item becomes a paragraph of its own
  (`paragraphs`).
- **Markdown to rich text** (`rich`). A link written as `[some-id]` becomes the id in code font, so that a
  reader can find the statement it points to. Maths between dollar signs becomes a code run. Emphasis marks are
  dropped. Nothing is added.
- **LaTeX to Unicode** (`latex`). A table of about a hundred macros rewrites `\le` as ≤, `\to` as →, `\alpha`
  as α, `\mathbb{Q}` and `\Q` as ℚ, fractions as `(a)/(b)`, and strips `\mathrm`, `\operatorname`, `\left`,
  `\right` and spacing. Sub- and superscripts in braces become `_(…)` and `^(…)`. A macro the table does not
  know keeps its name without the backslash, so `\Sha` reads as `Sha`. This is enough to read a statement off a
  poster; it is not typesetting, and a reader who needs the formula as written should follow the blueprint link
  in the card's footer.
- **Abridgement** (`abridge`). Text longer than its limit is cut at the last sentence end (`. ` or `; `) before
  the limit, or at a word if no sentence end falls in the last two thirds, never inside a code run, and the cut
  is marked with ` …`. A card that shows an ellipsis is showing less than the blueprint says.

The subtitle of every reader poster says that its text is the blueprint's, abridged, and the footer of every
card gives the blueprint path. `NOTICE` records the CC BY 4.0 licence the blueprint's author granted for this prose on 2026.11.22, under
which the reader set quotes it, attributed.

## 2. Read from the blueprint's front matter and structure (both sets)

These values are data, not prose, and both sets draw them:

- the statement's **id**, **title**, **kind** (theorem, lemma, proposition, definition, remark, corollary),
  **provenance** (new, modified, published, or unmarked), **order**, and its **chapter and section**, which are
  its directory path;
- the **`uses`** list, split by the reader into uses that appear in the statement and uses that appear in the
  proof (`statement_uses`, `proof_uses`), from which every arrow, every "Stated with", "Proof uses" and "Used
  by" line, and every count of edges, depths and citations is computed;
- the **`source`** line of a published result, drawn in R2's literature table;
- the **`lean`** list, the declarations the blueprint says the statement stands for;
- chapter and section **titles** and **orders**, used as card titles and in the tables of F2 and F3;
- the provenance labels, which the legend explains in this repository's words. The blueprint site's provenance
  colours (`blueprint.toml`) are copied as constants into the Graphviz scripts under `graphs/`; the posters use
  the drawing library's own accents instead.

The map posters keep all of this. A map card carries the id, title, kind, provenance, chapter, Lean name and
location, every edge, and a count of the paragraphs the blueprint spends on the statement and its proof, in
place of the text.

## 3. Quoted from the formal proof

Two files beside the blueprint and three in the mirror are read:

- **`lean-facts.json`**, the blueprint's index of the 1194 declarations its statements name. The reader set
  quotes each declaration's **signature** verbatim into the card's Lean panel, wrapped at the panel's width and
  cut at nine lines (four on a short card, eight on R2's chapter cards), with a last line counting what was cut
  (`lean_block`). Both sets draw the declaration's **name**, **kind**, **module**, **file** and **line**; F3 is
  built from nothing else. One declaration in the index carries a docstring; it is not drawn.
- **`src/Main.lean`** and **`src/Statements.lean`** in the mirror: R1 draws the five theorem lines of
  `Main.lean` as written, in both sets, since each is one line naming a theorem, its `Prop` and its proof
  term; the reader set adds the `Prop` definitions of `Statements.lean` those lines are stated against. The
  reader parses both files and fails if `Main.lean` has a line it cannot read.
- **`comparator.json`** in the mirror: the theorem names, checked against `Main.lean`, and the permitted
  axioms, which R1 lists.

`NOTICE` records that the formal proof was published without a licence and that these quotations remain its
author's. The map set leaves the signatures out and keeps names and locations.

## 4. Written for this repository

Everything else is prose written in the poster modules, `src/d_*.py`, `src/chapter.py` and `src/trace.py`, by
the author of this repository, and it falls into three kinds.

**Framing.** Titles, subtitles, band headings, legend entries, the "How to read" cards, the short chapter labels
(Main theorems, Outline, Zero-free, Families, Theta, Heights, Sha, Galois, Literature), pill wording, footer
labels, and the caveats that no Lean was built and that a card says what a statement is, not that it is proved.
This is the posters' own voice. It describes the sources and the drawing; it does not describe the mathematics.

**Computed sentences.** Most sentences that contain a number are templates filled at build time: "24
definitions: 3 in Main theorems, …", "263 proof uses between new statements", "413 of 416 statements name a
declaration". The numbers are the blueprint's data counted by the generator, and they change when the pin
moves. A template's wording is written here; its values are not.

**Interpretations.** A few sentences say what the data shows, in words chosen at the current pin. Each one
is either computed, so that its wording follows the data, or guarded by an assertion that fails the build when
the data no longer supports it, so that a pin move forces the sentence to be re-read rather than leaving it
standing:

- F1, the tallest tower of definitions: computed. The sentence names the chain's two ends, their chapters and
  its height from the longest path among the definition edges.
- F2, the heaviest flows between chapters' new work: the two pairs and their counts are computed; the reading
  that follows them, "the families are built from what those two chapters prove", stands behind a check that
  the two heaviest pairs are still theta to families and heights to families (`HEAVIEST`).
- F3, "a statement that names two usually names a definition and a theorem": guarded by a check that that pair
  is the majority of the statements naming two declarations.
- R1, band 5, the seven cards on what has been checked of the formal proof, arranged by the four questions of
  the Xena post. They paraphrase the mirror's `verification/NOTES.md` (independent complete builds, compared
  with the author's checksums; Comparator's output still to be added) and three pages recorded in
  `src/checks.toml`: Sutherland's verification files, for the builds, the axiom audit, the kernels and the
  comparisons, and for what is still running; the Lean and Mathlib communities' joint statement, for its
  certificate and for the vetting of the statement; and the Xena post, for the four questions. The
  certificate card quotes one sentence of the joint statement, in quotation marks, with the three pages linked
  beneath it. The generator reads the notes and fails if they no longer hash to `NOTES_SHA256`, and reads
  `checks.toml` and fails if a page's recorded hash is not the one in `CHECKS_SHA256` (both in `src/bp.py`).
  The build cannot fetch the pages: `tools/check-sources.py` does, and with `--update` records a changed page,
  which stops the build until the cards are re-read against it. The last card, that no check covers the
  blueprint's edges or its words, is the posters' own reading.

The rule for these is that a reader should be able to tell them from quotations. A quotation is in italics or
in a Lean panel and its card links to the file it came from; an interpretation is in the posters' own voice in
a grey or amber card, and the build knows the fact it rests on.

**Links to the papers** (F4). The url each reference's title links to is this repository's data, not its
text: `src/papers.toml`, one entry per reference, looked up on Crossref and zbMATH on 2026.11.22 and settled
by hand where they disagreed, each entry saying how. The blueprint records the citation (author, title,
journal, year); it does not carry the link. The id beneath a title links to the blueprint's entry, so a
reader can tell the citation from the paper this repository found for it.

## 5. Derived relations the blueprint does not state

Two things on the posters are neither quoted nor written: they are inferred from the sources by the generator,
and the posters say so where they appear.

- **Dashed arrows** (R3 to R8). The proof text of a statement sometimes names a result of the same chapter,
  as `[some-id]`, that its `uses` list leaves out. The generator finds these with a regular expression over
  the proof file (`chapter.hypotheses`), draws them dashed where they keep the layout acyclic, and lists the
  rest. Each chapter module records the ones it expects, and the build fails if the blueprint now gives
  others. Whether such a result is a hypothesis of the Lean theorem or a missed edge, the generator cannot
  tell, and the card beside the grid says so.
- **Layouts.** Which card stands where is computed from the edges (R4 to R8, F1), the chapter order (R2, F2),
  or a shortest path (T1, T2); R3 is laid out by hand in its module. A layout is a reading of the argument, and
  the plan's risks section notes that a computed one can mislead.

## 6. What is not used

No text is fetched from the web at build time, no model generates text at build time, and no data outside the
two sibling checkouts and this repository is read. The generator uses the Python standard library only. The
drawing library, `src/lib.py`, is from the TOPAK diagram family and contributes no words. The fonts embedded in
every poster are subsets of Noto, and contribute none either.

Every poster's footer carries a sources line naming the files it read and a state line naming the commits of
both checkouts, so that any sentence on it can be traced to a file at a commit, or to a module in `src/`.
