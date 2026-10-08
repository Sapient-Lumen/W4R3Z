# Defect: integration tests could not deterministically cover syscall failures

Real-process tests exercise successful lifecycle transitions and observable
race windows, but they cannot reliably force exact sequences such as `EINTR`
then success, `ECHILD` after observation, `EPERM` during group signaling, a
foreign `si_pid`, or an impossible zero return from blocking `waitpid`.
Consequently, source structure carried more proof burden than it should.

Rev0836 adds a GNU/Clang Linux linker-wrap oracle for `kill`, `waitid`, and
`waitpid`. Twelve deterministic scenarios execute 24 assertions over pending,
completion, retries, hard failures, identity mismatch, consume-before-syscall
cleanup, and move transfer. Calls fall through to the real libc functions when
no script is armed, allowing the same binary to coexist with sanitizer runtime
machinery.
