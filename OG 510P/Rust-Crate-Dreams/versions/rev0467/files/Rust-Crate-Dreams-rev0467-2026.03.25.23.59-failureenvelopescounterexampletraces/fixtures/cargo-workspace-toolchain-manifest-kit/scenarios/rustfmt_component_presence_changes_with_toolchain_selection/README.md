# rustfmt_component_presence_changes_with_toolchain_selection

A workspace expects `rustfmt` as a rustup component, but the selected toolchain changed from the repository toolchain file to an explicit `+nightly` route.

The important distinction is that the same command family now has different optional-component posture because toolchain selection changed.
