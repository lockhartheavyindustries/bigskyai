# Repository coordination lifecycle

This repository participates in `agent-coordination/v1`. The private
`lockhartheavyindustries/agent-coordination` hub owns shared protocol evolution
and cross-repository routing; this local copy lets GitHub-capable agents work
safely when the hub is unavailable.

## Discover and claim

Before mutable work, read `.coordination/project.json`, `AGENTS.md`, and the
repository briefing. Search open issues and pull requests for overlap. Create
or accept an issue before editing; it must name the objective, boundaries, lead
and platform, branch, affected areas, dependencies, acceptance evidence,
external authority, and any decision needed from the owner.

Open `status:claimed` or `status:in-progress` issues are active leases. Use an
isolated branch or worktree, preserve unrelated work, and do not push directly
to the default branch. Record mutable lifecycle state in labels and dated
comments, not rewritten issue titles or bodies.

## Handoff and integration

Before pausing or changing agents, add a comment headed with the acting agent
and platform. Include outcome, branch/SHA, files, validation, verified and
unverified external surfaces, remaining work, risks, non-Git artifacts, and
next action; apply `status:handoff`.

Use a linked PR for integration. A blocking review resumes the same issue,
branch, and PR: move it back to `status:in-progress`, correct it, add
regression coverage when practical, rerun checks, resolve corrected threads,
and post a fresh handoff. Before closing, confirm review/checks, default-branch
reachability, required/deferred verification, and worktree disposition.

Repository access, an issue, PR, merge, or automatic deployment does not
authorize a manual deployment/promotion, environment, account, billing, domain,
credential, protection, or other external change. Those need separate explicit
owner scope.

## Hub-unavailable mode

An agent without hub access may inspect, test, review, or continue an existing
claim. It must not begin potentially overlapping mutable work, must disclose
the gap in the issue or PR, and must reconcile lifecycle state when access
returns.
