# foreign_callback_requires_explicit_unregister_or_drop_story

A crate accepts a foreign callback interface and may invoke it after the original registration call returns.

The important review lesson is that “supports callbacks” is not enough.
The lifecycle receipt must say whether callbacks are cloned, when they are freed, whether explicit unregister is required, and what happens if teardown races with a late callback or cancellation.
