# Wake from amnesia — rev0078

Start here after forgetting the current line:

```text
rev0076 summarydrain / deliverywitness / settlementfence
rev0077 summaryackledger / deliveryarchive / summaryprunefence
rev0078 summaryreplay / ackclosure / summaryexportfence
```

The key memory is that delivered-summary ACK evidence is not safe merely because it settled once. It must replay after restart, close locally, and fence any redacted export without dropping contradiction or redaction memory.
