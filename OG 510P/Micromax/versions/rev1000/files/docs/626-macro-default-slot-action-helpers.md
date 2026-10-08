# Rev685 - centralize tiny default-slot action wording

Micromax's macro surface now uses a coherent little action dialect around the default `last` slot: `play default slot`, `record default slot`, `overwrite default slot on save`, and `default slot empty`. Those phrases show up in exact slot rows, count rows, and bare play/record root rows.

Rev685 keeps the follow-up deliberately small and structural. New helpers now own the default-slot play/record wording once, and the exact/root macro surfaces reuse them instead of repeating the strings in parallel. Visible behavior stays the same; the goal is simply to make future wording changes less drift-prone for humans and LLMs maintaining the archive.
