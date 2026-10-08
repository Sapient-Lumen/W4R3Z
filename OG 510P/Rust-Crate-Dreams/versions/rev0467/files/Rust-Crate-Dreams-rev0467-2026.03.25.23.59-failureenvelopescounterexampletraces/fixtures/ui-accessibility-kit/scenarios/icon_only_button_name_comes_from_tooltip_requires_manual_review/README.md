# Scenario — icon-only button name comes from tooltip and requires manual review

An icon-only button appears to have a usable label only because a tooltip string currently mirrors the intended action text.
That can be acceptable in some toolkit/application patterns, but it is fragile and should not be silently treated as a fully automatic pass.

The right artifact here is a **rule-authority policy** that keeps this rule in a semi-automatic or manual-review lane unless the toolkit can prove the name source is stable and intentional.
