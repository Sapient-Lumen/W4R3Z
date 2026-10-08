# Workspace root default-members make lane-selection truth non-optional

This scenario freezes the distinction between **package-scope truth** and **lane-selection origin truth**.

A package-scope report can honestly say that only the library member was checked.
That is still not enough if the reason was simply that Cargo operated from the workspace root and used `workspace.default-members`.

The pack should say:

- the invocation subject was the workspace root,
- the workspace attached through `default-members`,
- which members were selected versus merely attached,
- and that the omitted member lane should not be over-read as an explicit maintainer exclusion or completed review.
