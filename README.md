# Big Sky AI public pages

This repository is the public GitHub Pages home for Big Sky AI experiments and
publications.

## Ralph and The Weekly Ralph

Ralph is a top-level Big Sky AI project at `ralph/`. Its landing page and The
Weekly Ralph issue archive are generated from the public issue source in
`content/weekly-ralph/`. That source must already be anonymized and approved
before it enters this public repository. Raw chats, private QMD excerpts, phone
numbers, real names, and unapproved media belong in the private OpenClaw
workspace—not here.

Create a new issue by copying the previous TOML file, incrementing `issue` and
`slug`, setting `published` to the date the issue is generated (preferably a
Monday), and replacing the editorial content. The public date is formatted
automatically from `published`. Then run:

```sh
just check
```

The build writes:

- `ralph/index.html` — Ralph project landing page and newsletter index
- `weekly-ralph/index.html` — issue archive
- `weekly-ralph/issues/<slug>/index.html` — permanent issue page
- `weekly-ralph/feed.xml` — RSS feed

GitHub Pages publishes from the root of `main`. Use a branch and draft pull
request for editorial review. Merging the approved change publishes it.

## Public URLs that must remain stable

- `/weekly-ralph/`
- `/ralph/`
- `/strummer/`
