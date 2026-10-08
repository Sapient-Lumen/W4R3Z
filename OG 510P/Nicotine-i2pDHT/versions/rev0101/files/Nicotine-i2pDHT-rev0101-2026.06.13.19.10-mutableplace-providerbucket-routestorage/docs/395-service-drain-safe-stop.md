# Service drain and safe stop

`servicedrain.py` models garden service stop/retirement as a side effect.  A service cannot stop safely just because an operator wants to stop, a withdrawal exists, or a catalog expires.

The drain gate looks at:

- in-flight tickets, relay work, and handoff work;
- matching receipts for ticket work;
- accepted withdrawal/retirement evidence;
- public announcements that are still live;
- protected service work that should not be interrupted;
- hard-negative memory that must not disappear during drain.

Useful refusal can close work, but it does not become proof of completed work unless the item state says so.  Public exposure and protected work are intentionally conservative.
