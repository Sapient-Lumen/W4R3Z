
# async_trait_boxed_service

A typical service/workflow trait family that still relies on `async-trait`.
The important fact is not merely that it works.
It is that the crate can hand another maintainer a compact statement of:

- the current recipe,
- the observed boxing/allocation posture,
- and whether a future native async-dyn migration would change the public promise or only the implementation recipe.
