# Future const-reflection values do not imply runtime mutation surface

This scenario exists to stop future Rust reflection experiments from being overclaimed as a drop-in runtime reflection framework.

The current Rust project goal is explicitly about `const fn`-based compile-time reflection that produces const-eval values and does not yet put types back into the type system.
A bridge crate should therefore keep **compile-time-only export posture** separate from any runtime registry or mutation story.
