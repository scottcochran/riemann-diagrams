# Framing a link's target

A worked example, from riemann-masullo-diagrams (`diagrams/src/lib.py`, `draw.py`, `chapter.py`), where 45 posters
carry about 29,000 links with a target and 3,577 framed groups. The code here is the pattern; the project's own
library decides the names.

## The markup

A card a link may open is a group with the card's id, whose first child is its halo:

```xml
<g id="i-theorem-5.2.4.1">
  <rect x="…" y="…" width="…" height="…" rx="12" fill="#fdf3e4" stroke="#a35a00"
        class="rd-target ft-amber s-amber" stroke-width="3.5" opacity="0"/>
  <rect …/>        <!-- the card itself -->
  <text …>…</text>
</g>
```

- The halo is drawn before the card, so the card covers its middle and only a frame shows around it. It is a few
  pixels larger than the card on every side.
- `opacity="0"` hides it from a renderer that runs no CSS. The poster's style, which a browser does run, shows it.
- One `class` attribute: a library helper that writes `fill`, `stroke` and `class` together must not be combined with
  a second `class`. An XML parser fails on the duplicate; parse every output before writing it.

The halo's size is only known when the group is drawn. Keep the index where the group opened, and insert the halo
there when it closes:

```python
def anchored(c, anchor):
    c.add(f'<g id="{anchor}">')
    c.anchors.append(anchor)
    return len(c.out)                      # where the halo goes

def close(c, mark, x, y, w, h, pad=7):
    c.out.insert(mark, f'<rect … class="rd-target …" opacity="0"/>')
    c.add("</g>")
```

Nested groups work: an inner group's halo is inserted inside the outer group, after the outer one's mark.

A table row a link may open is its own group, and frames its own background rectangle:

```xml
<g id="row-117" class="rd-row"><rect …/>…cells…</g>
```

## The style

```css
.rd-target{opacity:0}
g:target>.rd-target{opacity:1;animation:rd-pulse 0.9s ease-in-out 3}
@keyframes rd-pulse{50%{stroke-width:9}}
g[id]{scroll-margin-top:90px}
g.rd-row:target>rect:first-child{fill:var(--amber-t);stroke:var(--amber);stroke-width:3;
  animation:rd-pulse 0.9s ease-in-out 3}
```

The frame pulses three times and stays while the address names it. A selector such as `g.rd-row:target>rect` is more
specific than the row's own colour class, so it wins without `!important`.

## Testing it, and what misleads

- **`:target` works in a standalone SVG.** Opened in Chrome at `poster.svg#i-theorem-5.2.4.1`, the page scrolls to the
  card and its frame shows.
- **A headless capture of a scrolled poster is not to be trusted.** `chrome --headless --screenshot` of a tall SVG
  opened at a fragment leaves the area above the target unpainted, and on a poster of 46,000 pixels it left the whole
  capture blank. The same happened with the posters from before the frames existed, and a capture with no fragment is
  whole: the capture fails, not the poster.
- **To test a frame without scrolling**, copy the poster with its `:target` rule rewritten to name one group, and
  capture the copy whole:

  ```sh
  sed 's/g\.rd-row:target>rect:first-child/g[id="row-117"]>rect:first-child/' poster.svg > test.svg
  ```

  Use an attribute selector. `#o-text-1.4.6--Ch03` would not match: the dots start class names in a selector, though
  they are legal in the id and `:target` matches the id as it is.
- **Every link to a poster must name a target.** A link to a whole poster opens its top and frames nothing, and a
  reader who followed "Chapter 3 (4)" from a card cannot tell where they are. Give every poster a `top` anchor, and
  make a count open the list it counts.
- **Links inside bold** were drawn as raw `[[@…|…]]` text by one library, which does not nest a link in bold: 19 rows
  of one poster, caught only by searching the output. Fail the build on the library's link markers in an output.
