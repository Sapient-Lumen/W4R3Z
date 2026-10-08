# Scenario: classpath loader needs ALL-UNNAMED but docs omit it

The Java side uses restricted native loading from the class path, but package docs do not declare the resulting `--enable-native-access=ALL-UNNAMED` posture.
A user may see warnings or future hard failures even though the native library itself is present.
