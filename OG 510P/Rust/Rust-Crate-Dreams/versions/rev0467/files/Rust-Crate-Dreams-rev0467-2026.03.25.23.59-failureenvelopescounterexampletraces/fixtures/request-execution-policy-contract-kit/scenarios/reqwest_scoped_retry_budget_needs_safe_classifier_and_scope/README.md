# Scenario — reqwest scoped retry budget needs safe classifier and scope

This scenario captures a client that uses `reqwest` retry support with a scoped policy.
The point is to keep three truths visible at once:

- replay safety comes from a safe classifier and HTTP/app semantics,
- retry budgets are scoped rather than global folklore,
- and serial retry budgets are not the same thing as parallel hedging.
