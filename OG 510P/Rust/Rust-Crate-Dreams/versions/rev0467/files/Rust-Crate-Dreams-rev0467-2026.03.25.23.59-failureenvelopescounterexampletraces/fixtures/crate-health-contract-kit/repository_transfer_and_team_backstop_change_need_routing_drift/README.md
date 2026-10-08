# Repository transfer and team-backstop change need routing drift

This scenario protects a subtler stewardship change.

A repository transfer can preserve issues, pull requests, collaborators, stars, watchers, and redirects.
That still does **not** mean support continuity stayed identical.

After a transfer, a team backstop may widen, narrow, or change its effective owner class.
If CODEOWNERS or notification settings also change, the crate-health lane needs a `routing-drift.diff` artifact instead of a reassuring but shallow “repo transferred successfully” story.
