# Indented code-ish markdown

This page exists as **test data** for Micromax's tiny docs-browser indentation guards.

It exercises a small but real CommonMark rule: a few block starters may begin with up to three leading spaces, but **four spaces or a tab should stay code-ish prose** instead of becoming active docs-browser structure.

## Links and refs

- [Visible doc link](00-vision.md)
- [Ghost four-space reference][ghost-four-space-ref]
- [^ghost-four-space-footnote]
- [Jump to real setext heading](#real-setext-heading)

    [ghost-four-space-ref]: 94-softwrap.md
    [^ghost-four-space-footnote]: Four leading spaces should stay code-ish prose.

## Indented inline links stay prose

    [Ghost indented inline link](94-softwrap.md)
    <https://example.invalid/indented-not-a-real-help-link>

## Indented heading lookalikes

    # Four-space ATX heading stays prose

Real setext heading
-------------------

Micromax should keep the indented lookalikes above out of outline rows, fragment jumps, and docs-link resolution.
