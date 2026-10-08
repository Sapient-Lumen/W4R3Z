# Angle-wrapped links

This page exists to prove a tiny docs-browser affordance: **wrapped angle-bracket link destinations**.

- [Angle space path doc (inline dest next line)](
  <103-space path.md>)
- [Angle space path doc (inline title next line)](<103-space path.md>
  "tiny wrapped title")
- [Angle space path doc ref (dest next line)][angle-space-path-doc-multiline]

[angle-space-path-doc-multiline]:
  <103-space path.md>
  "tiny angle title"

Tiny policy:
- keep this conservative and editor-facing
- reuse the same shared destination parser as single-line inline links and wrapped reference definitions
- allow wrapped angle-bracket destinations where CommonMark already allows wrapped whitespace around the destination/title
- still require whitespace between a closing `>` and any optional title
