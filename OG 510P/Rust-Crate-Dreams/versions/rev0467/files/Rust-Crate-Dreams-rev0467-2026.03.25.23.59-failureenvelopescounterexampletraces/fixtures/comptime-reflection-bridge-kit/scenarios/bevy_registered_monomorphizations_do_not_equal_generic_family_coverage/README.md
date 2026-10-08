# Bevy registered monomorphizations do not equal generic family coverage

This scenario exists to stop a bridge export from claiming that one populated `TypeRegistry` proves broad generic coverage.

`bevy_reflect` can register reflected types in a runtime registry, but generic types still require the desired monomorphized representations to be registered manually.
A bridge crate should therefore keep **runtime registry population basis** and **generic coverage scope** explicit.
