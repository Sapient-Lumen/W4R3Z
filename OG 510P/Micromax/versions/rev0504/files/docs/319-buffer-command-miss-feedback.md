# Rev377: buffer/close named-buffer misses fail plainly

Small trust-first follow-up: `buffer NAME` and `close NAME` used to fail as a bare `no such buffer: NAME`, which hid the command family exactly when a human or future LLM was trying to understand whether the miss came from a navigation command or a close request.

Rev377 keeps the behavior change deliberately tiny:

- `buffer NAME` now fails as `buffer: no such buffer: NAME`
- `close NAME` now fails as `close: no such buffer: NAME`
- successful `buffer` / `close` behavior stays unchanged

This keeps named-buffer navigation and close misses in the same plain-spoken, typed dialect as the recent `showcmd` / `showword` / `showkey` / `help` / `see` / `where` cleanup work.
