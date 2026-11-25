# The tag message

The tag message opens the release notes, and it is what a reader of a cited poster reads first. It follows the
same shape every time.

```
vX.Y.Z: <what this release is, in one line a reader can cite>

<CLASS>: <the kind of move, in one sentence>. <Each pin: moved from A to B, or "stay" with their values>.
<Posters added or removed, or "No poster removed or changed">; <every EXPECTED and HYPOTHESES list unchanged,
or which changed>. The posters are dated <date>.

<A paragraph per change that matters to a reader: what it is, the numbers, where it comes from.>

Re-read: <the posters a reader must re-read, by id; or "nothing: the same statements and arrows, drawn again">.
```

Rules:

- **Plain and exact.** Give numbers, with the denominator ("275 of 289"). Name pins by name and value. No
  adjectives of praise, no "major improvements".
- **The first line after the title is the class and the move**, so that the class can be checked against the
  table without reading further.
- **Say what was not checked.** If a number is read from a file rather than checked by a kernel or a build, say
  so ("read from the export, not checked by a kernel").
- **The re-read line is required**, even when the answer is "nothing".
- **Wrap at about 72 columns**, as git shows it.
- No credentials, no internal hostnames, nothing private about anyone.
