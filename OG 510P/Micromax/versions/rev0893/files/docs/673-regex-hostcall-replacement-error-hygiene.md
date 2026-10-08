# Rev673 / rev732 — regex substitution replacement-error hygiene

Micromax's editor replacement commands and VM regex substitution hostcalls share
the same replacement-template dialect: `$1`, `$name`, `${name}`, and `$$`.
The editor side already reports bad active references as explicit invalid
replacement templates before mutation.  Before rev732, the VM substitution
hostcalls still surfaced lower-level Python errors directly:

- `"abc" "(a)" "$2" "" re-sub` failed as a raw invalid group reference;
- `"abc" "(?P<x>a)" "$missing" "" re-subn` failed as a raw unknown group name.

Those messages were truthful, but they hid which part of the hostcall boundary
was wrong.  A caller should be able to tell the difference between an invalid
regex pattern, an invalid replacement template, and a substitution runtime
failure without knowing Python's exception taxonomy.

Rev732 keeps the change deliberately small:

- `re-sub` catches replacement-template expansion failures separately and
  reports `re.sub: invalid replacement: ...`;
- `re-subn` reports `re.subn: invalid replacement: ...`;
- the shared replacement-template formatter keeps diagnostics one-line and
  aligned with editor `replace`, `replaceall`, and `qreplace`;
- zero-width substitution preflight remains earlier, so invisible matches still
  fail before replacement expansion;
- invalid templates remain visible even when the pattern has no matches, so a
  typo cannot hide as an ordinary no-op.

The trust rule is simple: if a hostcall accepts the editor-aligned replacement
dialect, it should also use the editor-aligned failure language when that
dialect is malformed or names a missing group.
