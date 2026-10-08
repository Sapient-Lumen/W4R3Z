# env string then wrapped secret must not masquerade as protected source path

This scenario captures a common application pattern:

1. read a secret from an environment variable,
2. parse or deserialize it into an ordinary `String` / buffer,
3. only then wrap it in `secrecy::SecretBox<T>` or `SecretString`.

That is still better than leaving the value as an ordinary string forever, but it is **not** the same thing as a direct protected-memory import path.
