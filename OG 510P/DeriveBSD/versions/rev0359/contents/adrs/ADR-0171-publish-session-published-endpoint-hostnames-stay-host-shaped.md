# ADR-0171: Publish-session published-endpoint hostnames stay host-shaped

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0165 fixed the high-level endpoint family for `net.publish.session` by deciding which lanes carry `hostname + port` and which do not.
ADR-0169 then made `relay-url` `url_hint` / `path_prefix` serialize that same canonical tuple, and ADR-0170 kept the local-source URI hint subordinate to the loopback-only source boundary.

That still left one smaller but practical ambiguity inside the canonical tuple itself:

**what stops `published_endpoint.hostname` from quietly carrying a URL, a host:port pair, a path, or a local-only name even though the archive already treats it as the typed host half of the published endpoint?**

Without one more narrow decision, a receipt can still claim it has a canonical `hostname + port` endpoint while the `hostname` field itself smuggles `https://...`, `host:443`, `/path`, `localhost`, or loopback text. That would force support, CLI, UI, and later implementation to reopen the same endpoint parsing questions the archive has already spent several rounds shrinking.

DeriveBSD does not need a provider registry or richer endpoint object here, but it does need one coherent rule for what the existing `published_endpoint.hostname` field is allowed to contain.

## Decision

1. `published_endpoint.hostname` remains the canonical host token for the `relay-url` and `reverse-forward` lanes.

2. If present, it must stay a **lowercase host-shaped token**, not a serialized authority or URL.

3. If present, it must therefore **not** carry:
   - a scheme,
   - userinfo,
   - an explicit port,
   - a path,
   - query or fragment material,
   - brackets or other URL-authority decoration.

4. If present, it must stay **non-local**:
   - not `localhost`,
   - not a name under `.localhost`,
   - not a loopback IP literal.

5. The field is intentionally kept **DNS-host-shaped** for now: dot-separated lowercase labels with ASCII letters / digits / hyphen, so copy surfaces and diffs do not have to normalize case, brackets, or ad hoc URL syntax.

6. This ADR still does not standardize provider-owned relay domains, custom DNS posture, internationalized names, or richer typed endpoint objects.

## Consequences

- The canonical published-endpoint tuple now has a real host token instead of an arbitrary string that can smuggle another endpoint grammar inside it.
- `published_endpoint.hostname` complements ADR-0170 cleanly: the source hint stays loopback/local, while the published host token stays non-local and host-shaped.
- Support/UI/export surfaces can show the published host without reparsing or stripping URL syntax.

## Alternatives considered

- **Leave `published_endpoint.hostname` free-form.** Rejected because that would preserve one of the last cheap ways for endpoint drift to re-enter the receipt.
- **Allow full URL authority strings in `hostname`.** Rejected because the archive already chose `hostname + port` as the typed floor; embedding `:port` or brackets back into `hostname` would re-collapse that separation.
- **Design a richer typed endpoint object now.** Rejected as premature.
