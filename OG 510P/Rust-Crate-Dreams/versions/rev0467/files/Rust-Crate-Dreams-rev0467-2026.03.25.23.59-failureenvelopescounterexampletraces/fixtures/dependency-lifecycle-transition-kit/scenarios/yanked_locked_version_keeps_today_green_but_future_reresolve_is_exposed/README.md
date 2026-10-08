# Scenario: yanked locked version keeps today green but future re-resolve is exposed

This fixture keeps another lifecycle distinction visible:

- a yanked dependency may keep working for existing lockfiles,
- but that does not mean the same route is safely selectable in the future,
- so “our current release still builds” must not masquerade as “our transition posture is durable.”
