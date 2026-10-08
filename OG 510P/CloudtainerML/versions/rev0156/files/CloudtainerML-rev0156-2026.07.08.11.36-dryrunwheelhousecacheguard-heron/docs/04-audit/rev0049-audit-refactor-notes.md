# rev0049 audit/refactor notes

Refactor target: the trace gate claim boundary.

Before rev0049, row metadata could derive `public_pretrained_trace_loaded` from the presence of an external NPZ. That was too permissive. rev0049 separates:

- `external_trace_loaded`;
- `public_pretrained_trace_loaded`;
- `declared_public_pretrained_trace`;
- `accepted_as_public_pretrained_trace`.

The new audit fails if arbitrary external fixtures produce public/pretrained row labels.
