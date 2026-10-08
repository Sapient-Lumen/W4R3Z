# Scenario — UniFFI foreign trait unexpected-error mapping must not stay implicit

This scenario captures a subtle but important completion/failure truth.

UniFFI says foreign-trait methods should return a compatible `Result`, and unexpected callback errors can be converted via `From<UnexpectedUniFFICallbackError>`. Without that mapping, generated code will panic.
