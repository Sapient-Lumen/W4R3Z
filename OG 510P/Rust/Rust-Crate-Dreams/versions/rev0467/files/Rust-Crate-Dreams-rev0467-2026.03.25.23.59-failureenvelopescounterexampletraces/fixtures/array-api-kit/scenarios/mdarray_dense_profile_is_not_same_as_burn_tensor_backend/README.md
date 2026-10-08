# Scenario — dense arrays and backend-generic tensors need distinct semantic profiles

`mdarray` documents dense multidimensional arrays with static/dynamic dimensions and view types.
`burn` documents tensors generic over backend and tensor kind.
Those are both important, but they should not share one semantic profile unless the claim is deliberately narrowed.
