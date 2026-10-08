# Send fence restart memory

A send fence records that live-send permission and delivery witness evidence have agreed at one exact boundary.  It prevents a one-shot send permission from being reused after restart and prevents pending delivery from being pruned as if it were terminal.

The fence is local monotonic memory.  It is not consensus, not a remote receipt oracle, and not proof that a public record propagated.
