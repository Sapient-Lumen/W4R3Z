# Compile Iteration Feedback Kit — generation-boundary reminders (2026-03-23)

When future passes deepen **P-0537** again, keep these truths separate:

1. **activation boundary** — when fresh code becomes reachable on some route;
2. **generation witness** — what evidence identifies the code epoch of a route;
3. **stale-code residency** — whether older code may remain reachable;
4. **mixed-generation risk** — whether old and new generations may coexist across routes;
5. **state continuity** — what state survived, migrated, reset, or re-instanced.

Do not let any of the following masquerade as a complete answer by themselves:

- “the dylib reload finished,”
- “the latest function pointer is in the jump table,”
- “`ptr_address` changed,”
- “the app visibly updated,”
- “the load counter increased,”
- or “the hot function was called once.”

A pass may truthfully show a successful patch, a visible UI update, and preserved state while still lacking an honest answer to:

- which callbacks/tasks remain on older code,
- whether unchanged functions can be distinguished from merely re-pointed ones,
- whether one route switched while another route did not,
- and whether the process is now homogeneous or mixed-generation.
