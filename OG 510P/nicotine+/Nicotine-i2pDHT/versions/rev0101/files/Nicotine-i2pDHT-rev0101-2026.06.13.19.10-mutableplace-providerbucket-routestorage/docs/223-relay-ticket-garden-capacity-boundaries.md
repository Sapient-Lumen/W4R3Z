# Relay ticket garden-capacity boundaries

Garden nodes and relay-like helpers are mutual-aid capacity surfaces. They should be able to help with wake rendezvous, lookup relay, seed gates, provider probes, and witness queries without becoming authorities or unbounded metadata sinks.

`relayticket.py` adds short-lived signed tickets. A ticket is bound to:

- issuer key;
- relay node id and relay family;
- audience node id;
- purpose;
- target digest;
- scope id;
- sequence;
- nonce;
- time window;
- stream, byte, and metadata budgets.

A valid relay ticket is not proof that the relay is honest, that the target is true, or that the route is private. It is only a local admission object. The tests cover wrong audience, replay, scope mismatch, budget excess, time-window rejection, same-sequence ticket forks, and low relay-family diversity.

Design rule:

```text
A garden may give relay capacity, but the ticket must not let capacity become authority.
```
