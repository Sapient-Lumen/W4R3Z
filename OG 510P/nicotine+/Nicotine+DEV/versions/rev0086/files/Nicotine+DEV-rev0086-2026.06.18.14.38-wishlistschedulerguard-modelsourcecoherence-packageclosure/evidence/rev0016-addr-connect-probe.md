# rev0016 ADDR-CONNECT-01 probe evidence

The full JSONL output is in `evidence/rev0016-addr-connect-probe.jsonl`.

## Harness design

The harness replaces `socket.socket` with `FakeSock`, records `connect_ex()` targets, and drives server-message handlers with packed `GetPeerAddress` and `ConnectToPeer` messages. It does not open real sockets.

## Summary

```text
lanes tested: 3
cases per lane: 9
pytest result: 9 passed per lane
```

### Confirmed in every lane

```text
GetPeerAddress pending local request:
  127.0.0.1:631      -> connect_ex attempted
  169.254.169.254:80 -> connect_ex attempted
  203.0.113.10:2234  -> connect_ex attempted
  192.168.1.24:2234  -> connect_ex attempted as compatibility baseline
  0.0.0.0:2234       -> no connect; offline baseline preserved
  198.51.100.20:0    -> no direct connect; side effects differ by lane

ConnectToPeer unsolicited server request:
  127.0.0.1:631      -> connect_ex attempted
  169.254.169.254:80 -> connect_ex attempted
  192.168.1.24:2234  -> connect_ex attempted as compatibility baseline
```

## Port-zero lane difference

```text
3.3.10 / 3.3.x:
  port 0 does not open a socket, but an indirect ConnectToPeer request is scheduled before direct-port rejection.

master:
  port 0 does not open a socket and the witness sees no extra handler-side indirect ConnectToPeer side effect.
```
