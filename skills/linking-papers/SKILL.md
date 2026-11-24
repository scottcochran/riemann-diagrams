---
name: linking-papers
description: "Finds the stable link for each paper a bibliography cites and records it in the project's papers file: a DOI from Crossref checked against the DOI's own record, else zbMATH Open's record and the DOI or stable scan it links, else a stable scan chosen by hand with a note. Use when the build fails on a reference with no entry in the papers file, or on an entry that names no reference; when a new reference appears after a source moved; or when asked to add, fix or check a paper link. Not for the poster that draws the references (the project's own poster skill), and not for the source move that brought the reference in (moving-pins)."
---

# Linking papers

A bibliography entry records a citation, not a link. This skill finds the one stable URL a reader should land on
for each citation and records how it was found, so that the choice can be checked and repeated.

## Setup

Read `[papers]` in the project's `proof-posters.toml`. It gives the papers file, where the citations live (the
reference files of the source), the module whose build checks the two against each other, the command that
regenerates that poster, and the form of an entry. If there is no `[papers]` table, ask where the papers file is.

## Privacy

Send only the citation (its title, its authors' surnames and its year) to Crossref and zbMATH. Send nothing about
the project, and use the script's generic User-Agent. Do not add an email address to a request unless the user asks.

## Steps

1. **List what is missing.** Regenerate the checking poster. Its error names the references with no entry, and
   any entries with no reference. For each missing one, read its reference file: authors, title, journal, year,
   and any url field it already has.
2. **Search.**

   ```sh
   python3 ${CLAUDE_SKILL_DIR}/scripts/lookup.py --title "<title>" --author "<first author's surname>" --year <year>
   ```

   It prints Crossref's best matches, scored by title, and zbMATH Open's records for that author and year, with
   every link zbMATH holds. zbMATH often gives a title in English for a paper published in another language, so a
   low title score there is not a mismatch by itself. Compare the journal, the volume and the pages instead.
3. **Choose, in this order:**
   1. **Crossref** (`via = "crossref"`): the top match, if its title, an author and the year agree, after the
      check in step 4.
   2. **zbMATH** (`via = "zbmath"`): when Crossref has nothing, or matches the wrong paper. Take the record whose
      journal, volume and pages agree. Use the DOI it links if it has one. Otherwise use a stable scan it links
      (numdam, EuDML, arXiv), or the zbMATH record itself.
   3. **The source's own url** (`via = "blueprint"` or the project's word for it): when the reference file
      already carries a stable url, such as an author's PDF of an announcement.
   4. **By hand** (`via = "hand"`, with a `note`): when the two services disagree, or neither has the work. Look
      for a stable copy: the publisher's page, numdam, EuDML, arXiv, the Internet Archive, a society's archive
      (the Clay Institute holds Riemann 1859). The note says what was chosen and why.

   Never link to a search page, a personal page that may move, a paywall mirror or a preprint when the
   published version has a DOI.
4. **Verify a DOI against its own record** before recording it:

   ```sh
   python3 ${CLAUDE_SKILL_DIR}/scripts/lookup.py --verify <doi> --title "<title>" --author "<surname>" --year <year>
   ```

   It must say the record agrees with the citation. Crossref and zbMATH may differ by a year (online against
   print), which counts as agreeing. A DOI that does not agree is not used until the disagreement is understood:
   a wrong DOI looks correct on the page.
5. **Record** each entry in the papers file in the form `[papers].entry` gives, keeping the file's order (it is
   sorted by id). Write a DOI as a `https://doi.org/` url.
6. **Check:** regenerate the checking poster (`[papers].regenerate`), then the rest, and make sure no
   WARNING or ERROR is printed. Open each new link once (`curl -sIL <url> | head -1`) and confirm it resolves.

## Check before you stop

- Every reference has exactly one entry, and every entry names a reference.
- Every DOI was verified against its own record, and every `hand` entry has a note.
- No request carried anything but the citation.
