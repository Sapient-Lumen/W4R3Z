# Native call hold

`nativecallhold.py` models the next dangerous pressure: after re-entry and revalidation, a caller may want to run the native leaf.

rev0092 says no. The accepted path is `accept_call_held_on_python_fallback`:

- the native call is held;
- the native call is not allowed;
- the native call did not execute;
- the Python fallback/oracle did execute;
- re-entry and revalidation memory are carried forward.

This gives us a place to test call-boundary drift without letting the native line silently become runtime authority.
