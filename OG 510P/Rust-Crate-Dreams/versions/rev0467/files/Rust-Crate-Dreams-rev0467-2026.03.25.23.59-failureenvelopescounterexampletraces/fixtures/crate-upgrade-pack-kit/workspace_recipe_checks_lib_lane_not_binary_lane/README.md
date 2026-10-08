# Workspace recipe checks library lane, not binary lane

Focus: the checked migration recipe passes for a library member, but the CLI/example/binary lane was not exercised.
This fixture exists to prove that a workspace upgrade pack must report package-subset fidelity instead of silently upgrading the claim to “the whole workspace migrated cleanly.”
