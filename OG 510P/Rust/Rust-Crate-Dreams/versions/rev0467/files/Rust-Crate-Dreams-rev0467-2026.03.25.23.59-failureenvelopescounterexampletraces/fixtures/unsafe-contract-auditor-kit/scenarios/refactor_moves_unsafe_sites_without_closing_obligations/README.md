# refactor moves unsafe sites without closing obligations

This scenario models a refactor that extracts helper functions and changes the number and location of `unsafe` sites.

The key requirement is that the diff should not imply the obligation disappeared just because the block moved.
