# Scenario: `async-channel` competing receivers claim each message once

This scenario exists to prove that **multiple receivers may exist** while each message is still claimed by **only one** of them.

Current docs say `async-channel` is an async MPMC channel where each message can be received by only one of all existing consumers.

The fixture should fail any classifier that turns “MPMC” into broadcast fanout or assumes cloned receivers all see the same send.
