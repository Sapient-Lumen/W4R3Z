# Scenario — campaign policy excludes `match` arms until upstream support arrives

This scenario protects against silently treating unsupported constructs as if they were merely absent from the codebase.

The current Rust branch-coverage limitations issue still leaves individual `match` arms and or-patterns unsupported.
A serious campaign therefore needs an explicit `campaign-policy.receipt.json` showing whether those constructs are excluded, tolerated with caveats, or routed to manual review.
