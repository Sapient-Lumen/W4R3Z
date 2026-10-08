# Scenario — Diplomat callback parameter is not a bidirectional trait surface

This scenario models a common reporting mistake: treating a limited callback-parameter feature as if it were a symmetric foreign-trait implementation lane.

Diplomat is intentionally unidirectional, and its types documentation says callback support in parameters is limited.
The receipt therefore needs to say that the callback surface is **limited** and should not be summarized as “full bidirectional callback support”.
