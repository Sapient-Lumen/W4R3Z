
# Inactive target edge keeps build green but metadata floor is higher

This scenario exists to show that command-family truth can diverge even when the main build lane stays green.

What should happen:
- `build` for the shipped target remains supported at the policy floor,
- `metadata` needs something newer,
- the report names the divergence explicitly,
- and the lane does not overclaim that the product build itself is broken.

The point is not to punish mixed target graphs.
The point is to stop “cargo build works” from masquerading as “all workspace tooling is supported at this floor”.
