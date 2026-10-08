# rev0840 parent defect witnesses

`parent_effect_transition_locale_repro.cpp` reproduces the parent serializer's use of
ambient stream locale without compiling or invoking the corrected rev0841 code.

Under `std::locale::classic()` sequence 7000 is emitted as `7000`. Under a legal custom
`std::numpunct` grouping facet, the same parent-shaped streams emit `7_000` in both JSON
and signing input. The strict Python JSON parser rejects the grouped document, and the two
signing inputs are unequal.

The witness is source plus captured output; the compiled executable is deliberately not
packaged.
