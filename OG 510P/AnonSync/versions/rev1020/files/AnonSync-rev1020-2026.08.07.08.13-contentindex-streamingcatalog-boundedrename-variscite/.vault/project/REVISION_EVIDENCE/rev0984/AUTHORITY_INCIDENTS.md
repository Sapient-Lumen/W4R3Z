# rev0984 authority incidents

- Multiple unsealed source and build authorities existed; only the committed wrapper matched to the frozen source was retained.
- One GCC cache was contaminated by overlapping Ninja invocations and produced a missing-object failure; it was discarded.
- Cloudtainer cleanup removed build directories during validation; incomplete runs were excluded and fresh retained caches were used.
- A writer-lock race oracle was rejected because it blocked receipt publication before the intended cutpoint. The final oracle uses SIGSTOP after receipt publication and a free-page-expanded database to deterministically replace the candidate pathname after its retained image is sealed.
- Final documentation and two lexical audits changed after C++ compilation. The complete CMake/C++/header/test/third-party input set remained byte-identical to the frozen build source, and the changed audits were rerun as registered final-source tests.
