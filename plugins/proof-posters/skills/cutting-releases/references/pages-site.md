# The Pages site

A release's page on GitHub lists its assets as downloads; a reader who opens a poster there gets a file, not a
drawing. A Pages site serves the posters of one release as `image/svg+xml`, so that a poster opens in the browser
and its links between posters work. This page is how to set one up so that it stays the release and nothing else.
riemann-diagrams' `.github/workflows/pages.yml` is the worked example; the pitfalls below say which project met each.

## What the workflow does

One workflow, `pages.yml`, called by the release workflow with the new tag and runnable by hand with an existing one:

- **`workflow_call` and `workflow_dispatch`, each with a `tag` input.** The release workflow calls it after the
  release exists (`needs: release`, with `pages: write` and `id-token: write`); a run by hand from the default branch
  publishes a release made before the site existed, or an older one back.
- **Two jobs, build and deploy.** Build checks that the run is the custodian's and that the tag has a release, checks
  out the tag, stages the posters at their paths in the tree with the release's metadata file and an index page, and
  uploads the artifact. Deploy publishes it.
- **The site is the release.** Before it uploads, build downloads the release's checksum file and metadata file and
  checks every staged poster against it (`sha256sum --strict -c`), and that the tag has no SVG the release lacks.
- **The site serves the tag.** After `deploy-pages`, the deploy job reads the metadata file from the live site, with a
  query string of its own so that no cache answers, and fails unless it names the tag. Set `[release].pages_url`,
  and `verify-release.py` checks the same thing afterwards.
- **An index**, for example the project's poster README at the tag rendered by GitHub's Markdown API, with each
  relative link sent to the site (a poster) or to the repository at the tag (anything else), and the list of the
  release's posters from its manifests.

## The settings, once

- **Pages from GitHub Actions:** Settings, Pages, Source "GitHub Actions", or
  `gh api -X POST repos/OWNER/REPO/pages -f build_type=workflow`. The answer gives the site's address and whether it is
  public.
- **The `github-pages` environment** must allow the default branch (for a run by hand) and the release tags (for the
  call from the release workflow), as custom deployment policies:

  ```sh
  R=repos/OWNER/REPO
  gh api -X PUT $R/environments/github-pages --input - <<<'{"deployment_branch_policy":{"protected_branches":false,"custom_branch_policies":true}}'
  gh api -X POST $R/environments/github-pages/deployment-branch-policies -f name=main -f type=branch
  gh api -X POST $R/environments/github-pages/deployment-branch-policies -f 'name=v*' -f type=tag
  ```

## Before enabling it

**A Pages site is public, even for a private repository**, unless the account has GitHub Enterprise Cloud's private
Pages. The API's answer says so (`"public": true`). Enabling it publishes the posters, the metadata file and whatever
the index renders to anyone. Ask the custodian first, say what will become public, and do not enable it on your own
judgment. The repository and its release pages stay as they were.

## Pitfalls

- **Build and deploy in one job** (riemann-diagrams, v0.2.0, three runs): `deploy-pages` looked for the artifact right
  after the upload and found none once it had grown to 5 MB. A job boundary waits for the artifact to be registered.
- **A deployment is named by its commit** (riemann-diagrams, v0.3.0): a second deployment at a commit that already
  has one does not replace the site, and still reports success. The deploy job's check of the live metadata catches
  it; the fix is a commit to the default branch and a run by hand from there with the tag.
- **A release made before the workflow existed** is not published by its own run, since the release workflow at its
  tag has no pages job. Run `pages.yml` by hand from the default branch with the tag; the build still checks out and
  checks the files at the tag.
- **The custodian check uses the actor.** A run by hand started with the custodian's own credentials (`gh workflow
  run pages.yml -f tag=vX.Y.Z`) passes it; one started by anyone else is refused, as it should be.

## Check after a deploy

`verify-release.py vX.Y.Z` with `[release].pages_url` set: the assets against the tree at the tag, the metadata file
naming the tag, and the site serving it. Then open the index and one poster, and check that the poster is served as
`image/svg+xml` (`curl -sI <url>`), not as a download.
