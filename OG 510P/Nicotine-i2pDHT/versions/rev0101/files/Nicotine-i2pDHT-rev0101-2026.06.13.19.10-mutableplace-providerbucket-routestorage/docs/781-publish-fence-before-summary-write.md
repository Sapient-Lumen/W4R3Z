# Publish fence before summary write

`publishfence.py` joins summary outbox staging, redaction archive memory, and import-prune audit before a future live/public summary write can treat the edge as ready.

The fence is deliberately no-network.  It keeps the DHT cube one step short of live I2P/SAM side effects while still making the next side-effect boundary explicit and testable.

publish fence lower-case audit needle.
