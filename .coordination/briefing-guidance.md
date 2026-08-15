# Repository briefing guidance

Keep a current repository-native briefing at the manifest's `briefing` path.
It should state the product purpose, current priorities, source/runtime
boundaries, validation entry points, external authority limits, and durable
decisions an agent needs without relying on a local computer or prior chat.

Do not copy secrets, credentials, private keys, or private account exports into
the briefing. A commit proves source state, not deployment or external account
state; record external verification with a date and method in the owning
repository.
