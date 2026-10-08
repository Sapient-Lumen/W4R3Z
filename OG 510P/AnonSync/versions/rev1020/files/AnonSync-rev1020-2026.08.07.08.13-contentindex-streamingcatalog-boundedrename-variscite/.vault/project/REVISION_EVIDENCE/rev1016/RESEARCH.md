# Rev1016 research

Primary references reviewed:

- Linux procfs documentation: https://docs.kernel.org/filesystems/proc.html
- Linux smaps_rollup ABI: https://docs.kernel.org/admin-guide/abi-testing.html
- Linux getrusage(2): https://man7.org/linux/man-pages/man2/getrusage.2.html

The retained design uses one bounded smaps_rollup read, treats PSS as proportional sampled evidence rather than ownership, binds PID to process start ticks, and reports that multi-process samples are sequential rather than an atomic global cutpoint.
