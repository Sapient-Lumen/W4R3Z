# Scenario: embedded pinned field needs inner and outer commit truth

A parent struct embeds a structurally pinned field. Review needs to know both when the field itself becomes address-stable and when the outer object is considered committed/published.
