# SAM wire shadow script

`samwire.py` is a no-network harness. It does not open a SAM socket. It models a future integration boundary where HELLO, SESSION_CREATE, STREAM_CONNECT, STREAM_SEND, STREAM_CLOSE, and RECONNECT steps carry canonical `WireFrame` payloads.

The harness checks ordering, persistent destination stability, signed step freshness, frame/payload digest binding, and canonical wire validation before send.
