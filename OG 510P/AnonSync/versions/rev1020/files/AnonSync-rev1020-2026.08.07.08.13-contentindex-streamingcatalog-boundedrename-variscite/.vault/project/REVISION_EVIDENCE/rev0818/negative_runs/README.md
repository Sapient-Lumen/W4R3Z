# Retained development runs

The first cutpoint implementation declared `SyncAtomicFilePublicationError`
`final`. C++ `std::throw_with_nested` only synthesizes a wrapper derived from
the supplied type when that type is a non-final class. The initial corpus
therefore passed 87/96 checks but failed every nested-cause assertion.

The sequence is retained rather than overwritten:

- `cutpoint-test.log`: 87/96, exposing the final-class nested-cause defect;
- `cutpoint-test2.log`: 96/96 after correcting exception composition;
- `cutpoint-test-path.log`: 111/111 after adding component-walk and parent-rebind proof;
- `../validation/focused-cutpoint-direct.log`: final 133/133 after late-rebind,
  stale-typed-error, and temp-permission adversaries were added.

This evidence distinguishes corrected defects from assertions that were merely
weakened or deleted.
