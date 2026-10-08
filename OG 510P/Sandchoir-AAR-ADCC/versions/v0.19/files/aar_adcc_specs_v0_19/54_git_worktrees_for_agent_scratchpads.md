# 54 — Git Worktrees for Agent Scratchpads (v0.19)

You said: each agent gets a scratchpad for work outside the shared workspace.
Git worktrees are a cheap, robust way to do this *without nested sandboxes*.

## 1) Basic model
- canonical workspace = main worktree (the “shared truth”)
- each agent Ai gets a worktree:
  - `worktrees/Ai/` on branch `agent/Ai/<thread>`
- agents do experiments freely in their worktrees
- they export patch-shaped results back to the canonical lane (P#)

## 2) Why worktrees
- isolates index/HEAD per agent (reduces collisions)
- cheap to create/remove
- lets you run tests independently

## 3) Protocol integration
- A lease may grant integrator permission to merge from Ai’s worktree.
- Patch proposals should include:
  - worktree path
  - branch
  - a short patch summary
  - a verifier intent (what should pass)

## 4) Cleanup
- on thread completion, remove worktrees
- run `git worktree prune` to clean metadata
- avoid checking out the same branch in multiple worktrees; use per-agent branches

## 5) Lowest-hanging workflow
- agents “own” their worktree, not files
- integrator merges into canonical only after cheap checks pass

Patch application pipeline: see 70_patch_lane_git_apply_3way_and_rerere.md.
