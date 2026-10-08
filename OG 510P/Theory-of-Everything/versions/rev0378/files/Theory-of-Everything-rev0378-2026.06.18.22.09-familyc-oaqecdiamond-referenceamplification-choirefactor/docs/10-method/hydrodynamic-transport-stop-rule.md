# Hydrodynamic, transport, and fluctuation-dissipation stop rule

`OQ-0104` blocks hydrodynamic overclaiming.

Forbidden move:

```text
effective fluid + equation of state + transport coefficient + FDT/KMS relation
= candidate-native recovery
```

Allowed move:

```text
route-local effective fluid row
+ declared variables
+ declared transport coefficient
+ declared fluctuation/noise relation
+ public carrier
+ rollback rule
= bounded route pressure only
```

Hydrodynamic and fluid/gravity arguments are useful because they create robust effective constraints.  They are dangerous when they are used to erase microscopic, public-record, observed-sector, or candidate-identity debts.
