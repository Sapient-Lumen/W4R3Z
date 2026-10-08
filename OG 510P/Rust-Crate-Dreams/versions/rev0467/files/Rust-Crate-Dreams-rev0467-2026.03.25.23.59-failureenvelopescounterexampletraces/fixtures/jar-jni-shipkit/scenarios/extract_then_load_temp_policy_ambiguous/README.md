# Scenario: extract then load temp policy ambiguous

The package embeds a native library inside a JAR and extracts it at runtime before loading it.
The extraction destination, cleanup policy, and filesystem assumptions are not clearly declared, so residency and support posture remain ambiguous.
