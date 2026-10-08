# Rev674 / rev733 — editor replacement no-match template hygiene

Micromax has one shared replacement-template dialect for editor replacement
commands and regex substitution hostcalls: `$1`, `$name`, `${name}`, and
`$$`.  By rev732, the VM `re-sub` / `re-subn` hostcalls reported malformed
or missing replacement references as explicit invalid replacements even when the
pattern had no matches.  The editor side still had one leak: no-match regex
replacement commands could return `not found` before ever validating the
replacement template.

That made these failures depend on buffer contents instead of command shape:

- `replace 'z([0-9])' '$2'` could say `replace: not found`;
- `replaceall 'z([0-9])' '$2'` could say `replaceall: not found`;
- `qreplace 'z([0-9])' '$2'` could enter the no-match path instead of
  explaining that `$2` is invalid for a one-group regex.

Rev733 keeps the boundary deliberately small:

- matching edit paths keep validating with the real match object;
- zero-width matches still fail before replacement-template expansion;
- valid templates with no matches still report ordinary `not found`;
- invalid templates with no matches now report action-specific
  `invalid replacement` diagnostics before mutation or capture mode.

The trust rule is simple: a malformed replacement template is a command error,
not a property of whether today's buffer happens to contain a target match.
