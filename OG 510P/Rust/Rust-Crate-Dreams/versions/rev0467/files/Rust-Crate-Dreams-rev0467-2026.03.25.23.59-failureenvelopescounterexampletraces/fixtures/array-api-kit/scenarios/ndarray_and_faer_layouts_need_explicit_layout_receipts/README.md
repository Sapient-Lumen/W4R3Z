# Scenario — `ndarray` and `faer` need different layout receipts

`ndarray` documents a row-major default order and also supports column-major and custom-stride shapes.
`faer` documents column-major matrix layout.
Those are both valid, but they should not collapse into one vague “dense matrix layout” claim.
