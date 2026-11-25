---
name: linking-posters
description: "Links a set of generated posters to each other and to their pinned sources, so that every name, item, entry and count opens where it is drawn in full: stable anchors on what a link may open, links made only to anchors the committed manifest lists (a second run when anchors move), a target for every link, the source at the pinned commit and never a branch, and the target framed when it is opened (CSS :target in the SVG, hidden where CSS is not run). Ends with check-links.py passing on the built outputs and the links looked at in a browser. Use when posters are to be linked, a link lands on nothing or on the wrong place, a reader cannot see where a link went, or a new card, row or poster must be reachable. Not for what a poster checks (recording-expectations) or the links to papers (linking-papers)."
---

# Linking posters

A set of posters drawn from one source is one document cut into pages. A reader who meets a name on one should be
able to open it where it is drawn in full, and see at once where they landed. Links that are typed in drift as the
posters change; links that are generated, checked and framed do not.

To learn it, read `references/target-highlighting.md`: the markup and CSS of a framed target, how a halo is put
behind what it frames, and how to test it, with what failed on the way.

## Setup

Read `[build]` in `proof-posters.toml`: `outputs` and `manifests` are what is linked, and `rerun_marker` is how the
generator asks for the second run. Read `[links]` if there is one (`skills/README.md` gives its keys): whether every
link must name a target, the markup that must never reach an output, the address prefixes allowed besides the pinned
sources, and the classes that frame a target. Read the project's poster skill for its library's link markup.

## 1. Anchor what a link may open

- **Every card, row or block a link may land on gets an id**, and the id is made from the source's own key for the
  thing (a statement's label, an item's kind and number, an errata line), never from its place on the page. Then
  the id survives a change of layout, and a link from an older release still lands.
- **Ids are XML names** (`[A-Za-z_][\w.-]*`), unique within a poster. A dot is allowed in an id, but in a CSS `#id`
  selector it starts a class name: never select an anchor by `#id` in a style; use `:target` or `[id="…"]`.
- **Group what the anchor covers** (`<g id="…">` around the card and its text), so the browser scrolls to the whole
  of it and a style can frame it.
- **Give every poster a title anchor** (`top`), so that a link to the poster as a whole still has a target.

## 2. Make every link land

- **Three kinds of address:** a fragment on the same poster (`#id`); another poster by the relative file name it has
  in the tree, on the Pages site and among a release's flat assets alike (`R3-zero-free-<date>.svg#id`); a source
  file at the pinned commit (`…/blob/<commit>/path#L12`). Never a branch, never a search, never a page that moves.
- **Link only to what exists.** A poster learns another's anchors from the committed manifest, which the generator
  writes with every poster's anchors. A link is made only to an anchor it lists, and stays plain text otherwise. When
  a run moves any poster's anchors, the generator updates the manifest, prints the rerun marker (`NOTE …`) and exits
  1; the second run makes the links follow. If CI regenerates once and compares the result with the committed
  files, as it should, a manifest that was not regenerated fails there; if it does not, nothing catches a stale
  manifest but this second run.
- **Every link has a target** (`[links].require_targets`). A link to a whole poster opens its `top`. A count
  ("8 declarations", "Chapter 3 (4)") opens the list it counts: the one item's card when it counts one, else a block
  or row that names them, each of which links on. Where nothing yet lists what a count counts, add the list (a new
  block, or a new poster), and record what it draws as an expectation (recording-expectations).
- **The library must render every link.** A link written inside markup the library does not nest (a link inside
  bold, in one library) is drawn as its raw text. Put the markers that must never reach an output in
  `[links].unrendered`, and fail the build on them.
- **Ordinary text stays text.** Do not turn prose into links. Link names, labels, counts and ids, where the reader
  will look for them.

## 3. Frame the target

When a link opens, the target is scrolled to; on a poster as tall as these, the reader still cannot tell which card
it was. Frame it with CSS `:target`, which matches the element the address's fragment names:

- **A halo behind each anchored group**: a rounded rectangle drawn first in the group, sized to what the group drew,
  hidden by a presentation attribute (`opacity="0"`), and shown by the poster's own style while the group is the
  target (`g:target>.halo{opacity:1}`), pulsing a few times and then staying. CSS beats presentation attributes, so a
  renderer that runs no CSS keeps it hidden, and the poster looks as it did.
- **No pulse under reduced motion**: `@media (prefers-reduced-motion:reduce)` turns the animation off for the halo
  and the row, and leaves the frame shown.
- **A row frames itself**: `g.row:target>rect:first-child{…}` recolours the row's own background rectangle.
- **Leave room above**: `g[id]{scroll-margin-top:…}`, so the frame is not cut by the top of the window. Measured to
  work on a group in a standalone SVG in Chrome; untested in Firefox and Safari (the reference says how it was
  measured).
- **Where it works:** wherever a browser opens the SVG as a document: the Pages site, a release asset, a file. Not in
  GitHub's file viewer, which shows an SVG as an image, without its links or its style. Say so in the docs.

## 4. Check

```sh
python3 ${CLAUDE_SKILL_DIR}/scripts/check-links.py
```

It reads every output, parses it as XML, and fails on: a duplicate id; a link to an id that is not there, on the same
poster or another; a link to a file that is not an output; with `require_targets`, a link to a poster with no
fragment; a link out that is not at a pinned commit or an allowed prefix (or, without `[links].allow`, reports them;
a commit is recognised only in a GitHub `blob`, `tree` or `commit` address, so a pinned link on another host needs
an `allow` prefix);
any `[links].unrendered` marker; and, with `frame_classes`, a linked id with no frame. It ends with the links by
kind. Then look: open a few targets in a browser, and read `references/target-highlighting.md` before trusting a
headless capture of one.

## 5. The docs

A project that links its posters says how, in the doc that says what each poster checks: what links to what, the
anchor forms, the second run, and where the framing works. A count of links in a doc is written by hand: say so, or
compute it.

## Check before you stop

- Every link lands: `check-links.py` passes, and the generator's own check fails on a link to nothing.
- Every link to a poster names a target, and every linked id is framed.
- No link points at a branch; every link out is at a pin or an allowed prefix.
- A second run changes nothing, and `determinism.py` passes.
- A few targets were opened in a browser and seen framed.
