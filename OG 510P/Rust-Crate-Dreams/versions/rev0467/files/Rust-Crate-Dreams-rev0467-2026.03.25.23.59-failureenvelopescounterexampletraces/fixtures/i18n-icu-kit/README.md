# i18n-icu-kit fixtures

This fixture family makes **P-0039 i18n-icu-kit** concrete as a support-contract lane instead of a vague “typed localization” claim.

The point is to keep four truths reviewable:

1. **message-argument schema truth** — what a public message actually accepts;
2. **locale-data profile truth** — compiled defaults, baked subsets, runtime providers, and mixed modes are not the same promise;
3. **formatter-coverage truth** — plain substitution, selection/plurals, and ICU4X-backed rich formatting are different support classes;
4. **fallback-witness truth** — requested locale lists, negotiation, and runtime fallback paths should be observed rather than guessed.

These fixtures are intentionally tiny.
They exist so future archive passes do not flatten “uses ICU4X / Fluent / typed messages / fallback locales” into one fake localization-support story.
