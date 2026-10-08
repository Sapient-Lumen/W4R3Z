# Embedded manifest defaults need authority, not guessing

A single-file package can omit `package.edition` and let Cargo infer it while still carrying explicit dependency frontmatter.
The capture must keep explicit, defaulted, and rejected fields separate.
