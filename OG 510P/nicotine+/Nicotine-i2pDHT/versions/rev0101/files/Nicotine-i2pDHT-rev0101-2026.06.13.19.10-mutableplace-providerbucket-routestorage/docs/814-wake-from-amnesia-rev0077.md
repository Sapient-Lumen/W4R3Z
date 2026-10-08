# Wake from amnesia — rev0077

The current public-summary path is now:

```text
summary send canary -> summary drain -> delivery witness -> settlement fence -> summary ACK ledger -> delivery archive -> summary prune fence
```

Remember the rule: delivered-looking evidence is not enough. The ACK must settle, the archive must preserve restart memory, and pruning must keep redaction/contradiction evidence.
