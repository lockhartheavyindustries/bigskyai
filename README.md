# Big Sky AI public pages

This repository is the public GitHub Pages home for Big Sky AI experiments and
publications.

## The Weekly Ralph

Public issue source lives in `content/weekly-ralph/`. It must already be
anonymized and approved before it enters this public repository. Raw chats,
private QMD excerpts, phone numbers, real names, and unapproved media belong in
the private OpenClaw workspace—not here.

Create a new issue by copying the previous TOML file, incrementing `issue` and
`slug`, and replacing the editorial content. Then run:

```sh
just check
```

The build writes:

- `weekly-ralph/index.html` — issue archive
- `weekly-ralph/issues/<slug>/index.html` — permanent issue page
- `weekly-ralph/feed.xml` — RSS feed

GitHub Pages publishes from the root of `main`. Use a branch and draft pull
request for editorial review. Merging the approved change publishes it.

## Public URLs that must remain stable

- `/weekly-ralph/`
- `/strummer/`
