# missing_sysroot_src

This scenario exists to keep the crate honest about source assumptions.

The right output is not “everything is fine because cargo check ran”.
The right output is a concrete degraded-capability diagnosis plus a concrete fix.
