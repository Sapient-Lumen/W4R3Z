# `--manifest-path` plus local-config split

This scenario captures the class where the target manifest lives in one repo but the current working directory contributes a different local Cargo config.
The bundle should keep project selection and config influence separate.
