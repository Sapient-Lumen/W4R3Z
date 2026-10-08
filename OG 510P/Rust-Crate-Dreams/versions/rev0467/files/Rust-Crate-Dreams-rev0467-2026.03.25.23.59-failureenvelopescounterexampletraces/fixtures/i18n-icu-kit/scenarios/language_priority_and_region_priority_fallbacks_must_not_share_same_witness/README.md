# Scenario: language-priority and region-priority fallbacks must not share same witness

This scenario keeps locale fallback witnesses honest.

ICU4X exposes different fallback priorities, so one requested locale can legitimately resolve along different paths depending on whether the application prioritizes language retention or region retention.
That difference should stay reviewable rather than hidden behind a generic “has fallback” claim.
