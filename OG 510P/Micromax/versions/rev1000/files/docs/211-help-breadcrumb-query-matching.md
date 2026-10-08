# Rev269: docs heading queries should reuse breadcrumb context too

Rev266 and rev268 made the docs heading breadcrumbs visible in the live picker
world:

- `helpoutlinepick` groups heading rows by parent breadcrumb labels
- `helpnavpick` now reuses those same heading groups on its heading half
- prompt preview/status surfaces already reuse the same visible labels

There was still one small but real gap: **searching** did not understand those
breadcrumbs.

Before rev269, heading queries only ranked against the leaf heading title plus
small metadata like `h2` / `line:col`. That meant visible, human-obvious queries
like these could still fail:

- `Guide Links`
- `Guide Deep dive`
- `helpjump Guide Links`

That gap mattered most on pages with repeated headings like `Examples`,
`Overview`, or `Links`: the grouped picker already showed which parent section
each heading lived under, but the query path still forced users (and future
LLMs) to guess the exact leaf title alone.

Rev269 keeps the fix tiny and honest:

- the visible row shape stays the same: `[title kind menu info]`
- `help_outline_rows(query)` now ranks against hidden breadcrumb metadata built
  from the same heading scan the docs browser already trusts
- `helpnavpick` inherits that automatically because its heading rows already come
  from `help_outline_rows(query)`
- `helpjump QUERY` inherits it too, so direct command-bar jumps can use parent
  breadcrumb terms

Examples after rev269:

- `helpoutlinepick Guide Links` selects the `Links` heading under `Guide`
- `helpnavpick Guide Deep dive` selects the nested `Deep dive` heading row
- `helpjump Guide Links` jumps directly to that heading

This is still deliberately not a larger outline tree or richer docs AST.
It is one more small shared improvement that makes the live picker model, the
command-bar model, and future offline archive readers agree on the same visible
context.
