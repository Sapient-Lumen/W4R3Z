# Hook handler counts (rev369)

Hook inspection is part of Micromax’s trust surface: future users, plugins, and
LLMs need to answer “what is wired here right now?” without mentally switching
between one dialect for empty hooks and a different dialect for populated ones.

Rev369 keeps this deliberately small:

- editor `showhook NAME` now starts with `hook NAME: N handler(s)`
- core hook source/help output now starts with `hook NAME handlers: N handler(s)`
- non-empty hook inventories keep the same prefix before the existing
  `handler#group@file:line:col` detail

That means hook inspection stays structurally honest whether a hook currently
has zero, one, or many handlers, while keeping the VM/editor boundary tiny and
fully inspectable.
