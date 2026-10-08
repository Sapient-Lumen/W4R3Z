# Record ingress after substrate return

`recordingress.py` is the first active DHT substrate gate after rev0099.

It joins substrate re-entry, the Python-owned record-plane oracle, parser evidence, validator evidence, admission evidence, record kind/scope, TTL/size limits, native-permission denial, and preserved negative memory before an incoming record is admitted.

The hard guess is that record acceptance is not one check. It is a chain of local permissions:

```text
substrate re-entered
+ Python record-plane oracle
+ canonical parse
+ Python validation/signature check
+ admission budget
+ no native parser/validator attempt
+ hard-negative memory preserved
    -> admitted record observation
```

rev0100 intentionally keeps untrusted-byte parsing and record truth in Python.
