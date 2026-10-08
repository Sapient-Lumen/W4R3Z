# manifest rename witness does not settle feature and behavior lanes

This scenario shows why `offramp-recipe.manifest.json` and `recipe-witness.report.json` should stay separate.

A Cargo.toml rename recipe can compile and pass tests on one matrix slice while still leaving feature-remap and behavior review open on other lanes.
