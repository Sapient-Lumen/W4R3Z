# Wake from amnesia — rev0079

You are in the delivered-summary export path.

Previous seam:

```text
summary ACK ledger -> delivery archive -> prune fence -> replay -> ACK closure -> summary export fence
```

Current seam:

```text
summary export fence -> summary export receipt -> summary import gate -> export retention audit
```

Remember the rule: a redacted export fence is not a receipt, import permission, or retention proof.
