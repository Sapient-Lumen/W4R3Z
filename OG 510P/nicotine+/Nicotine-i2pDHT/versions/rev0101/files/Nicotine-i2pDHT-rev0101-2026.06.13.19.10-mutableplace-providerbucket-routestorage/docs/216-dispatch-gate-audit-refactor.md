# Dispatch gate audit after validator wall

rev0022 added parseguard and validatorwall. rev0023 added namespace policies. rev0024 adds the next seam: a payload that is parse-safe, signature-valid, namespace-valid, and role/kind-valid still needs a registered handler before expensive or dangerous work begins.

`gateaudit.py` models this post-validator dispatch gate. It catches:

- no observations,
- validator-wall failures,
- missing namespace handlers,
- missing message-kind handlers,
- missing payload-role handlers,
- same request-id conflicts with different object digests.

This is a refactor pressure surface, not a production dispatcher.

Important rule:

```text
Validation permits dispatch only when the local handler table agrees.
```
