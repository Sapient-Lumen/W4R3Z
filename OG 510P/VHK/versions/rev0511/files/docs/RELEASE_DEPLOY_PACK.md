# Release deploy pack

`vhk gen-release-deploy-pack` is the bridge between release-lane planning and a
real Linux shipping story.

It consumes:
- release lanes
- target-route comparisons
- setup/toolchain package hints

It emits:
- lane-native deploy styles
- generated artifact subsets
- copy-ready install/autostart snippets
- a short refresh script for maintainers

Read it when the question is no longer "which desktop lane is the flagship?"
but "what files/commands/docs should actually travel with that lane?"
