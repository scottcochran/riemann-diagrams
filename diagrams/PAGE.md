# The page behind the cards

In the light theme, the page of every poster is `#eeeeee`, 93% white, not white. This document records why
that number, how it was measured, and how to measure it again. It is derived from the measurement made on
2026.11.22 with `tools/measure-page.py`; if the posters change enough that the measurement moves, the number
in `diagrams/src/lib.py` (the `page` token) and this document move with it.

## Why not white

A poster is cards on a page. With a white page, the cards' white interiors and the page are the same colour,
and only the borders say where a card ends. The first alternative tried was an 80% grey, `#cccccc`, which
separates the cards well but reads darker than the page's contents: the cards float on a surface that is
heavier than they are. The rule adopted instead is that the page should match the average luminance of what
sits on it, so that the page is neither lighter nor darker than the poster as a whole, and the cards are set
off by their borders and their tints at the smallest contrast that still separates them.

## The measurement

The poster measured was R2, the chapter map, as committed at the time (`R2-chapters-2026.11.22.svg` with the
embedded fonts). The method, which `tools/measure-page.py` carries out:

1. Render the poster as it is, light theme, 1700 pixels wide.
2. Render it again at the same width with its full-page background rectangle painted a sentinel colour, pure
   magenta, which nothing on a poster uses. This render is a mask: a pixel that is magenta in it is page, and
   every other pixel is content, which includes the cards' interiors, text, arrows, tables and tints.
3. Over the content pixels of the first render, average the **relative luminance**: each sRGB channel
   linearised by the standard transfer function, weighted 0.2126 red, 0.7152 green, 0.0722 blue, and the mean
   converted back to an sRGB grey level. This is the perceptual average, the grey that looks as bright as the
   content does on average.
4. For comparison, average the plain sRGB channel values too.

The result on R2:

| | |
|---|---|
| Pixels | 1700 × 2126 |
| Page background | 31.1% of the pixels |
| Content | 68.9% |
| Mean relative luminance of the content | 0.855 |
| As an sRGB grey | 237.9, which is 93.3% white, `#eeeeee` |
| Mean sRGB value of the content, for comparison | 233.9, which is 91.7% white, `#eaeaea` |

The two measures agree to within a step. The perceptual one is the one that matches "as bright as the
content", so the page is `#eeeeee`. The choice was confirmed by eye on R2 rendered at 2400 pixels wide, against
the 80% render that preceded it.

## One number for every poster

The measurement was made on one poster and applied to all thirteen, in both sets. The posters share one
drawing library and one palette, so their content averages are close, and a page that changed shade from
poster to poster would make the set look like thirteen designs. R2 was chosen because it is the map of the
set, with a typical mix of full cards, a table and arrows; a chapter poster with more card interior would
measure a little lighter, a table-heavy one a little darker, and neither would move the grey by more than a
step or two.

## What changed in the generator

`diagrams/src/lib.py` has a theme token for every colour, written once as a presentation attribute for
renderers without CSS and once as a CSS custom property that switches under `prefers-color-scheme: dark`. The
page used the `bg` token, which the cards' interiors, panels and label boxes also use. The page now has a token
of its own, `page`, so that it can differ from the cards:

| Token | Light | Dark |
|---|---|---|
| `bg` | `#ffffff` | `#12151b` |
| `page` | `#eeeeee` | `#12151b` |

The dark theme is unchanged: its page and its cards were already different shades (`#12151b` against the
panels' `#1a1e26`), and the measurement was not repeated there. Everything else on a poster is drawn as before;
only the first rectangle of each SVG, the one that covers the canvas, changed colour and class. Every poster in
both sets was regenerated.

## Measuring again

```bash
uv run --with pillow tools/measure-page.py diagrams/R2-chapters-2026.11.22.svg
uv run --with pillow tools/measure-page.py diagrams/R5-theta-2026.11.22.svg --width 1200
```

The script needs `rsvg-convert` on the path and reads the poster's own SVG, so it measures the content against
whatever page the poster currently has: the mask is made by repainting the page rectangle, and the as-is render
contributes only the content pixels. A poster whose content measurement differs from 93% by more than a few
percent is a reason to look at the poster, not to change the page.

## Rendering a poster on the page

Browsers draw the SVG as it is. To make a PNG in the light theme, `rsvg-convert`, which ignores
`prefers-color-scheme`, renders the light presentation attributes:

```bash
rsvg-convert -w 2400 diagrams/R2-chapters-2026.11.22.svg -o R2.png
```
