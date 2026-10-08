# Risk register rev0084

Risks addressed:

- Native parser enthusiasm could bypass parseguard.
- Native leaf expansion could happen without sanitizer/fuzz posture.
- Runtime parity could be mistaken for permission to native-implement semantic surfaces.
- Python fallback could be dropped after native dispatch starts passing.

Risks still open:

- No production sanitizer runner exists.
- No production native ABI exists.
- No production fuzz harness exists for C leaves.
- No live I2P/SAM transport exists.
- No production DHT exists.
