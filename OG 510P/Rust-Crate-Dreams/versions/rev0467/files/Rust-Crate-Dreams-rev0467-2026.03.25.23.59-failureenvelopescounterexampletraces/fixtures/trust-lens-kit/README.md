# Trust Lens fixtures

This fixture family exists to keep **P-0017 Trust Lens** concrete.

The core claim is that trust posture should be a **reviewable bundle**, not a confusable-name warning by itself, not a registry badge collection, and not a single number.

## Core review objects

- `identity-risk.report.json`
- `signal-basis.report.json`
- `assumption-register.report.json`
- `review-debt.report.json`
- `notification-channel.report.json`
- `policy-decision.report.json`

## What these fixtures are trying to protect

They protect against flattening all of the following into one fake verdict:

- clean RustSec / Security-tab posture at capture time,
- Trusted Publishing posture,
- imported audit records,
- simple name-similarity warnings,
- and unresolved dangerous-effect or context-sensitive review work,
- and watch surfaces that cover different trust-change classes.

## Scenario families

### `typosquat_campaign_signal_forces_manual_review_even_with_clean_registry_surface/`
A graph can look ordinary at the registry surface while still containing a dependency name that is too confusable or campaign-adjacent to auto-approve.
The fixture keeps identity risk and policy posture explicit.

### `trusted_publishing_and_audit_import_do_not_erase_effect_review_debt/`
A graph can import some reassuring trust signals and still owe real human review.
The fixture keeps signal provenance, assumptions, and review debt distinct.

### `rustsec_rss_is_required_when_blog_posts_are_not_comprehensive/`
A team can watch the Rust blog and still miss routine malicious-crate removals if it is not also watching RustSec advisories/RSS.
The fixture keeps watch-channel coverage explicit.

### `security_tab_and_trusted_publishing_only_do_not_cover_malware_watch/`
Current crate-page security visibility and publishing-identity posture are both useful, but neither by itself is a complete malware-watch route.
The fixture keeps channel coverage and feed gaps explicit.
