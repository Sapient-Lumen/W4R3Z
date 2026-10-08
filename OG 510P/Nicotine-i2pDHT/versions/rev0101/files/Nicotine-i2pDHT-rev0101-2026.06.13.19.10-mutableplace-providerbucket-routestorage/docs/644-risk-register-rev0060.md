# Risk register rev0060

- A watchful retry canary might be mistaken for terminal send permission.
- A payload budget overrun might leak more public metadata than intended.
- Endpoint/session/Destination drift might send the right payload through the wrong path.
- Delivery acknowledgements might replay or fork.
- Restart may erase pending delivery and treat it as terminal.
