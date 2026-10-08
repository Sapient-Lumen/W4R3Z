# latest_docsrs_redirect_resolves_to_pinned_citation_locator

This scenario proves that a convenient docs.rs shorthand such as `latest` is useful for browsing but not sufficient as a review surface.

The receipt should resolve that shorthand to an exact version, keep the original fetched route visible, and mark the locator as `resolved_from_floating` rather than pretending it was pinned all along.
