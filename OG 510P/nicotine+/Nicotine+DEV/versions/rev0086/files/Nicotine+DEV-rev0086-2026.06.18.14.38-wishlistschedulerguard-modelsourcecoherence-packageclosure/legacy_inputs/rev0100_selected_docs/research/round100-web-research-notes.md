# rev0100 web research notes

Searches performed:

- `site:github.com/nicotine-plus/nicotine-plus/issues lifecycle retry shelf priority main-thread queue`
- `site:github.com/nicotine-plus/nicotine-plus/issues "file-connection-closed" "queue"`
- `site:github.com/nicotine-plus/nicotine-plus/issues "peer-message-unsent"`
- `site:github.com/nicotine-plus/nicotine-plus/issues "SimpleQueue" "emit_main_thread"`

Result:

No exact public issue was found for priority admission inside a lifecycle retry shelf, or for priority cleanup/rollback events being unable to displace ordinary preserved payload/request retries.

Relevant overlap found:

- Broad connection-closed/connectivity reports, including nicotine-plus/nicotine-plus#2978.
- Broad queued-download/transfer-stall reports, including nicotine-plus/nicotine-plus#2926 and #3320.
- Broad freeze reports, including nicotine-plus/nicotine-plus#2700.

Upstream source check:

- Current upstream `pynicotine/slskproto.py` still uses `SimpleQueue` for network-thread queueing and a direct parsed-message/main-thread bridge shape.
- Current upstream `pynicotine/events.py` still exposes the event bridge surface, without the cube's bounded lifecycle retry shelf.

Conclusion:

rev0100 is best presented as an exact hardening-layer design invariant, not as a new broad freeze/transfer/connectivity symptom.
