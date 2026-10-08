# Scenario: foreign reexports and manifest SemVer need a loss report

Some downstream questions require facts that are absent from the target crate's rustdoc JSON.
This scenario keeps those absences explicit instead of treating normalization as lossless.
