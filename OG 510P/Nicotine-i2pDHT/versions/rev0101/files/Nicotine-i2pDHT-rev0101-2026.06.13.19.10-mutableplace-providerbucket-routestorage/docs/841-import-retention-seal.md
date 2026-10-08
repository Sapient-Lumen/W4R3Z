# Import retention seal

Import retention seal joins settled import, import archive, and export retention audit before later cleanup or cross-node handoff may treat the imported summary as durable.

The seal is not cleanup. It is a permission boundary before cleanup.

It preserves:

```text
summary import settlement digest
import archive digest
export retention audit digest
redacted summary memory
contradiction memory
accepted marker chain
family/path diversity evidence
```

The key failure this lane protects against is an import archive that looks locally valid while retention evidence or contradiction memory has silently been split away.
