# Risk register rev0073

Main risks tested:

- raw boundary or payload leakage through summary publication
- one component accepting a digest that another component did not bind
- redaction being assumed from publication rather than witnessed
- import/archive/prune memory splitting away from redaction/publication memory
- replay, rollback, same-sequence fork, and previous-link failures
- contradiction memory being dropped during publication or audit
- one-family witness/publication monoculture

Nonclaims remain explicit: this is a Python design lab with no live network side effects.
