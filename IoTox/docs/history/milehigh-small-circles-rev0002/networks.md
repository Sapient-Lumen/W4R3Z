# Network stacks

IoToxmutorr currently implements only **Tox/native**. It retains architecture space for **Tox/I2P** and **Tox/Tor**, and keeps future direct I2P or Tor transports as separate application transport choices.

The Mutorr Cube is above these choices. It consumes stable member identities and emits a bounded neighbor plan; it does not open sockets or silently select routes.

```text
Mutorr namespace Cube
          |
application peer transport: Tox
          |
route: native                  [implemented]
       future I2P route        [reserved]
       future Tor route        [reserved]
```

Reserved routes fail explicitly. The current adapter enables toxcore UDP and local discovery defaults, but public bootstrap-node and relay configuration has not yet been added. This revision therefore does not claim a complete public-network deployment.

A future Cube connection scheduler should maintain only the namespace union of required neighbors, reuse an existing Tox friendship across namespaces, and apply bounded reconnect/backoff policy. Tox friendship must not be treated as namespace authorization.
