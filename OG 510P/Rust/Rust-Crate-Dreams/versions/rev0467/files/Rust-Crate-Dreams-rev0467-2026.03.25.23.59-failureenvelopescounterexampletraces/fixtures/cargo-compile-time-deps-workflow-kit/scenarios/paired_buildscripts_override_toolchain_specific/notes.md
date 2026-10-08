# paired_buildscripts_override_toolchain_specific

This scenario exists to keep the crate from treating override commands as purely negative.

A toolchain-specific override can be the correct fix, but the bundle should still record that both check and build-script lanes were intentionally paired.
