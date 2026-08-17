# Big Sky AI public pages

This repository is the public GitHub Pages home for Big Sky AI experiments and
publications.

## Ralph

Ralph is a top-level Big Sky AI project at `ralph/`. Its landing page and
subpages are generated from `templates/` and `content/ralph-whats-new.toml`.
Raw chats, private QMD excerpts, phone numbers, and real names belong in the
private OpenClaw workspace—not here.

The former Weekly Ralph publication is no longer part of the public site.

After changing Ralph page content, run:

```sh
just check
```

The build writes:

- `ralph/index.html` — Ralph project landing page
- `ralph/how-it-works/index.html` — plain-English technology tour (from
  `templates/ralph-how-it-works.html`; subpages are declared in
  `RALPH_SUBPAGES` in `scripts/build_weekly_ralph.py`)
- `ralph/whats-new/index.html` — running changelog rendered from
  `content/ralph-whats-new.toml` (add an `[[entries]]` block with `date`,
  `title`, and Markdown `body`, then run `just check`; the landing page's
  "New" teaser shows the most recent entry automatically)
- `sitemap.xml` and `robots.txt` — regenerated from `SITE_URL` on every
  build so they can never go stale or point at the wrong domain

Production is served by Vercel (project `bigskyai`, team Big Sky AI) at
https://bigskyai.ai from the root of `main` — no build step; generated output
is committed. Use a branch and draft pull request for editorial review.
Merging the approved change publishes it. GitHub Pages remains enabled as a
legacy mirror so old lockhartheavyindustries.github.io links keep working;
canonical URLs point at bigskyai.ai.

## Ralph assets

Reusable public media lives in [`ralph/assets/`](ralph/assets/). Add collection
images under `ralph/assets/images/` and record their metadata in
`ralph/assets/manifest.json`.

## Analytics

Public HTML pages include the GoatCounter beacon for
`bigskyai.goatcounter.com`. Generated Ralph pages inherit it from their templates, and `just check`
verifies that every public page contains exactly one beacon.

## Public URLs that must remain stable

- `/ralph/`
- `/strummer/`
- `/powbot/`
