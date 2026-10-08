# rev0044 experiment matrix additions

New experiment family:

```text
public hard-frame margin screening
```

Question:

```text
Can public frame features predict whether branch rollouts will produce decisive action-counterfactual labels?
```

Inputs:

```text
historical audited candidate rows from rev0034/rev0035/rev0036/rev0038/rev0043
public hard-frame candidate pool
```

Outputs:

```text
margin-screen model
holdout evaluation
margin-ranked selected frames
online branch-racing labels
C++ transition shadow rows
```

Success should not be judged by one smoke run.  The useful metric is:

```text
decisive labels per 100 branch rollouts
```

and later:

```text
matched margin-screen vs baseline hard-frame queue agreement / enrichment
```
