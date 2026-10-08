# Rematch worlds should choose shortest-script transport by state knowledge and branch exactness

The archive now has enough exact normalized half-step codecs that future inheritors should stop treating transport choice as ad hoc. For **shortest-script transport** there are only two questions that matter:

- does the decoder already know the exact feasible interval state?
- must the **exact noncanonical shortest branch** survive, or is deterministic canonicalization acceptable?

Those two booleans define a complete four-regime frontier on the current `17`-rank path.

## The exact frontier

If the exact noncanonical shortest branch **must survive**:

- when state is **unknown**, use the standalone **global exact-shortest-word prefix**,
- when state is **known**, use the **state-conditional local choice prefix**.

If deterministic canonicalization is acceptable:

- when state is **unknown**, transport the cheaper **interval-state prefix** and rebuild the canonical shortest script after decode,
- when state is **known**, transport **zero script bits** and rebuild the canonical shortest script directly from state.

## Why those four corners are exact on the current path

The archive revalidated the winning margins of the recommended codecs against the nearest admissible alternatives:

- standalone canonical shortest-script transport: `1121` bits total via interval-state prefix, beating the nearest admissible alternative (`1224`-bit fixed-width state transport) by **`103` bits** over the full `153`-script canonical catalog,
- state-known canonical shortest-script transport: **`0` bits** total via canonical reconstruction from known state, beating the nearest admissible alternative (`165` bits via canonical words routed through the state-conditional choice prefix) by **`165` bits**,
- standalone exact shortest-script transport: `4619` bits total via the global exact-word prefix, beating the nearest admissible alternative (`5130`-bit fixed-width exact-word transport) by **`511` bits** over the full `513`-word exact catalog,
- state-known exact shortest-script transport: `1350` bits total via the local choice prefix, beating the nearest admissible alternative (`1560`-bit fixed local-choice fields) by **`210` bits**.

So the inheritor should not search the codec menu anymore. The decision is already pinned by these two regime questions.

## Practical rule

For **script transport only**:

- known state + canonical okay → **send nothing**, rebuild canonical,
- known state + exact branch required → **send local choice prefix only**,
- unknown state + canonical okay → **send interval-state prefix**,
- unknown state + exact branch required → **send global exact-word prefix**.

If the goal is to preserve the **state itself** rather than any script view, fall back to the earlier interval-state transport law; that case sits outside this script-frontier pass.
