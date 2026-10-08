# Facet SHAPE export is static shape, not runtime registry population

This scenario exists to stop a bridge export from pretending that a static shape source needs the same runtime-population story as a registry-backed source.

`facet` exposes a `SHAPE` associated const with layout, field, doc-comment, and attribute information, while `facet-reflect` adds runtime value views such as `Peek` and `Poke`.
A bridge crate should therefore keep **static shape export**, **runtime value mutation capability**, and **registry dependence** separate.
