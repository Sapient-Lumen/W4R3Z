# Scope qualifier fields

Rev0020 introduces a lightweight `scope_qualifiers` overlay for genomics records. It is intentionally not yet required by global schema.

Fields:

- `revision_added`: when the overlay was added.
- `phenotype_scope`: what phenotype or claim family the record actually covers.
- `ancestry_or_population_scope`: what population/ancestry/training-data/governance surface matters.
- `portability_caution`: what must not be generalized.

Future sessions may promote this into a cross-domain factor axis if it proves useful outside genomics.
