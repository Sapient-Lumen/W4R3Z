cmake_minimum_required(VERSION 3.20)
project(anonsync_core LANGUAGES C CXX)
include(GNUInstallDirs)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
find_package(OpenSSL REQUIRED)
find_package(Threads REQUIRED)
option(ANONSYNC_USE_BUNDLED_SQLITE
  "Build against the reviewed SQLite amalgamation pinned under third_party" ON)
option(ANONSYNC_ENABLE_SANITIZERS "Build with AddressSanitizer and UndefinedBehaviorSanitizer when supported" OFF)
option(ANONSYNC_SANITIZE_BUNDLED_SQLITE
  "Also instrument the pinned SQLite amalgamation (slow; intended for dedicated upstream-boundary jobs)" OFF)
option(ANONSYNC_ENABLE_LIBFUZZER
  "Build the Clang libFuzzer projection-decoder target" OFF)
option(ANONSYNC_LIBFUZZER_WITH_ASAN
  "Add AddressSanitizer to the libFuzzer target (toolchain/runtime dependent)" OFF)

# One lifecycle policy feeds both the C++ admission boundary and the installed
# Type=notify user unit. A configured network step may finish after SIGTERM, but
# no new step begins; the manager margin covers local status publication and
# capability teardown without pretending arbitrary filesystem scans are timed.
set(ANONSYNC_INSTALLED_SERVICE_MAXIMUM_NETWORK_STEP_SECONDS 3600
  CACHE STRING "Maximum admitted linked-peer network owner step")
set(ANONSYNC_INSTALLED_SERVICE_STOP_TIMEOUT_SECONDS 3660
  CACHE STRING "Installed linked-peer service graceful-stop timeout")
if(ANONSYNC_INSTALLED_SERVICE_MAXIMUM_NETWORK_STEP_SECONDS LESS 1)
  message(FATAL_ERROR
    "ANONSYNC_INSTALLED_SERVICE_MAXIMUM_NETWORK_STEP_SECONDS must be positive")
endif()
if(ANONSYNC_INSTALLED_SERVICE_STOP_TIMEOUT_SECONDS LESS_EQUAL
    ANONSYNC_INSTALLED_SERVICE_MAXIMUM_NETWORK_STEP_SECONDS)
  message(FATAL_ERROR
    "installed service stop timeout must exceed the maximum network step")
endif()
set(ANONSYNC_SYSTEMD_USER_UNIT_INSTALL_DIR
  "${CMAKE_INSTALL_LIBDIR}/systemd/user" CACHE STRING
  "Install directory for the AnonSync systemd user unit")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/packaging/systemd")
set(ANONSYNC_CONFIGURED_SYSTEMD_USER_UNIT
  "${CMAKE_CURRENT_BINARY_DIR}/packaging/systemd/anonsync-linked-peer@.service")
configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/packaging/systemd/anonsync-linked-peer@.service.in"
  "${ANONSYNC_CONFIGURED_SYSTEMD_USER_UNIT}"
  @ONLY)

if(ANONSYNC_USE_BUNDLED_SQLITE)
  # One reviewed profile owns the vendored path, every retained file digest,
  # the official amalgamation SHA3, and the semantic runtime identity. Keep
  # native configure and pre-compilation gates independent of Python and of
  # prior build trees.
  include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/AnonSyncBundledSqliteProfile.cmake")
  include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/AnonSyncVerifyBundledSqlite.cmake")
  anonsync_verify_bundled_sqlite_profile("${CMAKE_CURRENT_SOURCE_DIR}")
  set(ANONSYNC_BUNDLED_SQLITE_DIR
    "${ANONSYNC_BUNDLED_SQLITE_VERIFIED_DIR}")

  set(ANONSYNC_BUNDLED_SQLITE_GENERATED_INCLUDE_DIR
    "${CMAKE_CURRENT_BINARY_DIR}/generated")
  file(MAKE_DIRECTORY "${ANONSYNC_BUNDLED_SQLITE_GENERATED_INCLUDE_DIR}")
  configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/anonsync_bundled_sqlite_profile.hpp.in"
    "${ANONSYNC_BUNDLED_SQLITE_GENERATED_INCLUDE_DIR}/anonsync_bundled_sqlite_profile.hpp"
    @ONLY)
  message(STATUS
    "Verified bundled SQLite ${ANONSYNC_BUNDLED_SQLITE_VERSION} complete profile "
    "(closed nonsymlink inventory, SHA-256, official sqlite3.c SHA3-256, "
    "semantic identity generated)")
  add_library(anonsync_sqlite3 STATIC
    "${ANONSYNC_BUNDLED_SQLITE_DIR}/sqlite3.c")
  anonsync_add_bundled_sqlite_build_gate(
    anonsync_sqlite3
    "${CMAKE_CURRENT_SOURCE_DIR}")
  target_include_directories(anonsync_sqlite3 PUBLIC
    "${ANONSYNC_BUNDLED_SQLITE_DIR}")
  target_compile_definitions(anonsync_sqlite3 PRIVATE
    SQLITE_THREADSAFE=1
    SQLITE_DQS=0
    SQLITE_DEFAULT_FOREIGN_KEYS=1
    SQLITE_DEFAULT_MEMSTATUS=0
    SQLITE_DEFAULT_SYNCHRONOUS=2
    SQLITE_DEFAULT_WAL_SYNCHRONOUS=2
    SQLITE_ENABLE_API_ARMOR
    SQLITE_OMIT_LOAD_EXTENSION
    SQLITE_OMIT_SHARED_CACHE
    SQLITE_SECURE_DELETE=1
    SQLITE_TRUSTED_SCHEMA=0)
  target_link_libraries(anonsync_sqlite3 PUBLIC Threads::Threads ${CMAKE_DL_LIBS})
  set_target_properties(anonsync_sqlite3 PROPERTIES POSITION_INDEPENDENT_CODE ON)
  set(ANONSYNC_SQLITE_TARGET anonsync_sqlite3)
else()
  find_package(SQLite3 REQUIRED)
  set(ANONSYNC_SYSTEM_SQLITE_WAL_RESET_SAFE OFF)
  if(SQLite3_VERSION VERSION_GREATER_EQUAL "3.51.3")
    set(ANONSYNC_SYSTEM_SQLITE_WAL_RESET_SAFE ON)
  elseif(SQLite3_VERSION VERSION_GREATER_EQUAL "3.50.7" AND
         SQLite3_VERSION VERSION_LESS "3.51.0")
    set(ANONSYNC_SYSTEM_SQLITE_WAL_RESET_SAFE ON)
  elseif(SQLite3_VERSION VERSION_GREATER_EQUAL "3.44.6" AND
         SQLite3_VERSION VERSION_LESS "3.45.0")
    set(ANONSYNC_SYSTEM_SQLITE_WAL_RESET_SAFE ON)
  endif()
  if(NOT ANONSYNC_SYSTEM_SQLITE_WAL_RESET_SAFE)
    message(FATAL_ERROR
      "System SQLite ${SQLite3_VERSION} is not known to contain the official "
      "WAL-reset corruption fix. AnonSync refuses an implicit journal-policy "
      "downgrade: use the bundled SQLite profile (default), SQLite 3.51.3+, "
      "SQLite 3.50.7 on the 3.50 branch, or SQLite 3.44.6 on the 3.44 branch.")
  endif()
  set(ANONSYNC_SQLITE_TARGET SQLite::SQLite3)
endif()

# A raw PID is recyclable and therefore cannot by itself identify a live
# capability owner. This independently linked boundary mints one opaque token
# from the current PID plus an ordinary-fork lineage generation, advances the
# child copy in a pthread_atfork hook, and lets every capability owner reject
# inherited authority before touching parent-owned resources.
set(ANONSYNC_PROCESS_INCARNATION_SOURCE
  src/sync_process_incarnation.cpp)
add_library(anonsync_process_incarnation STATIC
  ${ANONSYNC_PROCESS_INCARNATION_SOURCE})
target_include_directories(anonsync_process_incarnation PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_process_incarnation PUBLIC
  Threads::Threads)
target_compile_options(anonsync_process_incarnation PRIVATE
  -Wall -Wextra -Wpedantic)

# Native thread identifiers may be reused, and thread_local state survives as
# copied bytes across fork. Keep exact thread-lifetime identity in a generic
# process-bound leaf so SQLite and filesystem capabilities share one owner
# primitive without introducing a SQLite dependency into persistence leaves.
set(ANONSYNC_THREAD_INCARNATION_SOURCE
  src/sync_thread_incarnation.cpp)
add_library(anonsync_thread_incarnation STATIC
  ${ANONSYNC_THREAD_INCARNATION_SOURCE})
target_include_directories(anonsync_thread_incarnation PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_thread_incarnation PUBLIC
  anonsync_process_incarnation)
target_compile_options(anonsync_thread_incarnation PRIVATE
  -Wall -Wextra -Wpedantic)

# A descriptor number can be recycled through close/dup2 while still naming a
# nonblocking socket. Keep the Linux fstat/SO_COOKIE lifetime proof in one
# transport-independent leaf so readiness adapters reprove the same kernel
# socket object rather than merely the same integer. Other platforms fail closed
# until they provide an equivalently strong process-local lifetime identifier.
set(ANONSYNC_SYNC_SOCKET_READINESS_IDENTITY_SOURCE
  src/sync_socket_readiness_identity.cpp)
add_library(anonsync_sync_socket_readiness_identity STATIC
  ${ANONSYNC_SYNC_SOCKET_READINESS_IDENTITY_SOURCE})
target_include_directories(anonsync_sync_socket_readiness_identity PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sync_socket_readiness_identity PRIVATE
  -Wall -Wextra -Wpedantic)

# Generic absolute-deadline readiness owner for one exact nonblocking stream
# socket lifetime. It deliberately reports only advisory readiness; the caller
# retains protocol classification and durable authority.
set(ANONSYNC_SYNC_STREAM_SOCKET_DEADLINE_POLL_SOURCE
  src/sync_stream_socket_deadline_poll.cpp)
add_library(anonsync_sync_stream_socket_deadline_poll STATIC
  ${ANONSYNC_SYNC_STREAM_SOCKET_DEADLINE_POLL_SOURCE})
target_include_directories(anonsync_sync_stream_socket_deadline_poll PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_stream_socket_deadline_poll PUBLIC
  anonsync_sync_socket_readiness_identity)
target_compile_options(anonsync_sync_stream_socket_deadline_poll PRIVATE
  -Wall -Wextra -Wpedantic)

# A heartbeat PID is recyclable.  Keep serializable OS process-life evidence in
# a separate observational leaf so it cannot be confused with the opaque,
# process-local SyncProcessIncarnation capability above.
set(ANONSYNC_PROCESS_IDENTITY_OBSERVATION_SOURCE
  src/sync_process_identity_observation.cpp)
add_library(anonsync_process_identity_observation STATIC
  ${ANONSYNC_PROCESS_IDENTITY_OBSERVATION_SOURCE})
target_include_directories(anonsync_process_identity_observation PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_process_identity_observation PRIVATE
  -Wall -Wextra -Wpedantic)

# Exact SQLite scalar extraction is a small invariant-owned boundary shared by
# runtime policy, generic support, runner metadata, and replay-ledger recovery.
# It is the only general-purpose location permitted to call sqlite3_column_*
# directly; callers receive byte-exact TEXT/BLOB and exact storage classes.
set(ANONSYNC_SQLITE_EXACT_VALUE_SOURCE
  src/persistence/sqlite_exact_value.cpp)
add_library(anonsync_sqlite_exact_value STATIC
  ${ANONSYNC_SQLITE_EXACT_VALUE_SOURCE})
target_include_directories(anonsync_sqlite_exact_value PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_exact_value PUBLIC
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_exact_value PRIVATE
  -Wall -Wextra -Wpedantic)

# Sender-replay evidence is promoted to a durable reservation only after one
# small semantic owner validates every field and its exact prepared-entry
# binding. Keeping this pure C++ boundary outside the replay-ledger monolith
# makes malformed, overflow-edge, and aliasing proofs independently cheap.
set(ANONSYNC_INGRESS_SENDER_REPLAY_RECORD_SOURCE
  src/persistence/ingress_sender_replay_record.cpp)
add_library(anonsync_ingress_sender_replay_record STATIC
  ${ANONSYNC_INGRESS_SENDER_REPLAY_RECORD_SOURCE})
target_include_directories(anonsync_ingress_sender_replay_record PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_compile_options(anonsync_ingress_sender_replay_record PRIVATE
  -Wall -Wextra -Wpedantic)

# Schema shape is durable authority, not merely a list of expected columns.
# One pure owner supplies the exact version-10 CREATE SQL for new ledgers and
# verifies the exact normalized sqlite_schema.sql text before an existing or
# restored database is promoted. This prevents IF NOT EXISTS from laundering a
# weakened schema into writable authority.
set(ANONSYNC_SQLITE_REPLAY_LEDGER_SCHEMA_CONTRACT_SOURCE
  src/persistence/sqlite_replay_ledger_schema_contract.cpp)
add_library(anonsync_sqlite_replay_ledger_schema_contract STATIC
  ${ANONSYNC_SQLITE_REPLAY_LEDGER_SCHEMA_CONTRACT_SOURCE})
target_include_directories(anonsync_sqlite_replay_ledger_schema_contract PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_compile_options(anonsync_sqlite_replay_ledger_schema_contract PRIVATE
  -Wall -Wextra -Wpedantic)

# Linux mount namespace identity is a live authority boundary independent of
# path and mount-point identity. Retain /proc/thread-self/ns/mnt in one focused
# owner so a thread cannot unshare or join another mount namespace while still
# presenting a descriptor captured in the original context.
set(ANONSYNC_SYNC_POSIX_MOUNT_NAMESPACE_AUTHORITY_SOURCE
  src/sync_posix_mount_namespace_authority.cpp)
add_library(anonsync_sync_posix_mount_namespace_authority STATIC
  ${ANONSYNC_SYNC_POSIX_MOUNT_NAMESPACE_AUTHORITY_SOURCE})
target_include_directories(anonsync_sync_posix_mount_namespace_authority PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sync_posix_mount_namespace_authority PRIVATE
  -Wall -Wextra -Wpedantic)

# SQLite pathname identity and no-symlink family traversal are shared security
# infrastructure, not an implementation detail of the core monolith.  Keeping
# this owner separately linkable lets snapshot sealing and focused adversarial
# tests use the exact production path checks without compiling sync_domain.cpp.
set(ANONSYNC_SQLITE_PATH_SECURITY_SOURCE
  src/sqlite_path_security.cpp)
add_library(anonsync_sqlite_path_security STATIC
  ${ANONSYNC_SQLITE_PATH_SECURITY_SOURCE})
target_include_directories(anonsync_sqlite_path_security PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_path_security PUBLIC
  anonsync_process_incarnation
  anonsync_sync_posix_directory_resolution
  anonsync_sync_posix_mount_namespace_authority
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_path_security PRIVATE
  -Wall -Wextra -Wpedantic)

# Raw SQLite header fields become authority only after one pure boundary proves
# canonical file geometry: valid current page-count evidence and an exact
# page_count * page_size == descriptor_bytes relationship.  Keeping this logic
# separate makes trailing-byte and stale-header proofs independent of OpenSSL,
# the filesystem, and the core monolith.
set(ANONSYNC_SQLITE_SNAPSHOT_GEOMETRY_SOURCE
  src/persistence/sqlite_snapshot_geometry.cpp)
add_library(anonsync_sqlite_snapshot_geometry STATIC
  ${ANONSYNC_SQLITE_SNAPSHOT_GEOMETRY_SOURCE})
target_include_directories(anonsync_sqlite_snapshot_geometry PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_compile_options(anonsync_sqlite_snapshot_geometry PRIVATE
  -Wall -Wextra -Wpedantic)

# Live SQLite capture has a separate authority owner. It pins one source read
# transaction, copies only fixed-size page batches, and rejects page-count drift,
# restart, non-progress, or process-incarnation loss before another batch.
set(ANONSYNC_SQLITE_LIVE_BACKUP_SOURCE
  src/persistence/sqlite_live_backup.cpp)
add_library(anonsync_sqlite_live_backup STATIC
  ${ANONSYNC_SQLITE_LIVE_BACKUP_SOURCE})
target_include_directories(anonsync_sqlite_live_backup PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_live_backup
  PRIVATE
    anonsync_sqlite_exact_value
  PUBLIC
    anonsync_process_incarnation
    anonsync_sqlite_snapshot_geometry
    ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_live_backup PRIVATE
  -Wall -Wextra -Wpedantic)


# SQLite scoped mutation has two deliberately disjoint capabilities. The strict
# database-mutex witness is FULLMUTEX-only and authorizes retained callback
# claim/install transitions. The raw busy-timeout gateway receives a separate
# non-authorizing owner that may admit an externally single-user NOMUTEX handle
# but still enforces process and exact-thread teardown affinity. Both owners use
# one shared process-then-thread fail-stop validator.
set(ANONSYNC_SQLITE_EXECUTION_AFFINITY_SOURCE
  src/sync_sqlite_execution_affinity.cpp)
set(ANONSYNC_SQLITE_DATABASE_MUTEX_GUARD_SOURCE
  src/sync_sqlite_database_mutex_guard.cpp)
set(ANONSYNC_SQLITE_BUSY_TIMEOUT_MUTATION_GUARD_SOURCE
  src/sync_sqlite_busy_timeout_mutation_guard.cpp)
add_library(anonsync_sqlite_database_mutex_guard STATIC
  ${ANONSYNC_SQLITE_EXECUTION_AFFINITY_SOURCE}
  ${ANONSYNC_SQLITE_DATABASE_MUTEX_GUARD_SOURCE}
  ${ANONSYNC_SQLITE_BUSY_TIMEOUT_MUTATION_GUARD_SOURCE})
target_include_directories(anonsync_sqlite_database_mutex_guard PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_database_mutex_guard PUBLIC
  anonsync_process_incarnation
  anonsync_thread_incarnation
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_database_mutex_guard PRIVATE
  -Wall -Wextra -Wpedantic)
target_link_libraries(anonsync_sqlite_path_security PUBLIC
  anonsync_sqlite_database_mutex_guard)

# SQLite retained-callback setters publish a raw address into one mutable slot.
# This independent process-bound owner claims that slot through named client
# data, rejects connection destruction or same-name replacement while live,
# and authorizes only the exact synchronous detach path. sqlite3_close_v2 may
# defer the destructor behind outstanding dependents; typed generation owners
# therefore remain the reviewed synchronous close boundary.
set(ANONSYNC_SQLITE_RETAINED_CALLBACK_CLAIM_SOURCE
  src/persistence/sqlite_retained_callback_claim.cpp)
add_library(anonsync_sqlite_retained_callback_claim STATIC
  ${ANONSYNC_SQLITE_RETAINED_CALLBACK_CLAIM_SOURCE})
target_include_directories(anonsync_sqlite_retained_callback_claim PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_retained_callback_claim PUBLIC
  anonsync_process_incarnation
  anonsync_sqlite_database_mutex_guard
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_retained_callback_claim PRIVATE
  -Wall -Wextra -Wpedantic)

# Application authorizer policy state must not remain a loose void* behind
# SQLite's retained bridge. This dependency-light move-only owner binds the
# callback and optional shared context to one process incarnation and gives the
# connection state machine a safe retirement escrow outside SQLite's mutex.
set(ANONSYNC_SQLITE_OWNED_AUTHORIZER_POLICY_SOURCE
  src/sync_sqlite_owned_authorizer_policy.cpp)
add_library(anonsync_sqlite_owned_authorizer_policy STATIC
  ${ANONSYNC_SQLITE_OWNED_AUTHORIZER_POLICY_SOURCE})
target_include_directories(anonsync_sqlite_owned_authorizer_policy PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_owned_authorizer_policy PUBLIC
  anonsync_process_incarnation)
target_compile_options(anonsync_sqlite_owned_authorizer_policy PRIVATE
  -Wall -Wextra -Wpedantic)

# SQLite's singleton authorizer slot retains a raw callback context and exposes
# no getter or destructor.  This focused owner composes the shared client-data
# lifetime claim, makes replacement explicit, and revokes the callback before
# releasing the context address.
set(ANONSYNC_SQLITE_AUTHORIZER_OWNER_SOURCE
  src/persistence/sqlite_authorizer_owner.cpp)
add_library(anonsync_sqlite_authorizer_owner STATIC
  ${ANONSYNC_SQLITE_AUTHORIZER_OWNER_SOURCE})
target_include_directories(anonsync_sqlite_authorizer_owner PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_authorizer_owner PUBLIC
  anonsync_sqlite_database_mutex_guard
  anonsync_sqlite_retained_callback_claim
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_authorizer_owner PRIVATE
  -Wall -Wextra -Wpedantic)

# A sealed byte/page extent does not bound SQLite execution or C++ projection.
# This independently linked lifetime owner installs the sole progress handler
# on a hostile-snapshot connection and enforces monotone work, row, decoded-byte,
# retained-byte, and wall-clock ceilings without depending on the core monolith.
set(ANONSYNC_SQLITE_VERIFICATION_BUDGET_SOURCE
  src/persistence/sqlite_verification_budget.cpp)
add_library(anonsync_sqlite_verification_budget STATIC
  ${ANONSYNC_SQLITE_VERIFICATION_BUDGET_SOURCE})
target_include_directories(anonsync_sqlite_verification_budget PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_verification_budget PUBLIC
  anonsync_sqlite_retained_callback_claim
  anonsync_sqlite_support
  anonsync_thread_incarnation
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_verification_budget PRIVATE
  -Wall -Wextra -Wpedantic)

# A SQLite snapshot becomes authority only after exact geometry, standalone
# file format, process lineage, VFS identity, and SHA-256 are bound to one
# namespace-free resident allocation. Path capture reads one guarded descriptor;
# live backup copies an already-owned connection into private memory and
# canonicalizes it there. Logical verification and atomic publication consume
# that same move-only seal without a writable SQLite staging pathname.
set(ANONSYNC_SQLITE_SNAPSHOT_SEAL_SOURCE
  src/persistence/sqlite_snapshot_seal.cpp)
add_library(anonsync_sqlite_snapshot_seal STATIC
  ${ANONSYNC_SQLITE_SNAPSHOT_SEAL_SOURCE})
target_include_directories(anonsync_sqlite_snapshot_seal PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_snapshot_seal
  PRIVATE
    anonsync_sqlite_exact_value
    anonsync_sqlite_live_backup
  PUBLIC
    anonsync_sqlite_support
    anonsync_sqlite_snapshot_geometry
    anonsync_sqlite_path_security
    OpenSSL::Crypto
    ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_snapshot_seal PRIVATE
  -Wall -Wextra -Wpedantic)

add_library(anonsync_sqlite_runtime STATIC src/sync_sqlite_runtime.cpp)
target_include_directories(anonsync_sqlite_runtime PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)
if(ANONSYNC_USE_BUNDLED_SQLITE)
  target_include_directories(anonsync_sqlite_runtime PRIVATE
    ${ANONSYNC_BUNDLED_SQLITE_GENERATED_INCLUDE_DIR})
endif()
target_link_libraries(anonsync_sqlite_runtime PUBLIC
  anonsync_sqlite_exact_value
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_runtime PRIVATE -Wall -Wextra -Wpedantic)
if(ANONSYNC_USE_BUNDLED_SQLITE)
  target_compile_definitions(anonsync_sqlite_runtime PRIVATE ANONSYNC_BUNDLED_SQLITE=1)
endif()

# The peer-ingress durable-connection verifier is an invariant-owned boundary,
# not an implementation detail of the monolithic domain archive.  Keep it as a
# separately linkable library so its focused proof never has to compile the
# 24k-line sync domain or unrelated transports, ledgers, codecs, and reports.
set(ANONSYNC_PEER_INGRESS_CONNECTION_PROFILE_SOURCE
  src/persistence/peer_ingress_connection_profile.cpp)
add_library(anonsync_peer_ingress_connection_profile STATIC
  ${ANONSYNC_PEER_INGRESS_CONNECTION_PROFILE_SOURCE})
target_include_directories(anonsync_peer_ingress_connection_profile PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_peer_ingress_connection_profile PUBLIC
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_peer_ingress_connection_profile PRIVATE
  -Wall -Wextra -Wpedantic)

# Canonical projection comparison is a pure evidence boundary.  The focused
# proof should compile only this implementation, not the whole application.
set(ANONSYNC_CANONICAL_PROJECTION_VERIFIER_SOURCE
  src/persistence/canonical_projection_verifier.cpp)
add_library(anonsync_canonical_projection_verifier STATIC
  ${ANONSYNC_CANONICAL_PROJECTION_VERIFIER_SOURCE})
target_include_directories(anonsync_canonical_projection_verifier PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_compile_options(anonsync_canonical_projection_verifier PRIVATE
  -Wall -Wextra -Wpedantic)

# The local JSONL replay backend historically hashed one hand-built tuple and
# emitted a second stream-built row while journal recovery interpreted broad
# JSON again. Keep the compatible row/journal bytes, but own their complete
# fields, locale-free integer spelling, byte budgets, and canonical encoders in
# one independently testable leaf.
set(ANONSYNC_LOCAL_JSONL_REPLAY_PUBLICATION_SOURCE
  src/persistence/local_jsonl_replay_publication.cpp)
add_library(anonsync_local_jsonl_replay_publication STATIC
  ${ANONSYNC_LOCAL_JSONL_REPLAY_PUBLICATION_SOURCE})
target_include_directories(anonsync_local_jsonl_replay_publication PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_local_jsonl_replay_publication PRIVATE
  anonsync_sha256_digest)
target_compile_options(anonsync_local_jsonl_replay_publication PRIVATE
  -Wall -Wextra -Wpedantic)

# A terminal-effect signature is authority only over one exact owning payload.
# This leaf freezes all covered fields, frames v3 signing bytes without ambient
# locale or delimiters, bounds the document, and emits the JSON from that same
# frozen value. The core retains v2 read compatibility but mints only v3.
set(ANONSYNC_EFFECT_TRANSITION_INTENT_PUBLICATION_SOURCE
  src/persistence/effect_transition_intent_publication.cpp)
add_library(anonsync_effect_transition_intent_publication STATIC
  ${ANONSYNC_EFFECT_TRANSITION_INTENT_PUBLICATION_SOURCE})
target_include_directories(anonsync_effect_transition_intent_publication PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_effect_transition_intent_publication PRIVATE
  anonsync_sha256_digest)
target_compile_options(anonsync_effect_transition_intent_publication PRIVATE
  -Wall -Wextra -Wpedantic)

# The durable effect-transition chain historically used newline-delimited
# material across free-text reason, intent-id, and signer-id fields. Preserve
# ordinary wire bytes, but admit them only through one frozen control-free
# owner so distinct rows cannot share hash material by shifting a delimiter.
set(ANONSYNC_EFFECT_TRANSITION_RECORD_MATERIAL_SOURCE
  src/persistence/effect_transition_record_material.cpp)
add_library(anonsync_effect_transition_record_material STATIC
  ${ANONSYNC_EFFECT_TRANSITION_RECORD_MATERIAL_SOURCE})
target_include_directories(anonsync_effect_transition_record_material PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_effect_transition_record_material PRIVATE
  anonsync_sha256_digest)
target_compile_options(anonsync_effect_transition_record_material PRIVATE
  -Wall -Wextra -Wpedantic)

# The legacy snapshot-manifest wire format is accepted only through one frozen,
# control-free owning payload. The leaf preserves valid v2 signing bytes while
# eliminating newline-boundary substitution, ambient-locale integer spelling,
# broad-Json rereads, and unbounded publication text.
set(ANONSYNC_SQLITE_SNAPSHOT_MANIFEST_PUBLICATION_SOURCE
  src/persistence/sqlite_snapshot_manifest_publication.cpp)
add_library(anonsync_sqlite_snapshot_manifest_publication STATIC
  ${ANONSYNC_SQLITE_SNAPSHOT_MANIFEST_PUBLICATION_SOURCE})
target_include_directories(anonsync_sqlite_snapshot_manifest_publication PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_snapshot_manifest_publication PRIVATE
  anonsync_sha256_digest)
target_compile_options(anonsync_sqlite_snapshot_manifest_publication PRIVATE
  -Wall -Wextra -Wpedantic)

# SQLite projection decoding owns column-map and field semantics while routing
# all scalar conversion through the exact-value boundary. Keeping this slice
# independently linkable makes malformed-row testing cheap and exact without
# creating a second raw sqlite3_column_* authority.
set(ANONSYNC_SQLITE_PROJECTION_DECODER_SOURCE
  src/persistence/sqlite_projection_decoder.cpp)
add_library(anonsync_sqlite_projection_decoder STATIC
  ${ANONSYNC_SQLITE_PROJECTION_DECODER_SOURCE})
target_include_directories(anonsync_sqlite_projection_decoder PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_projection_decoder PUBLIC
  anonsync_canonical_projection_verifier
  anonsync_sqlite_exact_value)
target_compile_options(anonsync_sqlite_projection_decoder PRIVATE
  -Wall -Wextra -Wpedantic)

# One independently testable ownership and statement boundary is shared by
# the checkpoint and peer-ingress domains. Keeping it outside either large
# translation unit prevents another private helper copy from becoming an
# accidental source of divergent transaction semantics.
add_library(anonsync_sqlite_support STATIC
  src/sync_sqlite_support.cpp
  src/sync_sqlite_handle_slot.cpp
  src/sync_sqlite_mutex_capability.cpp
  src/sync_sqlite_transaction.cpp
  src/sync_sqlite_connection_authority.cpp)
target_include_directories(anonsync_sqlite_support PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_support
  PRIVATE
    anonsync_sqlite_authorizer_owner
  PUBLIC
    anonsync_sqlite_owned_authorizer_policy
    anonsync_sqlite_database_mutex_guard
    anonsync_process_incarnation
    anonsync_thread_incarnation
    anonsync_sqlite_runtime
    anonsync_sqlite_exact_value)
target_compile_options(anonsync_sqlite_support PRIVATE -Wall -Wextra -Wpedantic)

# A retained SQLite busy callback is a lifetime capability, not a loose helper.
# This focused owner pins one exact serialized connection generation, keeps all
# callback-reachable diagnostics atomic, rejects inherited-process use, and
# revokes both the callback and named client-data claim before its address dies.
set(ANONSYNC_SQLITE_BUSY_HANDLER_OWNER_SOURCE
  src/persistence/sqlite_busy_handler_owner.cpp)
add_library(anonsync_sqlite_busy_handler_owner STATIC
  ${ANONSYNC_SQLITE_BUSY_HANDLER_OWNER_SOURCE})
target_include_directories(anonsync_sqlite_busy_handler_owner PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_busy_handler_owner PUBLIC
  anonsync_sqlite_retained_callback_claim
  anonsync_sqlite_support)
target_compile_options(anonsync_sqlite_busy_handler_owner PRIVATE
  -Wall -Wextra -Wpedantic)

# SHA-256 digest text is a small shared evidence primitive. Keeping it outside
# the JSON/policy translation units lets persistence verifiers hash exact schema
# manifests without pulling unrelated codecs, JWT machinery, or the core model.
set(ANONSYNC_SHA256_DIGEST_SOURCE
  src/sha256_digest.cpp)
add_library(anonsync_sha256_digest STATIC
  ${ANONSYNC_SHA256_DIGEST_SOURCE})
target_include_directories(anonsync_sha256_digest PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sha256_digest PUBLIC OpenSSL::Crypto)
target_compile_options(anonsync_sha256_digest PRIVATE
  -Wall -Wextra -Wpedantic)

# Durable scrub progress needs a provider-independent SHA-256 continuation
# format. Keep this leaf independent from OpenSSL and continuously compare it
# with the ordinary provider-backed digest owner in its focused test.
add_library(anonsync_resumable_sha256 STATIC
  src/resumable_sha256.cpp)
target_include_directories(anonsync_resumable_sha256 PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_resumable_sha256 PRIVATE
  -Wall -Wextra -Wpedantic)

# Restart verification and rotating scrub records bind the same exact eleven-field
# POSIX stat projection. Keep its binary codec and private-regular-file
# validation in one dependency-light leaf so the two durable formats cannot
# silently drift while preserving their existing on-disk byte layouts.
add_library(anonsync_sync_posix_regular_file_snapshot_codec STATIC
  src/sync_posix_regular_file_snapshot_codec.cpp)
target_include_directories(anonsync_sync_posix_regular_file_snapshot_codec PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sync_posix_regular_file_snapshot_codec PRIVATE
  -Wall -Wextra -Wpedantic)

# Strict JSON parsing is a dependency-light authority leaf shared by the broad
# runtime codec and exact operational documents. Keeping it outside the core
# translation unit prevents a narrow manifest reader from inheriting crypto,
# policy, reporting, or SQLite implementation machinery.
set(ANONSYNC_JSON_PARSER_SOURCE
  src/anonsync_json_parser.cpp)
add_library(anonsync_json_parser STATIC
  ${ANONSYNC_JSON_PARSER_SOURCE})
target_include_directories(anonsync_json_parser PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_options(anonsync_json_parser PRIVATE
  -Wall -Wextra -Wpedantic)

# Linux boot identity is one typed, bounded observation shared by process and
# lease-clock owners.  Keep the strict procfs reader in one small leaf so those
# authorities do not silently invent incompatible boot-ID parsers.  A boot UUID
# is reboot-ephemeral evidence, never persistent filesystem-root identity.
set(ANONSYNC_SYSTEM_EPOCH_IDENTITY_SOURCE
  src/sync_system_epoch_identity.cpp)
add_library(anonsync_system_epoch_identity STATIC
  ${ANONSYNC_SYSTEM_EPOCH_IDENTITY_SOURCE})
target_include_directories(anonsync_system_epoch_identity PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_system_epoch_identity PRIVATE
  -Wall -Wextra -Wpedantic)

target_link_libraries(anonsync_process_identity_observation PRIVATE
  anonsync_system_epoch_identity)

# A received socket frame is observation, not checked evidence. Bind its exact
# bytes to the canonical digest frozen before transmission and publish only a
# move-only frame capability after budget and equality checks succeed.
set(ANONSYNC_SYNC_PEER_TRANSPORT_DIGEST_BOUND_FRAME_SOURCE
  src/sync_peer_transport_digest_bound_frame.cpp)
add_library(anonsync_sync_peer_transport_digest_bound_frame STATIC
  ${ANONSYNC_SYNC_PEER_TRANSPORT_DIGEST_BOUND_FRAME_SOURCE})
target_include_directories(anonsync_sync_peer_transport_digest_bound_frame PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_peer_transport_digest_bound_frame PUBLIC
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_peer_transport_digest_bound_frame PRIVATE
  -Wall -Wextra -Wpedantic)

# Security identities often need only the SHA-256 of a framed tuple, not a
# second in-memory copy of the complete tuple. This leaf streams the exact
# established v1 byte format and is shared by aggregate identity owners.
set(ANONSYNC_SECURITY_TUPLE_DIGEST_SOURCE
  src/security_tuple_digest.cpp)
add_library(anonsync_security_tuple_digest STATIC
  ${ANONSYNC_SECURITY_TUPLE_DIGEST_SOURCE})
target_include_directories(anonsync_security_tuple_digest PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_security_tuple_digest PUBLIC
  anonsync_sha256_digest)
target_compile_options(anonsync_security_tuple_digest PRIVATE
  -Wall -Wextra -Wpedantic)

# A typed manifest can carry attacker-influenced nested vectors even after its
# parser has returned. Bound cardinality and semantic metadata bytes before
# identity hashing, diff planning, or filesystem work, and keep portable path
# validation allocation-free and independent of ambient locale.
set(ANONSYNC_SYNC_MANIFEST_VALIDATION_SOURCE
  src/sync_manifest_validation.cpp)
add_library(anonsync_sync_manifest_validation STATIC
  ${ANONSYNC_SYNC_MANIFEST_VALIDATION_SOURCE})
target_include_directories(anonsync_sync_manifest_validation PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_manifest_validation PUBLIC
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_manifest_validation PRIVATE
  -Wall -Wextra -Wpedantic)

# Persisted and wire manifests must admit declared cardinality and byte budgets
# before nested vectors grow. This single-use owner consumes rows incrementally
# and publishes only a complete independently revalidated entry.
set(ANONSYNC_SYNC_MANIFEST_STREAM_DECODER_SOURCE
  src/sync_manifest_stream_decoder.cpp)
add_library(anonsync_sync_manifest_stream_decoder STATIC
  ${ANONSYNC_SYNC_MANIFEST_STREAM_DECODER_SOURCE})
target_include_directories(anonsync_sync_manifest_stream_decoder PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_manifest_stream_decoder PUBLIC
  anonsync_sync_manifest_validation)
target_compile_options(anonsync_sync_manifest_stream_decoder PRIVATE
  -Wall -Wextra -Wpedantic)

# Transfer workers already hold a small planner-selected chunk subset. Verify
# that subset with exact main-schema point probes and independent row, metadata,
# and payload ceilings instead of rematerializing an attacker-sized manifest.
set(ANONSYNC_SYNC_SQLITE_MANIFEST_CHUNK_SUBSET_SOURCE
  src/sync_sqlite_manifest_chunk_subset.cpp)
add_library(anonsync_sync_sqlite_manifest_chunk_subset STATIC
  ${ANONSYNC_SYNC_SQLITE_MANIFEST_CHUNK_SUBSET_SOURCE})
target_include_directories(anonsync_sync_sqlite_manifest_chunk_subset PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_sqlite_manifest_chunk_subset PUBLIC
  anonsync_sync_manifest_validation
  anonsync_sqlite_support)
target_compile_options(anonsync_sync_sqlite_manifest_chunk_subset PRIVATE
  -Wall -Wextra -Wpedantic)

# Sidecar checkpoint hydration must freeze its claimed-path frontier inside the
# exact transaction that owns every later apply/manifest evidence read. Keep
# the main-qualified bounded query in a small exact-generation owner.
set(ANONSYNC_SYNC_SQLITE_SIDECAR_CLAIMED_PATH_SNAPSHOT_SOURCE
  src/sync_sqlite_sidecar_claimed_path_snapshot.cpp)
add_library(anonsync_sync_sqlite_sidecar_claimed_path_snapshot STATIC
  ${ANONSYNC_SYNC_SQLITE_SIDECAR_CLAIMED_PATH_SNAPSHOT_SOURCE})
target_include_directories(anonsync_sync_sqlite_sidecar_claimed_path_snapshot PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_sqlite_sidecar_claimed_path_snapshot PUBLIC
  anonsync_sqlite_busy_handler_owner
  anonsync_sqlite_verification_budget
  anonsync_sync_manifest_validation
  anonsync_sqlite_support)
target_compile_options(anonsync_sync_sqlite_sidecar_claimed_path_snapshot PRIVATE
  -Wall -Wextra -Wpedantic)

# Manifest entry, version, and folder identities are nested aggregate hashes.
# Keep their compatibility-sensitive byte grammar out of the domain monolith
# and stream each aggregate directly into SHA-256.
set(ANONSYNC_SYNC_MANIFEST_IDENTITY_SOURCE
  src/sync_manifest_identity.cpp)
add_library(anonsync_sync_manifest_identity STATIC
  ${ANONSYNC_SYNC_MANIFEST_IDENTITY_SOURCE})
target_include_directories(anonsync_sync_manifest_identity PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_manifest_identity PUBLIC
  anonsync_security_tuple_digest)
target_compile_options(anonsync_sync_manifest_identity PRIVATE
  -Wall -Wextra -Wpedantic)

# Concurrent file and tombstone versions need one orientation-independent
# winner and one shared conflict-set identity. Keep that deterministic policy
# in a small pure C++ owner so both peer orientations and generated-history
# tests exercise the exact production rule without compiling the domain
# monolith.
set(ANONSYNC_SYNC_CONFLICT_RESOLUTION_SOURCE
  src/sync_conflict_resolution.cpp)
add_library(anonsync_sync_conflict_resolution STATIC
  ${ANONSYNC_SYNC_CONFLICT_RESOLUTION_SOURCE})
target_include_directories(anonsync_sync_conflict_resolution PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_conflict_resolution PUBLIC
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_conflict_resolution PRIVATE
  -Wall -Wextra -Wpedantic)

# Causal summaries are not proof that exact history exists. This pure C++
# oracle binds each dotted event to canonical bytes plus immediate predecessor
# hashes, retains immutable evidence, deterministically projects active/pending/
# quarantined state independent of arrival order, and applies the production
# conflict policy without depending on the sync-domain monolith or SQLite.
set(ANONSYNC_SYNC_REPLICA_MODEL_SOURCE
  src/sync_replica_digest_accumulator.cpp
  src/sync_replica_file_content_inventory.cpp
  src/sync_replica_model.cpp
  src/sync_replica_operation_codec.cpp
  src/sync_replica_evidence_projection.cpp)
add_library(anonsync_sync_replica_model STATIC
  ${ANONSYNC_SYNC_REPLICA_MODEL_SOURCE})
target_include_directories(anonsync_sync_replica_model PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_model PUBLIC
  anonsync_sync_manifest_validation
  anonsync_sync_conflict_resolution)
target_compile_options(anonsync_sync_replica_model PRIVATE
  -Wall -Wextra -Wpedantic)

# Lease/retry authority consumes one owned host-clock observation, not a caller
# epoch.  The pure state machine binds source, boot, time namespace, uncertainty,
# a cumulative drift anchor, quarantine evidence, and explicit recovery.  Linux
# probing treats kernel release only as a feature-generation hint: an unavailable
# calling-thread namespace identity is durable Unknown evidence, never a fabricated
# synchronization claim. Sampling remains isolated so policy is easy to fuzz and
# sanitize without syscall substitution.
set(ANONSYNC_SYNC_REPLICA_OUTBOX_CLOCK_SOURCES
  src/sync_replica_outbox_clock.cpp
  src/sync_replica_outbox_clock_linux.cpp)
add_library(anonsync_sync_replica_outbox_clock STATIC
  ${ANONSYNC_SYNC_REPLICA_OUTBOX_CLOCK_SOURCES})
target_include_directories(anonsync_sync_replica_outbox_clock PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_outbox_clock PRIVATE
  anonsync_sha256_digest
  anonsync_system_epoch_identity)
target_compile_options(anonsync_sync_replica_outbox_clock PRIVATE
  -Wall -Wextra -Wpedantic)

# Delivery attempts are operational state, but settlement is still authority.
# This pure policy owner mints one fresh receipt per lease, fences expired
# receipts, retains exact retry-release provenance, and keeps time-dependent
# policy separate from immutable replica evidence and SQLite mechanics.
set(ANONSYNC_SYNC_REPLICA_OUTBOX_LEASE_SOURCE
  src/sync_replica_outbox_lease.cpp)
add_library(anonsync_sync_replica_outbox_lease STATIC
  ${ANONSYNC_SYNC_REPLICA_OUTBOX_LEASE_SOURCE})
target_include_directories(anonsync_sync_replica_outbox_lease PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_outbox_lease PUBLIC
  anonsync_sha256_digest
  anonsync_sync_manifest_validation)
target_compile_options(anonsync_sync_replica_outbox_lease PRIVATE
  -Wall -Wextra -Wpedantic)

# The durable replica-operation cutpoint binds exact canonical evidence, local
# dot authority, deterministic projection attestations, persisted policy, and
# receipt-fenced sender intents in one typed SQLite transaction. A separate
# exact clock row remembers accepted liveness without falsely advancing the
# evidence generation. One canonical operation row serves every destination.
set(ANONSYNC_SYNC_REPLICA_SQLITE_OWNER_SOURCE
  src/sync_replica_sqlite_owner.cpp)
add_library(anonsync_sync_replica_sqlite_owner STATIC
  ${ANONSYNC_SYNC_REPLICA_SQLITE_OWNER_SOURCE})
target_include_directories(anonsync_sync_replica_sqlite_owner PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_sqlite_owner PUBLIC
  anonsync_sync_replica_model
  anonsync_sync_replica_outbox_clock
  anonsync_sync_replica_outbox_lease
  anonsync_sqlite_support)
target_compile_options(anonsync_sync_replica_sqlite_owner PRIVATE
  -Wall -Wextra -Wpedantic)

# Canonical bounded request/receipt frames bind one exact outbox attempt to the
# authenticated peer actor epoch and lower-layer channel context. Structural
# digests detect malformed transport data but are not authentication keys.
set(ANONSYNC_SYNC_REPLICA_DELIVERY_PROTOCOL_SOURCE
  src/sync_replica_delivery_protocol.cpp)
add_library(anonsync_sync_replica_delivery_protocol STATIC
  ${ANONSYNC_SYNC_REPLICA_DELIVERY_PROTOCOL_SOURCE})
target_include_directories(anonsync_sync_replica_delivery_protocol PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_delivery_protocol PUBLIC
  anonsync_sync_replica_model
  PRIVATE anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_delivery_protocol PRIVATE
  -Wall -Wextra -Wpedantic)

# One bounded longest-prefix selective-sync policy is shared by the rooted
# scanner, reconciliation wire, catalog owner, and shipping CLI. It is a small
# semantic leaf: no filesystem, SQLite, network, or scheduler authority lives
# here, and policy memory is bounded independently of tree size.
set(ANONSYNC_SYNC_REPLICA_SELECTIVE_SYNC_POLICY_SOURCE
  src/sync_replica_selective_sync_policy.cpp)
add_library(anonsync_sync_replica_selective_sync_policy STATIC
  ${ANONSYNC_SYNC_REPLICA_SELECTIVE_SYNC_POLICY_SOURCE})
target_include_directories(anonsync_sync_replica_selective_sync_policy PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_selective_sync_policy
  PUBLIC anonsync_sync_manifest_validation
  PRIVATE anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_selective_sync_policy PRIVATE
  -Wall -Wextra -Wpedantic)

# Allocation-free deterministic content-defined chunk boundary selection. The
# gear hash is scheduling only; payload and chunk authority remains SHA-256.
set(ANONSYNC_SYNC_REPLICA_CONTENT_DEFINED_CHUNKER_SOURCE
  src/sync_replica_content_defined_chunker.cpp)
add_library(anonsync_sync_replica_content_defined_chunker STATIC
  ${ANONSYNC_SYNC_REPLICA_CONTENT_DEFINED_CHUNKER_SOURCE})
target_include_directories(anonsync_sync_replica_content_defined_chunker PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sync_replica_content_defined_chunker PRIVATE
  -Wall -Wextra -Wpedantic)

# Bounded share-global peer knowledge exchange. Unlike courier delivery this
# protocol pages every retained operation independent of destination outbox
# history and carries each referenced payload once per page.
set(ANONSYNC_SYNC_REPLICA_RECONCILIATION_PROTOCOL_SOURCE
  src/sync_replica_reconciliation_protocol.cpp)
add_library(anonsync_sync_replica_reconciliation_protocol STATIC
  ${ANONSYNC_SYNC_REPLICA_RECONCILIATION_PROTOCOL_SOURCE})
target_include_directories(anonsync_sync_replica_reconciliation_protocol PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_reconciliation_protocol PUBLIC
  anonsync_sync_replica_delivery_protocol
  anonsync_sync_replica_model
  anonsync_sync_replica_selective_sync_policy
  anonsync_sync_replica_content_defined_chunker
  PRIVATE anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_reconciliation_protocol PRIVATE
  -Wall -Wextra -Wpedantic)

# Peer/binding bytes are descriptive evidence, not proof that authentication
# happened. This move-only, process/thread-bound capability is minted only by a
# reviewed transport adapter (or a separately linked test-only factory).
set(ANONSYNC_SYNC_REPLICA_DELIVERY_CHANNEL_SOURCE
  src/sync_replica_delivery_channel.cpp)
add_library(anonsync_sync_replica_delivery_channel STATIC
  ${ANONSYNC_SYNC_REPLICA_DELIVERY_CHANNEL_SOURCE})
target_include_directories(anonsync_sync_replica_delivery_channel PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_delivery_channel PUBLIC
  anonsync_sync_replica_delivery_protocol
  anonsync_thread_incarnation)
target_compile_options(anonsync_sync_replica_delivery_channel PRIVATE
  -Wall -Wextra -Wpedantic)

# First production-source orchestration seam for the causal owner. An
# authenticated stream adapter supplies peer/channel evidence; this service
# owns durable claim, exact receiver admission cutpoint, receipt, and settlement.
set(ANONSYNC_SYNC_REPLICA_DELIVERY_SERVICE_SOURCE
  src/sync_replica_delivery_service.cpp)
add_library(anonsync_sync_replica_delivery_service STATIC
  ${ANONSYNC_SYNC_REPLICA_DELIVERY_SERVICE_SOURCE})
target_include_directories(anonsync_sync_replica_delivery_service PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_delivery_service PUBLIC
  anonsync_sync_replica_delivery_channel
  anonsync_sync_replica_sqlite_owner)
target_compile_options(anonsync_sync_replica_delivery_service PRIVATE
  -Wall -Wextra -Wpedantic)

# Application-mutable SSL record semantics are a separate authority leaf from
# peer identity, exporter binding, BIO identity, and kernel socket lifetime.
set(ANONSYNC_SYNC_REPLICA_TLS_IO_POLICY_SOURCE
  src/sync_replica_tls_io_policy.cpp)
add_library(anonsync_sync_replica_tls_io_policy STATIC
  ${ANONSYNC_SYNC_REPLICA_TLS_IO_POLICY_SOURCE})
target_include_directories(anonsync_sync_replica_tls_io_policy PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_tls_io_policy PUBLIC
  OpenSSL::SSL)
target_compile_options(anonsync_sync_replica_tls_io_policy PRIVATE
  -Wall -Wextra -Wpedantic)

# A narrow OpenSSL adapter authenticates one peer actor epoch through a pinned
# SubjectPublicKeyInfo, derives the RFC 9266 TLS 1.3 exporter binding, and owns
# allocation-bounded encrypted stream framing. It does not own membership.
set(ANONSYNC_SYNC_REPLICA_TLS_TRANSPORT_SOURCE
  src/sync_replica_tls_transport.cpp)
add_library(anonsync_sync_replica_tls_transport STATIC
  ${ANONSYNC_SYNC_REPLICA_TLS_TRANSPORT_SOURCE})
target_include_directories(anonsync_sync_replica_tls_transport PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_tls_transport PUBLIC
  anonsync_sync_replica_delivery_channel
  OpenSSL::SSL
  PRIVATE anonsync_sha256_digest anonsync_sync_manifest_validation
          anonsync_sync_replica_tls_io_policy
          anonsync_sync_socket_readiness_identity OpenSSL::Crypto)
target_compile_options(anonsync_sync_replica_tls_transport PRIVATE
  -Wall -Wextra -Wpedantic)

# One bounded readiness owner composes the exact TLS read/write continuations
# with poll(2), an absolute steady-clock deadline, and no hidden progress loop.
set(ANONSYNC_SYNC_REPLICA_TLS_POLL_SOURCE
  src/sync_replica_tls_poll.cpp
  src/sync_replica_tls_record_exchange.cpp)
add_library(anonsync_sync_replica_tls_poll STATIC
  ${ANONSYNC_SYNC_REPLICA_TLS_POLL_SOURCE})
target_include_directories(anonsync_sync_replica_tls_poll PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_tls_poll PUBLIC
  anonsync_sync_replica_tls_transport)
target_compile_options(anonsync_sync_replica_tls_poll PRIVATE
  -Wall -Wextra -Wpedantic)

# Fault injection belongs beside the pure model, not hidden in integration
# fixtures. This deterministic harness owns duplicate/loss/reorder, directional
# partitions, crash/restart, durable snapshots, and explicit anti-entropy while
# making no false claim that its in-memory persistence cutpoint is SQLite.
set(ANONSYNC_SYNC_REPLICA_NETWORK_SIMULATOR_SOURCE
  src/sync_replica_network_simulator.cpp)
add_library(anonsync_sync_replica_network_simulator STATIC
  ${ANONSYNC_SYNC_REPLICA_NETWORK_SIMULATOR_SOURCE})
target_include_directories(anonsync_sync_replica_network_simulator PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_network_simulator PUBLIC
  anonsync_sync_replica_model)
target_compile_options(anonsync_sync_replica_network_simulator PRIVATE
  -Wall -Wextra -Wpedantic)

# One process-bound exclusive write-gate owner coordinates every replay-ledger
# writer and administrative transition. Extraction removes lock recursion,
# fork-incarnation, marker durability, and path hardening from the ledger
# monolith so reset and focused tests consume the exact same capability.
set(ANONSYNC_SQLITE_REPLAY_LEDGER_WRITE_GATE_SOURCE
  src/persistence/sqlite_replay_ledger_write_gate.cpp)
add_library(anonsync_sqlite_replay_ledger_write_gate STATIC
  ${ANONSYNC_SQLITE_REPLAY_LEDGER_WRITE_GATE_SOURCE})
target_include_directories(anonsync_sqlite_replay_ledger_write_gate PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_replay_ledger_write_gate PUBLIC
  anonsync_sqlite_path_security
  anonsync_sqlite_support)
target_compile_options(anonsync_sqlite_replay_ledger_write_gate PRIVATE
  -Wall -Wextra -Wpedantic)

# Restore serialization is a distinct process-incarnation-bound authority.
# Keep the path guard, descriptor, nonblocking flock, durable owner marker, and
# fork-child destruction fail-stop in one independently reviewable owner.
set(ANONSYNC_SQLITE_REPLAY_LEDGER_RESTORE_LOCK_SOURCE
  src/persistence/sqlite_replay_ledger_restore_lock.cpp)
add_library(anonsync_sqlite_replay_ledger_restore_lock STATIC
  ${ANONSYNC_SQLITE_REPLAY_LEDGER_RESTORE_LOCK_SOURCE})
target_include_directories(anonsync_sqlite_replay_ledger_restore_lock PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_replay_ledger_restore_lock PUBLIC
  anonsync_sqlite_path_security)
target_compile_options(anonsync_sqlite_replay_ledger_restore_lock PRIVATE
  -Wall -Wextra -Wpedantic)

# Destructive SQLite replay-ledger reset is a separately linked administrative
# transition, never an ordinary load option. It canonically digests every
# durable table under a bounded pinned transaction, compares the exact expected
# state, clears rows without deleting the namespace, and atomically rotates the
# ledger identity to a deterministic crash-recoverable receipt.
set(ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_SOURCE
  src/persistence/sqlite_replay_ledger_reset.cpp)
add_library(anonsync_sqlite_replay_ledger_reset STATIC
  ${ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_SOURCE})
target_include_directories(anonsync_sqlite_replay_ledger_reset PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_replay_ledger_reset
  PRIVATE
    anonsync_sha256_digest
    anonsync_sqlite_exact_value
    anonsync_sqlite_replay_ledger_schema_contract
    anonsync_sqlite_replay_ledger_write_gate
    anonsync_sqlite_verification_budget
    anonsync_sqlite_support
    ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_replay_ledger_reset PRIVATE
  -Wall -Wextra -Wpedantic)

# Reset inspection and durable-event JSON are pure evidence projections. Keep
# their canonical byte contract outside runner.cpp so the first execution and
# exact recovery can be compared in a focused target without compiling the CLI
# or the rest of the sync domain.
set(ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_DOCUMENTS_SOURCE
  src/persistence/sqlite_replay_ledger_reset_documents.cpp)
add_library(anonsync_sqlite_replay_ledger_reset_documents STATIC
  ${ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_DOCUMENTS_SOURCE})
target_include_directories(anonsync_sqlite_replay_ledger_reset_documents PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_replay_ledger_reset_documents
  PUBLIC anonsync_sqlite_replay_ledger_reset
  PRIVATE anonsync_sha256_digest)
target_compile_options(anonsync_sqlite_replay_ledger_reset_documents PRIVATE
  -Wall -Wextra -Wpedantic)

# SQLite stores schema SQL as evidence, but formatting and unquoted identifier
# case are not semantic.  Keep the token-stream canonicalizer in one focused
# library so independent schema owners compare exact semantics without copying
# a parser or depending on one another.
set(ANONSYNC_SQLITE_SCHEMA_IDENTITY_SOURCE
  src/sync_sqlite_schema_identity.cpp)
add_library(anonsync_sqlite_schema_identity STATIC
  ${ANONSYNC_SQLITE_SCHEMA_IDENTITY_SOURCE})
target_include_directories(anonsync_sqlite_schema_identity PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sqlite_schema_identity PRIVATE
  -Wall -Wextra -Wpedantic)

# The peer-ingress schema attestation is one independently testable authority
# boundary. It owns payload-table shape verification and consumes the shared
# exact sqlite_schema identity owner. The operational payload loader remains in
# the core, but schema proof no longer compiles the 24k-line sync domain.
set(ANONSYNC_PEER_INGRESS_SCHEMA_SOURCES
  src/sync_peer_ingress_schema.cpp
  src/sync_peer_ingress_payload_store_schema.cpp)
add_library(anonsync_peer_ingress_schema STATIC
  ${ANONSYNC_PEER_INGRESS_SCHEMA_SOURCES})
target_include_directories(anonsync_peer_ingress_schema PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_peer_ingress_schema PUBLIC
  anonsync_sha256_digest
  anonsync_sqlite_schema_identity
  anonsync_sqlite_support)
target_compile_options(anonsync_peer_ingress_schema PRIVATE
  -Wall -Wextra -Wpedantic)

# Queue selection loads durable evidence; action classification and bounded
# grouping are a pure policy boundary. Keeping the policy free of SQLite,
# filesystem, crypto, and mutator dependencies makes authority ordering cheap
# to exhaustively permute and independently sanitize.
set(ANONSYNC_SYNC_CHECKPOINT_SCHEDULER_POLICY_SOURCE
  src/sync_checkpoint_scheduler_policy.cpp)
add_library(anonsync_sync_checkpoint_scheduler_policy STATIC
  ${ANONSYNC_SYNC_CHECKPOINT_SCHEDULER_POLICY_SOURCE})
target_include_directories(anonsync_sync_checkpoint_scheduler_policy PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sync_checkpoint_scheduler_policy PRIVATE
  -Wall -Wextra -Wpedantic)

# A daemon owner lock becomes a fence only when the database mints a strictly
# increasing generation and every recipient validates that exact generation.
# The transition policy is pure so stale-owner, time-regression, malformed-row,
# and overflow traces can be tested without compiling SQLite or the sync domain.
set(ANONSYNC_SYNC_CHECKPOINT_OWNER_FENCE_POLICY_SOURCE
  src/sync_checkpoint_owner_fence_policy.cpp)
add_library(anonsync_sync_checkpoint_owner_fence_policy STATIC
  ${ANONSYNC_SYNC_CHECKPOINT_OWNER_FENCE_POLICY_SOURCE})
target_include_directories(anonsync_sync_checkpoint_owner_fence_policy PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sync_checkpoint_owner_fence_policy PRIVATE
  -Wall -Wextra -Wpedantic)

# Authority rows are meaningful only under their reviewed durable schema. This
# focused boundary creates the independent sticky-mode table only when truly
# absent, pins exact main.sqlite_schema SQL and PRAGMA geometry, and rejects
# TEMP shadows or trigger programs before any owner evidence is interpreted.
set(ANONSYNC_SYNC_CHECKPOINT_OWNER_SCHEMA_SOURCE
  src/sync_checkpoint_owner_schema.cpp)
add_library(anonsync_sync_checkpoint_owner_schema STATIC
  ${ANONSYNC_SYNC_CHECKPOINT_OWNER_SCHEMA_SOURCE})
target_include_directories(anonsync_sync_checkpoint_owner_schema PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_checkpoint_owner_schema
  PRIVATE
    anonsync_sqlite_schema_identity
    anonsync_sqlite_support)
target_compile_options(anonsync_sync_checkpoint_owner_schema PRIVATE
  -Wall -Wextra -Wpedantic)

# Keep the recipient-side SQLite interpreter independent of the sync-domain
# translation unit. It owns only canonical owner IDs, exact durable-row
# decoding, and same-transaction capability validation.
set(ANONSYNC_SYNC_CHECKPOINT_OWNER_FENCE_SOURCE
  src/sync_checkpoint_owner_fence.cpp)
add_library(anonsync_sync_checkpoint_owner_fence STATIC
  ${ANONSYNC_SYNC_CHECKPOINT_OWNER_FENCE_SOURCE})
target_include_directories(anonsync_sync_checkpoint_owner_fence PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_checkpoint_owner_fence
  PUBLIC
    anonsync_sync_checkpoint_owner_fence_policy
    anonsync_sqlite_support
  PRIVATE
    anonsync_sha256_digest
    anonsync_sync_checkpoint_owner_schema)
target_compile_options(anonsync_sync_checkpoint_owner_fence PRIVATE
  -Wall -Wextra -Wpedantic)

# POSIX directory resolution is one shared syscall owner. It classifies actual
# openat2/statx support, centralizes component-wise no-follow traversal, and
# enforces retained-root mount boundaries without copying subtly different
# openat/fstatat state machines into every filesystem authority.
set(ANONSYNC_SYNC_POSIX_DIRECTORY_RESOLUTION_SOURCE
  src/sync_posix_directory_resolution.cpp)
add_library(anonsync_sync_posix_directory_resolution STATIC
  ${ANONSYNC_SYNC_POSIX_DIRECTORY_RESOLUTION_SOURCE})
target_include_directories(anonsync_sync_posix_directory_resolution PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sync_posix_directory_resolution PRIVATE
  -Wall -Wextra -Wpedantic)

# One retained, process/thread-affine directory capability is shared by
# filesystem owners. It centralizes no-symlink absolute traversal, frozen
# identity/credential/mode/mount/namespace attestation, sticky revocation, and
# one internal move-only bridge for descriptor-relative owners that need a
# verified duplicate of the same open file description. Independent-cursor
# observers must reopen and attest a fresh authority instead of using that
# shared-offset bridge.
set(ANONSYNC_SYNC_DIRECTORY_AUTHORITY_SOURCE
  src/sync_directory_authority.cpp)
add_library(anonsync_sync_directory_authority STATIC
  ${ANONSYNC_SYNC_DIRECTORY_AUTHORITY_SOURCE})
target_include_directories(anonsync_sync_directory_authority PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_directory_authority
  PUBLIC
    anonsync_sync_posix_directory_resolution
    anonsync_sync_posix_mount_namespace_authority
    anonsync_process_incarnation
    anonsync_thread_incarnation
  PRIVATE anonsync_sha256_digest)
target_compile_options(anonsync_sync_directory_authority PRIVATE
  -Wall -Wextra -Wpedantic)

# Report and heartbeat publication is a filesystem authority boundary. A small
# allocation-free state owner classifies failures as pre-rename, post-rename
# with indeterminate directory durability, or post-directory-sync. The syscall
# owner consumes that model while keeping both pieces independent of the 15k-line
# sync domain and the operator CLI.
set(ANONSYNC_SYNC_ATOMIC_FILE_PUBLICATION_STATE_SOURCE
  src/sync_atomic_file_publication_state.cpp)
add_library(anonsync_sync_atomic_file_publication_state STATIC
  ${ANONSYNC_SYNC_ATOMIC_FILE_PUBLICATION_STATE_SOURCE})
target_include_directories(anonsync_sync_atomic_file_publication_state PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sync_atomic_file_publication_state PRIVATE
  -Wall -Wextra -Wpedantic)

set(ANONSYNC_SYNC_ATOMIC_FILE_PUBLICATION_SOURCE
  src/sync_atomic_file_publication.cpp)
add_library(anonsync_sync_atomic_file_publication STATIC
  ${ANONSYNC_SYNC_ATOMIC_FILE_PUBLICATION_SOURCE})
target_include_directories(anonsync_sync_atomic_file_publication PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_atomic_file_publication
  PUBLIC
    anonsync_sync_atomic_file_publication_state
    anonsync_sync_posix_directory_resolution
    anonsync_sync_directory_authority
  PRIVATE
    anonsync_process_incarnation
    anonsync_sync_bounded_regular_file)
target_compile_options(anonsync_sync_atomic_file_publication PRIVATE
  -Wall -Wextra -Wpedantic)

# Heartbeats and operator workflow documents become authority only after one
# exact, bounded observation of an opened regular-file object. Keep pathname
# resolution, descriptor type validation, EOF proof, and pre/post snapshot
# comparison in a focused leaf rather than duplicating a hidden helper inside
# the 15k-line sync domain.
set(ANONSYNC_SYNC_BOUNDED_REGULAR_FILE_SOURCE
  src/sync_bounded_regular_file.cpp
  src/sync_posix_descriptor_snapshot.cpp)
add_library(anonsync_sync_bounded_regular_file STATIC
  ${ANONSYNC_SYNC_BOUNDED_REGULAR_FILE_SOURCE})
target_include_directories(anonsync_sync_bounded_regular_file PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_bounded_regular_file PRIVATE
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_bounded_regular_file PRIVATE
  -Wall -Wextra -Wpedantic)

# First production-folder observation leaf. It retains one verified root
# authority, traverses with descriptor-relative no-follow opens, freezes the
# exact bytes and metadata of bounded regular files, and re-attests each
# parent/name after hashing. It deliberately does not publish replica evidence;
# complete-scan absence authority belongs to the durable catalog coordinator.
# Exact atomic-publication recovery names are counted but never surfaced as
# user files after a crash.
set(ANONSYNC_SYNC_REPLICA_FOLDER_OBSERVER_SOURCE
  src/sync_replica_folder_observer.cpp)
add_library(anonsync_sync_replica_folder_observer STATIC
  ${ANONSYNC_SYNC_REPLICA_FOLDER_OBSERVER_SOURCE})
target_include_directories(anonsync_sync_replica_folder_observer PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_folder_observer
  PUBLIC
    anonsync_sync_directory_authority
    anonsync_sync_bounded_regular_file
    anonsync_sync_replica_selective_sync_policy
  PRIVATE
    anonsync_sha256_digest
    anonsync_sync_atomic_file_publication
    anonsync_sync_manifest_validation)
target_compile_options(anonsync_sync_replica_folder_observer PRIVATE
  -Wall -Wextra -Wpedantic)

# One generated deployment identity is shared by the manifest, every SQLite
# role binding, and the product-bound payload marker. Keep randomness and exact
# identity validation in a small leaf so store owners cannot mint substitutes.
set(ANONSYNC_SYNC_REPLICA_DEPLOYMENT_IDENTITY_SOURCE
  src/sync_replica_deployment_identity.cpp)
add_library(anonsync_sync_replica_deployment_identity STATIC
  ${ANONSYNC_SYNC_REPLICA_DEPLOYMENT_IDENTITY_SOURCE})
target_include_directories(anonsync_sync_replica_deployment_identity PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_deployment_identity
  PUBLIC anonsync_sync_replica_model
  PRIVATE
    anonsync_sha256_digest
    anonsync_sync_manifest_validation
    OpenSSL::Crypto)
target_compile_options(anonsync_sync_replica_deployment_identity PRIVATE
  -Wall -Wextra -Wpedantic)

# Bootstrap publishes one exact self-digested deployment authority after all
# selected stores exist. Every operational product command reads this bounded,
# no-symlink document first and derives its complete store set and local identity
# from it instead of accepting independently mixable path arguments.
set(ANONSYNC_SYNC_REPLICA_DEPLOYMENT_MANIFEST_SOURCE
  src/sync_replica_deployment_manifest.cpp)
add_library(anonsync_sync_replica_deployment_manifest STATIC
  ${ANONSYNC_SYNC_REPLICA_DEPLOYMENT_MANIFEST_SOURCE})
target_include_directories(anonsync_sync_replica_deployment_manifest PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_deployment_manifest
  PUBLIC
    anonsync_sync_replica_deployment_identity
    anonsync_sync_replica_model
  PRIVATE
    anonsync_json_parser
    anonsync_sha256_digest
    anonsync_sync_bounded_regular_file
    anonsync_sync_manifest_validation)
target_compile_options(anonsync_sync_replica_deployment_manifest PRIVATE
  -Wall -Wextra -Wpedantic)

# Before any selected store is mutated, bootstrap persists the exact final
# manifest bytes under one deterministic hidden sibling. Interrupted bootstrap
# can therefore be inspected and resumed against one immutable configuration
# instead of guessing which partial stores belong together.
set(ANONSYNC_SYNC_REPLICA_BOOTSTRAP_RECORD_SOURCE
  src/sync_replica_bootstrap_record.cpp)
add_library(anonsync_sync_replica_bootstrap_record STATIC
  ${ANONSYNC_SYNC_REPLICA_BOOTSTRAP_RECORD_SOURCE})
target_include_directories(anonsync_sync_replica_bootstrap_record PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_bootstrap_record
  PUBLIC anonsync_sync_replica_deployment_manifest
  PRIVATE
    anonsync_sha256_digest
    anonsync_sync_atomic_file_publication
    anonsync_sync_bounded_regular_file)
target_compile_options(anonsync_sync_replica_bootstrap_record PRIVATE
  -Wall -Wextra -Wpedantic)

# Every selected SQLite database carries a role-specific application ID plus an
# exact singleton binding to the deployment ID, manifest digest/path, local
# actor, folder, and opened database pathname. Operational owners are composed
# only after this product gate succeeds.
set(ANONSYNC_SYNC_REPLICA_DEPLOYMENT_BINDING_SOURCE
  src/sync_replica_deployment_binding.cpp)
add_library(anonsync_sync_replica_deployment_binding STATIC
  ${ANONSYNC_SYNC_REPLICA_DEPLOYMENT_BINDING_SOURCE})
target_include_directories(anonsync_sync_replica_deployment_binding PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_deployment_binding
  PUBLIC
    anonsync_sync_replica_deployment_identity
    anonsync_sqlite_support
  PRIVATE anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_deployment_binding PRIVATE
  -Wall -Wextra -Wpedantic)
# The replica owner has one specialized composition for a sealed detached
# read-only image. Keep the general model target independent while linking the
# exact deployment attestation implementation into that boundary.
target_link_libraries(anonsync_sync_replica_sqlite_owner PRIVATE
  anonsync_sync_replica_deployment_binding)

# Process-facing SQLite stores are opened through one descriptor-rooted,
# existing-only authority. A sealed bootstrap image has a distinct candidate
# disposition and cannot become operational until its role owner attests it and
# explicitly promotes it to the reviewed WAL profile. Offline exact-schema
# inspection uses the same rooted authority with a read-only VFS and the shared
# hardened query-only connection profile.
set(ANONSYNC_SYNC_REPLICA_OPERATIONAL_DATABASE_SOURCE
  src/sync_replica_operational_database.cpp)
add_library(anonsync_sync_replica_operational_database STATIC
  ${ANONSYNC_SYNC_REPLICA_OPERATIONAL_DATABASE_SOURCE})
target_include_directories(anonsync_sync_replica_operational_database PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_operational_database
  PUBLIC
    anonsync_sqlite_path_security
    anonsync_sqlite_support
  PRIVATE
    anonsync_sync_replica_tls_membership)
target_compile_options(anonsync_sync_replica_operational_database PRIVATE
  -Wall -Wextra -Wpedantic)

# Restart verification metadata is a checksum-sealed acceleration hint, kept in
# a focused leaf so binary-format parsing and exact metadata invariants do not
# expand the already-large payload-store owner. It is never content authority.
add_library(anonsync_sync_replica_file_payload_verification_index STATIC
  src/sync_replica_file_payload_verification_index.cpp)
target_include_directories(anonsync_sync_replica_file_payload_verification_index PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_payload_verification_index
  PRIVATE
    anonsync_sha256_digest
    anonsync_sync_posix_regular_file_snapshot_codec)
target_compile_options(anonsync_sync_replica_file_payload_verification_index PRIVATE
  -Wall -Wextra -Wpedantic)

# Rotating byte-scrub continuation is a fixed-size checksum-framed scheduling
# record. It remains distinct from the complete verification index because
# partial hash state never grants payload authority.
add_library(anonsync_sync_replica_file_payload_scrub_state STATIC
  src/sync_replica_file_payload_scrub_state.cpp)
target_include_directories(anonsync_sync_replica_file_payload_scrub_state PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_payload_scrub_state
  PUBLIC anonsync_resumable_sha256
  PRIVATE
    anonsync_sha256_digest
    anonsync_sync_posix_regular_file_snapshot_codec)
target_compile_options(anonsync_sync_replica_file_payload_scrub_state PRIVATE
  -Wall -Wextra -Wpedantic)

# Staged-prefix terminal verification uses one fixed two-slot checksum journal.
# The journal is computation progress only; final whole-digest comparison and
# exact inode publication remain payload-store authority.
add_library(anonsync_sync_replica_file_payload_terminal_verification_state STATIC
  src/sync_replica_file_payload_terminal_verification_state.cpp)
target_include_directories(anonsync_sync_replica_file_payload_terminal_verification_state PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_payload_terminal_verification_state
  PUBLIC anonsync_resumable_sha256
  PRIVATE
    anonsync_sha256_digest
    anonsync_sync_posix_regular_file_snapshot_codec)
target_compile_options(anonsync_sync_replica_file_payload_terminal_verification_state PRIVATE
  -Wall -Wextra -Wpedantic)

# One fixed-width, checksum-framed retention mark preserves a deletion-free
# candidate observation together with explicit conservative owner policy. It is
# historical evidence only: no parser or caller gains collection authority.
add_library(anonsync_sync_replica_file_payload_retention_mark STATIC
  src/sync_replica_file_payload_retention_mark.cpp)
target_include_directories(anonsync_sync_replica_file_payload_retention_mark PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_payload_retention_mark
  PRIVATE
    anonsync_sha256_digest
    anonsync_sync_posix_regular_file_snapshot_codec)
target_compile_options(anonsync_sync_replica_file_payload_retention_mark PRIVATE
  -Wall -Wextra -Wpedantic)

# Source-side content-defined manifest preparation can otherwise reread up to
# four tebibytes after every service restart. Keep one checksum-framed,
# store-identity-bound active boundary or completed bounded manifest outside the
# broad reconciliation owner. The record is acceleration only: every use still
# reopens and re-proves the exact immutable payload inode.
add_library(anonsync_sync_replica_source_manifest_checkpoint STATIC
  src/sync_replica_source_manifest_checkpoint.cpp)
target_include_directories(anonsync_sync_replica_source_manifest_checkpoint PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_source_manifest_checkpoint
  PUBLIC
    anonsync_resumable_sha256
    anonsync_sync_replica_content_defined_chunker
    anonsync_sync_posix_regular_file_snapshot_codec
  PRIVATE
    anonsync_sha256_digest
    anonsync_sync_manifest_validation)
target_compile_options(anonsync_sync_replica_source_manifest_checkpoint PRIVATE
  -Wall -Wextra -Wpedantic)

# The ordinary completed source-manifest cache is process-local acceleration,
# not another wire or persistence format. Retain one fixed-width cumulative
# chunk vector and lend it directly to the canonical generation-9 response-frame
# assembler; compatibility-only callers may still materialize an owning copy.
add_library(anonsync_sync_replica_reconciliation_compact_manifest STATIC
  src/sync_replica_reconciliation_compact_manifest.cpp)
target_include_directories(
  anonsync_sync_replica_reconciliation_compact_manifest PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(
  anonsync_sync_replica_reconciliation_compact_manifest
  PUBLIC anonsync_sync_replica_reconciliation_protocol
  PRIVATE anonsync_sha256_digest)
target_compile_options(
  anonsync_sync_replica_reconciliation_compact_manifest PRIVATE
  -Wall -Wextra -Wpedantic)

# Sender payload bytes now have one durable, descriptor-relative content owner
# instead of requiring every dispatch caller to retain the complete working set
# in memory. The flat digest namespace remains deliberately bounded and is an
# availability seam. Its exact identity marker now carries a runtime-reproved
# shared/exclusive advisory lease for cooperative owners. Protected scans must
# retain and re-prove the exact locked marker inode; this is not garbage
# collection or a defense against noncooperating writers/filesystems.
set(ANONSYNC_SYNC_REPLICA_FILE_PAYLOAD_STORE_SOURCE
  src/sync_replica_file_payload_store.cpp)
add_library(anonsync_sync_replica_file_payload_store STATIC
  ${ANONSYNC_SYNC_REPLICA_FILE_PAYLOAD_STORE_SOURCE})
target_include_directories(anonsync_sync_replica_file_payload_store PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_payload_store
  PUBLIC
    anonsync_sync_replica_content_defined_chunker
    anonsync_sync_replica_deployment_identity
    anonsync_sync_replica_model
    anonsync_sync_atomic_file_publication
    anonsync_sync_directory_authority
    anonsync_sync_posix_directory_resolution
    anonsync_sync_bounded_regular_file
    anonsync_sync_replica_file_payload_verification_index
    anonsync_sync_replica_file_payload_scrub_state
    anonsync_sync_replica_file_payload_terminal_verification_state
    anonsync_sync_replica_file_payload_retention_mark
    anonsync_sync_replica_source_manifest_checkpoint
  PRIVATE
    anonsync_sha256_digest
    anonsync_resumable_sha256
    anonsync_sync_posix_regular_file_snapshot_codec)
target_compile_options(anonsync_sync_replica_file_payload_store PRIVATE
  -Wall -Wextra -Wpedantic)

# One authenticated bounded pull page joins the share-global SQLite evidence
# owner to the durable content-addressed payload owner. It is intentionally a
# socket-free service seam so direct, Tor, and I2P streams can share it.
set(ANONSYNC_SYNC_REPLICA_RECONCILIATION_SERVICE_SOURCE
  src/sync_replica_reconciliation_service.cpp)
add_library(anonsync_sync_replica_reconciliation_service STATIC
  ${ANONSYNC_SYNC_REPLICA_RECONCILIATION_SERVICE_SOURCE})
target_include_directories(anonsync_sync_replica_reconciliation_service PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_reconciliation_service PUBLIC
  anonsync_sync_replica_delivery_channel
  anonsync_sync_replica_file_payload_store
  anonsync_sync_replica_reconciliation_compact_manifest
  anonsync_sync_replica_reconciliation_protocol
  anonsync_sync_replica_sqlite_owner
  PRIVATE
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_reconciliation_service PRIVATE
  -Wall -Wextra -Wpedantic)

# First production-facing configured-folder bridge. It holds one exact regular
# file observation beneath a retained Linux root, captures the replica path
# heads before hashing, stages the immutable payload, publishes through the
# destination-free guarded boundary, and records a restart-stable SQLite path
# mapping. It refuses replica-ahead and populated-target ambiguity rather than
# laundering causality. It deliberately does not infer deletion or create peer
# outbox work.
set(ANONSYNC_SYNC_REPLICA_FOLDER_SCAN_OWNER_SOURCE
  src/sync_replica_folder_scan_owner.cpp)
add_library(anonsync_sync_replica_folder_scan_owner STATIC
  ${ANONSYNC_SYNC_REPLICA_FOLDER_SCAN_OWNER_SOURCE})
target_include_directories(anonsync_sync_replica_folder_scan_owner PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_folder_scan_owner
  PUBLIC
    anonsync_sync_replica_deployment_binding
    anonsync_sync_replica_file_payload_store
    anonsync_sync_replica_selective_sync_policy
    anonsync_sync_replica_sqlite_owner
  PRIVATE
    anonsync_sha256_digest
    anonsync_sync_atomic_file_publication
    anonsync_sync_bounded_regular_file
    anonsync_sync_directory_authority
    anonsync_sync_replica_folder_observer
    anonsync_sync_manifest_validation
    anonsync_sync_posix_directory_resolution
    anonsync_sqlite_support)
target_compile_options(anonsync_sync_replica_folder_scan_owner PRIVATE
  -Wall -Wextra -Wpedantic)

# One manifest-derived process boundary for the configured folder. The catalog
# pathname is deterministic beside the selected replica database; no second
# operator-selected configuration source can silently split the store set.
set(ANONSYNC_SYNC_REPLICA_FOLDER_PROCESS_SOURCE
  src/sync_replica_folder_process.cpp)
add_library(anonsync_sync_replica_folder_process STATIC
  ${ANONSYNC_SYNC_REPLICA_FOLDER_PROCESS_SOURCE})
target_include_directories(anonsync_sync_replica_folder_process PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_folder_process
  PUBLIC
    anonsync_sync_replica_deployment_binding
    anonsync_sync_replica_deployment_manifest
    anonsync_sync_replica_file_payload_store
    anonsync_sync_replica_folder_scan_owner
    anonsync_sync_replica_operational_database)
target_compile_options(anonsync_sync_replica_folder_process PRIVATE
  -Wall -Wextra -Wpedantic)

# File-effect identity is a small structural leaf shared by the durable effect
# owner and its wire receipt protocol. Keeping it outside SQLite prevents the
# same effect from acquiring two subtly different IDs at composition seams.
set(ANONSYNC_SYNC_REPLICA_FILE_EFFECT_IDENTITY_SOURCE
  src/sync_replica_file_effect_identity.cpp)
add_library(anonsync_sync_replica_file_effect_identity STATIC
  ${ANONSYNC_SYNC_REPLICA_FILE_EFFECT_IDENTITY_SOURCE})
target_include_directories(anonsync_sync_replica_file_effect_identity PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_effect_identity PUBLIC
  anonsync_sync_replica_model
  PRIVATE anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_file_effect_identity PRIVATE
  -Wall -Wextra -Wpedantic)

# Effect-terminal file delivery wraps the exact evidence attempt in a bounded
# payload frame and emits a distinct receipt that cannot retire sender intent
# until receiver publication is durable.
set(ANONSYNC_SYNC_REPLICA_FILE_DELIVERY_PROTOCOL_SOURCE
  src/sync_replica_file_delivery_protocol.cpp)
add_library(anonsync_sync_replica_file_delivery_protocol STATIC
  ${ANONSYNC_SYNC_REPLICA_FILE_DELIVERY_PROTOCOL_SOURCE})
target_include_directories(anonsync_sync_replica_file_delivery_protocol PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_delivery_protocol PUBLIC
  anonsync_sync_replica_delivery_protocol
  anonsync_sync_replica_file_effect_identity
  PRIVATE anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_file_delivery_protocol PRIVATE
  -Wall -Wextra -Wpedantic)

# Receiver file effects have authority distinct from causal evidence admission.
# A dedicated SQLite owner stages exact payload bytes, publishes immutable files
# through the atomic namespace owner, and reconciles post-rename/pre-mark crashes
# before exposing a terminal effect state.
set(ANONSYNC_SYNC_REPLICA_FILE_EFFECT_SQLITE_OWNER_SOURCE
  src/sync_replica_file_effect_sqlite_owner.cpp)
add_library(anonsync_sync_replica_file_effect_sqlite_owner STATIC
  ${ANONSYNC_SYNC_REPLICA_FILE_EFFECT_SQLITE_OWNER_SOURCE})
target_include_directories(anonsync_sync_replica_file_effect_sqlite_owner PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_effect_sqlite_owner PUBLIC
  anonsync_sync_replica_model
  anonsync_sync_replica_file_effect_identity
  anonsync_sqlite_support
  anonsync_sync_atomic_file_publication
  PRIVATE anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_file_effect_sqlite_owner PRIVATE
  -Wall -Wextra -Wpedantic)

# The first effect-terminal composition service deliberately remains file-only.
# It stages bytes before evidence admission, publishes only an unambiguous active
# primary, and settles sender intent only from a durable publication receipt.
set(ANONSYNC_SYNC_REPLICA_FILE_DELIVERY_SERVICE_SOURCE
  src/sync_replica_file_delivery_service.cpp
  src/sync_replica_file_payload_snapshot.cpp)
add_library(anonsync_sync_replica_file_delivery_service STATIC
  ${ANONSYNC_SYNC_REPLICA_FILE_DELIVERY_SERVICE_SOURCE})
target_include_directories(anonsync_sync_replica_file_delivery_service PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_delivery_service PUBLIC
  anonsync_sync_replica_file_delivery_protocol
  anonsync_sync_replica_delivery_service
  anonsync_sync_replica_file_effect_sqlite_owner
  anonsync_sync_replica_file_payload_store
  PRIVATE anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_file_delivery_service PRIVATE
  -Wall -Wextra -Wpedantic)

# Narrow first-prefix composition owner. It freezes one canonical File frame,
# re-attests the exact SQLite claim and live TLS channel, retains the writer
# guard through only the encrypted 8-byte record prefix, then releases SQLite
# and returns one move-only pollable body continuation. Prefix or local TLS
# completion is deliberately not mislabeled as receiver receipt.
set(ANONSYNC_SYNC_REPLICA_FILE_TLS_DISPATCH_SOURCE
  src/sync_replica_file_tls_dispatch.cpp)
add_library(anonsync_sync_replica_file_tls_dispatch STATIC
  ${ANONSYNC_SYNC_REPLICA_FILE_TLS_DISPATCH_SOURCE})
target_include_directories(anonsync_sync_replica_file_tls_dispatch PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_tls_dispatch PUBLIC
  anonsync_sync_replica_file_delivery_service
  anonsync_sync_replica_tls_poll)
target_compile_options(anonsync_sync_replica_file_tls_dispatch PRIVATE
  -Wall -Wextra -Wpedantic)

# Receiver-owned counterpart to the guarded sender dispatch. It preflights
# effect/channel authority before application bytes, consumes one complete
# strict-nonblocking request, invokes the durable file service, then re-attests
# the same channel and emits the exact receipt under an independent absolute
# response deadline. A move-only session freezes both deadlines and exclusively
# terminalizes the local application capability after one conversation.
set(ANONSYNC_SYNC_REPLICA_FILE_TLS_EXCHANGE_SOURCE
  src/sync_replica_file_tls_exchange.cpp)
add_library(anonsync_sync_replica_file_tls_exchange STATIC
  ${ANONSYNC_SYNC_REPLICA_FILE_TLS_EXCHANGE_SOURCE})
target_include_directories(anonsync_sync_replica_file_tls_exchange PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_tls_exchange PUBLIC
  anonsync_sync_replica_file_delivery_service
  anonsync_sync_replica_tls_poll)
target_compile_options(anonsync_sync_replica_file_tls_exchange PRIVATE
  -Wall -Wextra -Wpedantic)

# Multi-record share catch-up over the same authenticated TLS record owner used
# by file delivery. One explicit round-trip ceiling and one source-reset ceiling
# bound the conversation; the socket/listener and daemon lifetime stay outside.
set(ANONSYNC_SYNC_REPLICA_RECONCILIATION_TLS_EXCHANGE_SOURCE
  src/sync_replica_reconciliation_tls_exchange.cpp)
add_library(anonsync_sync_replica_reconciliation_tls_exchange STATIC
  ${ANONSYNC_SYNC_REPLICA_RECONCILIATION_TLS_EXCHANGE_SOURCE})
target_include_directories(
  anonsync_sync_replica_reconciliation_tls_exchange PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(
  anonsync_sync_replica_reconciliation_tls_exchange PUBLIC
  anonsync_sync_replica_reconciliation_service
  anonsync_sync_replica_tls_poll)
target_compile_options(
  anonsync_sync_replica_reconciliation_tls_exchange PRIVATE
  -Wall -Wextra -Wpedantic)

# Canonical TLS membership values and their durable append-only SQLite owner
# form an authority leaf independent of listener, OpenSSL, and file-effect
# ownership. Keeping this state machine separate makes policy publication and
# rollback tests rebuild without relinking the accepted-session implementation.
set(ANONSYNC_SYNC_REPLICA_TLS_MEMBERSHIP_SOURCE
  src/sync_replica_tls_membership_snapshot.cpp
  src/sync_replica_tls_policy_sqlite_profile.cpp
  src/sync_replica_tls_membership_sqlite_owner.cpp
  src/sync_replica_tls_membership_anchor_sqlite_owner.cpp
  src/sync_replica_tls_membership_anchored_owner.cpp)
add_library(anonsync_sync_replica_tls_membership STATIC
  ${ANONSYNC_SYNC_REPLICA_TLS_MEMBERSHIP_SOURCE})
target_include_directories(anonsync_sync_replica_tls_membership PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_tls_membership PUBLIC
  anonsync_sqlite_support
  PRIVATE anonsync_sha256_digest
          anonsync_sqlite_path_security)
target_compile_options(anonsync_sync_replica_tls_membership PRIVATE
  -Wall -Wextra -Wpedantic)

# Bounded production connection owners for the causal file-delivery path. The
# receiver binds one exact listener, accepts a nonblocking+CLOEXEC child, drives
# TLS and anchored membership, and owns one durable receive conversation. The
# sender uses numeric-only nonblocking connect, authenticates the expected peer
# before claiming SQLite work, crosses the guarded prefix frontier, applies one
# exact receipt, and closes every socket lifetime. Keep both directions in this
# existing product-spine library instead of creating another one-file archive.
set(ANONSYNC_SYNC_REPLICA_FILE_TLS_SERVER_SOURCE
  src/sync_replica_file_tls_server.cpp
  src/sync_replica_file_tls_client.cpp
  src/sync_replica_peer_tls_exchange.cpp
  src/sync_replica_stream_connector.cpp
  src/sync_replica_numeric_listener.cpp
  src/sync_replica_session_supervisor.cpp)
add_library(anonsync_sync_replica_file_tls_server STATIC
  ${ANONSYNC_SYNC_REPLICA_FILE_TLS_SERVER_SOURCE})
target_include_directories(anonsync_sync_replica_file_tls_server PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_tls_server PUBLIC
  anonsync_sync_replica_file_tls_dispatch
  anonsync_sync_replica_file_tls_exchange
  anonsync_sync_replica_reconciliation_tls_exchange
  anonsync_sync_replica_tls_membership
  anonsync_sync_replica_outbox_clock
  PRIVATE anonsync_sync_stream_socket_deadline_poll
          anonsync_thread_incarnation OpenSSL::SSL OpenSSL::Crypto)
target_compile_options(anonsync_sync_replica_file_tls_server PRIVATE
  -Wall -Wextra -Wpedantic)

# Retained inbound composition for one combined peer. This owner opens only an
# already-bootstrapped deployment, binds one numeric listener, and reuses the
# accepted-session dispatcher without moving store or socket capabilities across
# threads. Service lifetime and retry policy remain outside this library.
add_library(anonsync_sync_replica_peer_server_owner STATIC
  src/sync_replica_peer_server_owner.cpp)
target_include_directories(anonsync_sync_replica_peer_server_owner PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_peer_server_owner
  PUBLIC
    anonsync_sync_replica_file_tls_server
  PRIVATE
    anonsync_sync_replica_deployment_binding
    anonsync_sync_replica_deployment_identity
    anonsync_sync_replica_file_effect_sqlite_owner
    anonsync_sync_replica_file_payload_store
    anonsync_sync_replica_operational_database
    anonsync_sync_replica_reconciliation_service
    anonsync_sync_replica_sqlite_owner
    anonsync_sync_replica_tls_membership)
target_compile_options(anonsync_sync_replica_peer_server_owner PRIVATE
  -Wall -Wextra -Wpedantic)

# One repeatable product operation composes the configured local folder with one
# authenticated share-global pull and one post-pull apply. It retains route and
# TLS configuration for future service reuse but owns no retry or daemon loop.
set(ANONSYNC_SYNC_REPLICA_SYNC_ONCE_SOURCE
  src/sync_replica_sync_once.cpp)
add_library(anonsync_sync_replica_sync_once STATIC
  ${ANONSYNC_SYNC_REPLICA_SYNC_ONCE_SOURCE})
target_include_directories(anonsync_sync_replica_sync_once PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_sync_once
  PUBLIC
    anonsync_sync_replica_file_tls_server
    anonsync_sync_replica_folder_process
    anonsync_sync_replica_reconciliation_service
  PRIVATE
    anonsync_sha256_digest
    anonsync_sync_manifest_validation)
target_compile_options(anonsync_sync_replica_sync_once PRIVATE
  -Wall -Wextra -Wpedantic)

# Bounded filesystem wake hints for the retained service. Linux uses one
# nonblocking inotify descriptor on the service-owner thread; the event stream
# never becomes scan, deletion, rename, or publication authority.
add_library(anonsync_sync_replica_folder_wake STATIC
  src/sync_replica_folder_wake.cpp)
target_include_directories(anonsync_sync_replica_folder_wake PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sync_replica_folder_wake PRIVATE
  -Wall -Wextra -Wpedantic)

# Restartable two-direction peer service. One configured-folder lifetime owns
# both the outbound cycle and retained listener; deterministic actor turn-taking
# avoids symmetric redial lockstep without violating SQLite execution affinity.
add_library(anonsync_sync_replica_peer_service STATIC
  src/sync_replica_historical_version_inventory_json.cpp
  src/sync_replica_i2p_ingress_worker.cpp
  src/sync_replica_peer_service.cpp)
target_include_directories(anonsync_sync_replica_peer_service PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_peer_service
  PUBLIC
    anonsync_sync_replica_peer_server_owner
    anonsync_sync_replica_sync_once
    anonsync_sync_replica_folder_wake
  PRIVATE Threads::Threads)
target_compile_options(anonsync_sync_replica_peer_service PRIVATE
  -Wall -Wextra -Wpedantic)
target_compile_definitions(anonsync_sync_replica_peer_service PUBLIC
  "ANONSYNC_INSTALLED_SERVICE_MAXIMUM_NETWORK_STEP_SECONDS=${ANONSYNC_INSTALLED_SERVICE_MAXIMUM_NETWORK_STEP_SECONDS}"
  "ANONSYNC_INSTALLED_SERVICE_STOP_TIMEOUT_SECONDS=${ANONSYNC_INSTALLED_SERVICE_STOP_TIMEOUT_SECONDS}")

# One process may own a deployment's retained sync loop at a time. The lock is
# independent of CLI/config/status/listen path choices, preventing two local
# writers from silently opening the same SQLite/store set.
add_library(anonsync_sync_replica_peer_service_singleton STATIC
  src/sync_replica_peer_service_singleton.cpp)
target_include_directories(anonsync_sync_replica_peer_service_singleton PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_peer_service_singleton
  PUBLIC anonsync_sync_replica_deployment_manifest
  PRIVATE anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_peer_service_singleton PRIVATE
  -Wall -Wextra -Wpedantic)

# Native systemd notification datagrams for the existing foreground owner. This
# is intentionally a small Linux capability leaf, not a daemon wrapper and not
# a libsystemd dependency.
add_library(anonsync_sync_systemd_notify STATIC
  src/sync_systemd_notify.cpp)
target_include_directories(anonsync_sync_systemd_notify PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sync_systemd_notify PRIVATE
  -Wall -Wextra -Wpedantic)

# Strict owner-only JSON configuration for one retained linked peer. Both this
# durable form and the legacy CLI materialize the same service launch type.
add_library(anonsync_sync_replica_peer_service_configuration STATIC
  src/sync_replica_peer_service_configuration.cpp)
target_include_directories(
  anonsync_sync_replica_peer_service_configuration PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(
  anonsync_sync_replica_peer_service_configuration
  PUBLIC
    anonsync_sync_replica_peer_service
  PRIVATE
    anonsync_json_parser
    anonsync_sha256_digest
    anonsync_sync_bounded_regular_file
    anonsync_sync_local_status_socket
    anonsync_sync_manifest_validation
    anonsync_sync_replica_deployment_manifest
    anonsync_sync_replica_file_tls_server)
target_compile_options(
  anonsync_sync_replica_peer_service_configuration PRIVATE
  -Wall -Wextra -Wpedantic)

# Exact per-user configuration/runtime layout consumed by the installed
# linked-peer unit. This is a descriptor-relative namespace owner, not a shell
# installer and not a second service lifecycle.
add_library(anonsync_sync_linked_peer_user_layout STATIC
  src/sync_linked_peer_user_layout.cpp)
target_include_directories(anonsync_sync_linked_peer_user_layout PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_linked_peer_user_layout PRIVATE
  anonsync_sync_manifest_validation)
target_compile_options(anonsync_sync_linked_peer_user_layout PRIVATE
  -Wall -Wextra -Wpedantic)

# Exact co-installed executable composition for the first-share workflow. This
# leaf never invokes a shell or searches PATH; it resolves only a regular-file
# sibling of the running binary and captures stdout under an explicit bound.
add_library(anonsync_sync_sibling_process STATIC
  src/sync_sibling_process.cpp)
target_include_directories(anonsync_sync_sibling_process PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(anonsync_sync_sibling_process PRIVATE
  -Wall -Wextra -Wpedantic)

# Explicit public-card exchange and local admission for one linked-peer
# instance. Cards carry only signed public identity; durable membership and the
# peer trust anchor are created only by the local admission call.
add_library(anonsync_sync_linked_peer_pairing STATIC
  src/sync_linked_peer_pairing.cpp)
target_include_directories(anonsync_sync_linked_peer_pairing PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_linked_peer_pairing
  PUBLIC
    anonsync_sync_linked_peer_user_layout
    anonsync_sync_replica_deployment_manifest
    anonsync_sync_replica_tls_membership
  PRIVATE
    anonsync_json_parser
    anonsync_sha256_digest
    anonsync_sync_atomic_file_publication
    anonsync_sync_bounded_regular_file
    anonsync_sync_manifest_validation
    anonsync_sync_replica_deployment_binding
    anonsync_sync_replica_operational_database
    OpenSSL::Crypto)
target_compile_options(anonsync_sync_linked_peer_pairing PRIVATE
  -Wall -Wextra -Wpedantic)

# One CLI-independent local-share setup owner used by both first-share creation
# and second-peer join. It composes only exact co-installed siblings plus the
# shipping folder/pairing owners; the CLI no longer owns a parallel bootstrap.
add_library(anonsync_sync_local_share_setup STATIC
  src/sync_local_share_setup.cpp)
target_include_directories(anonsync_sync_local_share_setup PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_local_share_setup
  PUBLIC
    anonsync_sync_linked_peer_pairing
    anonsync_sync_linked_peer_user_layout
    anonsync_sync_replica_folder_process
  PRIVATE
    anonsync_sync_manifest_validation
    anonsync_sync_replica_bootstrap_record
    anonsync_sync_replica_deployment_manifest
    anonsync_sync_sibling_process
    OpenSSL::Crypto)
target_compile_options(anonsync_sync_local_share_setup PRIVATE
  -Wall -Wextra -Wpedantic)

# Create-new durable publication for the strict v2 linked-peer document. The
# published bytes are reopened through the shipping reader before success.
add_library(anonsync_sync_replica_peer_service_provisioning STATIC
  src/sync_replica_peer_service_provisioning.cpp)
target_include_directories(
  anonsync_sync_replica_peer_service_provisioning PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(
  anonsync_sync_replica_peer_service_provisioning
  PUBLIC anonsync_sync_replica_peer_service_configuration
  PRIVATE
    anonsync_sync_atomic_file_publication
    anonsync_sync_bounded_regular_file)
target_compile_options(
  anonsync_sync_replica_peer_service_provisioning PRIVATE
  -Wall -Wextra -Wpedantic)

# Presentation-only accounting and immutable status rendering stay outside the
# service owner so the CLI does not become a second scheduler.
add_library(anonsync_sync_replica_peer_service_status STATIC
  src/sync_replica_peer_service_status.cpp)
target_include_directories(anonsync_sync_replica_peer_service_status PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_peer_service_status PUBLIC
  anonsync_sync_replica_peer_service)
target_compile_options(anonsync_sync_replica_peer_service_status PRIVATE
  -Wall -Wextra -Wpedantic)

# Explicit Linux process measurement for the current one-process-per-share
# product shape.  smaps_rollup and rusage are diagnostic evidence only; this
# leaf owns no service, filesystem, SQLite, TLS, or scheduler capability.
add_library(anonsync_sync_linux_process_resources STATIC
  src/sync_linux_process_resources.cpp)
target_include_directories(anonsync_sync_linux_process_resources PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_linux_process_resources PRIVATE
  anonsync_json_parser)
target_compile_options(anonsync_sync_linux_process_resources PRIVATE
  -Wall -Wextra -Wpedantic)

# Owner-only Unix status and one-way drain front end. Its worker owns only a
# socket, copied JSON bytes, and an atomic drain latch; never service, TLS,
# folder, or SQLite capabilities.
add_library(anonsync_sync_local_status_socket STATIC
  src/sync_local_status_socket.cpp)
target_include_directories(anonsync_sync_local_status_socket PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_local_status_socket
  PUBLIC
    anonsync_sync_manifest_validation
  PRIVATE
    anonsync_json_parser
    anonsync_sync_directory_authority
    anonsync_sync_linux_process_resources
    Threads::Threads)
target_compile_options(anonsync_sync_local_status_socket PRIVATE
  -Wall -Wextra -Wpedantic)

# Directory identity, ownership/mode policy, mount observations, path traversal,
# and descriptor lifetime form a smaller capability than the full ledger family.
# Keep that proof in its own dependency leaf so namespace mutation cannot silently
# bypass the frozen parent-directory attestation.
set(ANONSYNC_LOCAL_JSONL_REPLAY_DIRECTORY_AUTHORITY_SOURCE
  src/persistence/local_jsonl_replay_directory_authority.cpp)
add_library(anonsync_local_jsonl_replay_directory_authority STATIC
  ${ANONSYNC_LOCAL_JSONL_REPLAY_DIRECTORY_AUTHORITY_SOURCE})
target_include_directories(anonsync_local_jsonl_replay_directory_authority PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_local_jsonl_replay_directory_authority PRIVATE
  anonsync_sync_directory_authority)
target_compile_options(anonsync_local_jsonl_replay_directory_authority PRIVATE
  -Wall -Wextra -Wpedantic)

# The local JSONL ledger is a namespace authority, not a pathname string.
# Compose the frozen directory capability with reserved member names and lock,
# observation, publication, replacement, and retirement operations.
set(ANONSYNC_LOCAL_JSONL_REPLAY_NAMESPACE_SOURCE
  src/persistence/local_jsonl_replay_namespace.cpp)
add_library(anonsync_local_jsonl_replay_namespace STATIC
  ${ANONSYNC_LOCAL_JSONL_REPLAY_NAMESPACE_SOURCE})
target_include_directories(anonsync_local_jsonl_replay_namespace PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_local_jsonl_replay_namespace PRIVATE
  anonsync_local_jsonl_replay_directory_authority
  anonsync_process_incarnation
  anonsync_thread_incarnation
  anonsync_sync_bounded_regular_file
  anonsync_local_jsonl_replay_publication)
target_compile_options(anonsync_local_jsonl_replay_namespace PRIVATE
  -Wall -Wextra -Wpedantic)

# Exact file bytes are still only an observation. Keep canonical heartbeat
# schema, stale-horizon arithmetic, lifecycle state coherence, and owner-release
# finality in a second focused leaf. The sync domain binds the decoded document
# to checkpoint path, session, and the exact durable owner generation.
set(ANONSYNC_SYNC_DAEMON_HEARTBEAT_DOCUMENT_SOURCE
  src/sync_daemon_heartbeat_document.cpp)
add_library(anonsync_sync_daemon_heartbeat_document STATIC
  ${ANONSYNC_SYNC_DAEMON_HEARTBEAT_DOCUMENT_SOURCE})
target_include_directories(anonsync_sync_daemon_heartbeat_document PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_daemon_heartbeat_document PUBLIC
  anonsync_process_identity_observation)
target_compile_options(anonsync_sync_daemon_heartbeat_document PRIVATE
  -Wall -Wextra -Wpedantic)

# Freeze the broad daemon orchestration snapshot into the exact owning value
# accepted by the codec. This is the sole dependency edge from the public
# daemon option/result model into the heartbeat publication schema.
set(ANONSYNC_SYNC_DAEMON_HEARTBEAT_PUBLICATION_SOURCE
  src/sync_daemon_heartbeat_publication.cpp)
add_library(anonsync_sync_daemon_heartbeat_publication STATIC
  ${ANONSYNC_SYNC_DAEMON_HEARTBEAT_PUBLICATION_SOURCE})
target_include_directories(anonsync_sync_daemon_heartbeat_publication PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_daemon_heartbeat_publication PUBLIC
  anonsync_sync_daemon_heartbeat_document)
target_compile_options(anonsync_sync_daemon_heartbeat_publication PRIVATE
  -Wall -Wextra -Wpedantic)

# Durable replay-ledger reset and immutable receipt publication are two
# resources, not one transaction. This focused protocol owner binds the exact
# request-derived document before reset, verifies returned durable evidence,
# and exposes one typed recovery decision instead of caller-owned booleans.
set(ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_RECEIPT_PROTOCOL_SOURCE
  src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp)
add_library(anonsync_sqlite_replay_ledger_reset_receipt_protocol STATIC
  ${ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_RECEIPT_PROTOCOL_SOURCE})
target_include_directories(
  anonsync_sqlite_replay_ledger_reset_receipt_protocol PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(
  anonsync_sqlite_replay_ledger_reset_receipt_protocol
  PUBLIC
    anonsync_sqlite_replay_ledger_reset
    anonsync_sync_atomic_file_publication
  PRIVATE
    anonsync_sqlite_replay_ledger_reset_documents
    anonsync_sha256_digest)
target_compile_options(
  anonsync_sqlite_replay_ledger_reset_receipt_protocol PRIVATE
  -Wall -Wextra -Wpedantic)

# Sealed SQLite images publish their exact resident bytes through the same
# capability-bound atomic owner used by reports. Keep the dependency one-way:
# publication reuses only the process-incarnation primitive and remains
# independent of SQLite state, storage, and snapshot interpretation.
target_link_libraries(anonsync_sqlite_snapshot_seal PUBLIC
  anonsync_sync_atomic_file_publication)

set(ANONSYNC_CORE_SOURCES
  src/sync_domain.cpp
  src/sync_checkpoint_scheduler.cpp
  src/sync_peer_ingress_projection.cpp
  src/sync_peer_ingress_lifecycle.cpp
  src/sync_peer_ingress_wire.cpp
  src/sync_peer_wire_codec.cpp
  src/sync_peer_ingress_payload_store.cpp
  src/sync_peer_ingress_retention.cpp
  src/sync_peer_ingress_claim.cpp
  src/sync_peer_ingress_reconciliation.cpp
  src/sync_operator_cli.cpp
  src/sync_peer_ingestion.cpp
  src/sync_peer_local_transport.cpp
  src/json_codec_crypto.cpp
  src/contracts_policy_profiles.cpp
  src/normalizer_envelopes.cpp
  src/replay_ledger.cpp
  src/sqlite_replay_ledger.cpp
  src/jwt_policy_decision.cpp
  src/reporting.cpp
  src/runner.cpp)
foreach(ANONSYNC_INVARIANT_OWNED_SOURCE
    "${ANONSYNC_PROCESS_INCARNATION_SOURCE}"
    "${ANONSYNC_PROCESS_IDENTITY_OBSERVATION_SOURCE}"
    "${ANONSYNC_PEER_INGRESS_CONNECTION_PROFILE_SOURCE}"
    "${ANONSYNC_SQLITE_EXACT_VALUE_SOURCE}"
    "${ANONSYNC_INGRESS_SENDER_REPLAY_RECORD_SOURCE}"
    "${ANONSYNC_SQLITE_REPLAY_LEDGER_SCHEMA_CONTRACT_SOURCE}"
    "${ANONSYNC_SQLITE_PATH_SECURITY_SOURCE}"
    "${ANONSYNC_SQLITE_SNAPSHOT_GEOMETRY_SOURCE}"
    "${ANONSYNC_SQLITE_LIVE_BACKUP_SOURCE}"
    "${ANONSYNC_SQLITE_RETAINED_CALLBACK_CLAIM_SOURCE}"
    "${ANONSYNC_SQLITE_VERIFICATION_BUDGET_SOURCE}"
    "${ANONSYNC_SQLITE_BUSY_HANDLER_OWNER_SOURCE}"
    "${ANONSYNC_SQLITE_SNAPSHOT_SEAL_SOURCE}"
    "${ANONSYNC_LOCAL_JSONL_REPLAY_PUBLICATION_SOURCE}"
    "${ANONSYNC_LOCAL_JSONL_REPLAY_DIRECTORY_AUTHORITY_SOURCE}"
    "${ANONSYNC_LOCAL_JSONL_REPLAY_NAMESPACE_SOURCE}"
    "${ANONSYNC_EFFECT_TRANSITION_INTENT_PUBLICATION_SOURCE}"
    "${ANONSYNC_EFFECT_TRANSITION_RECORD_MATERIAL_SOURCE}"
    "${ANONSYNC_SQLITE_SNAPSHOT_MANIFEST_PUBLICATION_SOURCE}"
    "${ANONSYNC_CANONICAL_PROJECTION_VERIFIER_SOURCE}"
    "${ANONSYNC_SQLITE_PROJECTION_DECODER_SOURCE}"
    "${ANONSYNC_SQLITE_EXECUTION_AFFINITY_SOURCE}"
    "${ANONSYNC_SQLITE_DATABASE_MUTEX_GUARD_SOURCE}"
    "${ANONSYNC_SQLITE_BUSY_TIMEOUT_MUTATION_GUARD_SOURCE}"
    "${ANONSYNC_SHA256_DIGEST_SOURCE}"
    "${ANONSYNC_JSON_PARSER_SOURCE}"
    "${ANONSYNC_SYNC_PEER_TRANSPORT_DIGEST_BOUND_FRAME_SOURCE}"
    "${ANONSYNC_SECURITY_TUPLE_DIGEST_SOURCE}"
    "${ANONSYNC_SYNC_MANIFEST_VALIDATION_SOURCE}"
    "${ANONSYNC_SYNC_MANIFEST_STREAM_DECODER_SOURCE}"
    "${ANONSYNC_SYNC_SQLITE_MANIFEST_CHUNK_SUBSET_SOURCE}"
    "${ANONSYNC_SYNC_SQLITE_SIDECAR_CLAIMED_PATH_SNAPSHOT_SOURCE}"
    "${ANONSYNC_SYNC_MANIFEST_IDENTITY_SOURCE}"
    "${ANONSYNC_SYNC_CONFLICT_RESOLUTION_SOURCE}"
    "${ANONSYNC_SYNC_REPLICA_MODEL_SOURCE}"
    "${ANONSYNC_SYNC_REPLICA_OUTBOX_LEASE_SOURCE}"
    "${ANONSYNC_SYNC_REPLICA_NETWORK_SIMULATOR_SOURCE}"
    "${ANONSYNC_SQLITE_REPLAY_LEDGER_WRITE_GATE_SOURCE}"
    "${ANONSYNC_SQLITE_REPLAY_LEDGER_RESTORE_LOCK_SOURCE}"
    "${ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_SOURCE}"
    "${ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_DOCUMENTS_SOURCE}"
    "${ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_RECEIPT_PROTOCOL_SOURCE}"
    "${ANONSYNC_SQLITE_SCHEMA_IDENTITY_SOURCE}"
    "${ANONSYNC_SYNC_CHECKPOINT_SCHEDULER_POLICY_SOURCE}"
    "${ANONSYNC_SYNC_CHECKPOINT_OWNER_FENCE_POLICY_SOURCE}"
    "${ANONSYNC_SYNC_CHECKPOINT_OWNER_SCHEMA_SOURCE}"
    "${ANONSYNC_SYNC_CHECKPOINT_OWNER_FENCE_SOURCE}"
    "${ANONSYNC_SYNC_ATOMIC_FILE_PUBLICATION_STATE_SOURCE}"
    "${ANONSYNC_SYNC_ATOMIC_FILE_PUBLICATION_SOURCE}"
    "${ANONSYNC_SYNC_BOUNDED_REGULAR_FILE_SOURCE}"
    "${ANONSYNC_SYNC_REPLICA_DEPLOYMENT_MANIFEST_SOURCE}"
    "${ANONSYNC_SYNC_DAEMON_HEARTBEAT_DOCUMENT_SOURCE}"
    "${ANONSYNC_SYNC_DAEMON_HEARTBEAT_PUBLICATION_SOURCE}"
    ${ANONSYNC_PEER_INGRESS_SCHEMA_SOURCES})
  list(FIND ANONSYNC_CORE_SOURCES "${ANONSYNC_INVARIANT_OWNED_SOURCE}"
    ANONSYNC_INVARIANT_SOURCE_IN_CORE_INDEX)
  if(NOT ANONSYNC_INVARIANT_SOURCE_IN_CORE_INDEX EQUAL -1)
    message(FATAL_ERROR
      "invariant-owned persistence boundary must remain outside anonsync_core_lib: ${ANONSYNC_INVARIANT_OWNED_SOURCE}")
  endif()
endforeach()
add_library(anonsync_core_lib STATIC ${ANONSYNC_CORE_SOURCES})
target_include_directories(anonsync_core_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(anonsync_core_lib
  PUBLIC OpenSSL::Crypto anonsync_sqlite_support
  PRIVATE
    anonsync_peer_ingress_connection_profile
    anonsync_sqlite_exact_value
    anonsync_ingress_sender_replay_record
    anonsync_sqlite_replay_ledger_schema_contract
    anonsync_sqlite_path_security
    anonsync_sqlite_snapshot_geometry
    anonsync_sqlite_live_backup
    anonsync_sqlite_verification_budget
    anonsync_sqlite_busy_handler_owner
    anonsync_sqlite_snapshot_seal
    anonsync_local_jsonl_replay_publication
    anonsync_local_jsonl_replay_namespace
    anonsync_effect_transition_intent_publication
    anonsync_effect_transition_record_material
    anonsync_sqlite_snapshot_manifest_publication
    anonsync_sha256_digest
    anonsync_json_parser
    anonsync_sync_peer_transport_digest_bound_frame
    anonsync_sync_manifest_validation
    anonsync_sync_manifest_stream_decoder
    anonsync_sync_sqlite_manifest_chunk_subset
    anonsync_sync_manifest_identity
    anonsync_sync_sqlite_sidecar_claimed_path_snapshot
    anonsync_sqlite_replay_ledger_write_gate
    anonsync_sqlite_replay_ledger_restore_lock
    anonsync_sqlite_replay_ledger_reset
    anonsync_sqlite_replay_ledger_reset_documents
    anonsync_sqlite_replay_ledger_reset_receipt_protocol
    anonsync_peer_ingress_schema
    anonsync_sync_checkpoint_scheduler_policy
    anonsync_sync_checkpoint_owner_fence
    anonsync_sync_atomic_file_publication
    anonsync_sync_bounded_regular_file
    anonsync_sync_daemon_heartbeat_document
    anonsync_sync_daemon_heartbeat_publication
    anonsync_sync_conflict_resolution
    anonsync_process_identity_observation
    anonsync_canonical_projection_verifier
    anonsync_sqlite_projection_decoder)
if(ANONSYNC_USE_BUNDLED_SQLITE)
  target_compile_definitions(anonsync_core_lib PRIVATE ANONSYNC_BUNDLED_SQLITE=1)
endif()
target_compile_options(anonsync_core_lib PRIVATE -Wall -Wextra -Wpedantic)

# Both test-process wrappers share one compiled owner for exact leader PID and
# process-group authority. Keep wait observation, group signaling, exact reap,
# and terminal authority consumption in that leaf target; wrapper translation
# units own only spawn policy, deadlines, and optional output descriptors.
if(UNIX)
  add_library(anonsync_test_process_topology_owner STATIC
    tests/test_process_topology_owner.cpp)
  target_include_directories(anonsync_test_process_topology_owner PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/tests)
  target_compile_options(anonsync_test_process_topology_owner PRIVATE
    -Wall -Wextra -Wpedantic)

  add_library(anonsync_inherited_test_process STATIC
    tests/inherited_test_process.cpp)
  target_include_directories(anonsync_inherited_test_process PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/tests)
  target_link_libraries(anonsync_inherited_test_process PRIVATE
    anonsync_test_process_topology_owner)
  target_compile_options(anonsync_inherited_test_process PRIVATE
    -Wall -Wextra -Wpedantic)

  add_executable(anonsync_inherited_test_process_test
    tests/inherited_test_process_test.cpp)
  target_link_libraries(anonsync_inherited_test_process_test PRIVATE
    anonsync_inherited_test_process)
  target_compile_options(anonsync_inherited_test_process_test PRIVATE
    -Wall -Wextra -Wpedantic)

  if(CMAKE_SYSTEM_NAME STREQUAL "Linux" AND
      CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    # A deterministic syscall-script oracle wraps only this executable's
    # topology-owner references. It proves transition/error ordering without
    # relying on PID reuse, scheduler timing, or external tracing tools.
    add_executable(anonsync_test_process_topology_owner_test
      tests/test_process_topology_owner_test.cpp)
    target_link_libraries(anonsync_test_process_topology_owner_test PRIVATE
      anonsync_test_process_topology_owner)
    target_link_options(anonsync_test_process_topology_owner_test PRIVATE
      -Wl,--wrap=kill
      -Wl,--wrap=waitid
      -Wl,--wrap=waitpid)
    target_compile_options(anonsync_test_process_topology_owner_test PRIVATE
      -Wall -Wextra -Wpedantic)
  endif()
endif()

# The public runtime library must not carry deterministic corpus generators,
# hostile-database fixtures, RSA key generation, subprocess lock holders, or
# CLI selftest entry points.  Keep that machinery in one-way test-support
# targets that depend on the runtime rather than making every runtime consumer
# compile and link the selftest surface.
set(ANONSYNC_REPORTING_SELFTEST_SOURCE src/reporting_selftests.cpp)
set(ANONSYNC_SYNC_DOMAIN_SELFTEST_SOURCE src/sync_domain_selftests.cpp)
set(ANONSYNC_SQLITE_REPLAY_LEDGER_SELFTEST_SOURCE
  tests/sqlite_replay_ledger_selftests.cpp)
set(ANONSYNC_SELFTEST_SOURCES
  ${ANONSYNC_REPORTING_SELFTEST_SOURCE}
  ${ANONSYNC_SYNC_DOMAIN_SELFTEST_SOURCE}
  ${ANONSYNC_SQLITE_REPLAY_LEDGER_SELFTEST_SOURCE})
foreach(ANONSYNC_SELFTEST_SOURCE IN LISTS ANONSYNC_SELFTEST_SOURCES)
  list(FIND ANONSYNC_CORE_SOURCES "${ANONSYNC_SELFTEST_SOURCE}"
    ANONSYNC_SELFTEST_SOURCE_IN_CORE_INDEX)
  if(NOT ANONSYNC_SELFTEST_SOURCE_IN_CORE_INDEX EQUAL -1)
    message(FATAL_ERROR
      "selftest machinery must remain outside anonsync_core_lib: ${ANONSYNC_SELFTEST_SOURCE}")
  endif()
endforeach()

# Keep independent diagnostic owners independent.  The generic reporting and
# ledger corpora need only the public selftest API; the sync-domain corpus also
# receives the private fixture bridge.  The interface target aggregates both
# only for the diagnostic CLI, so focused corpus wrappers do not compile the
# 8k-line domain model test as collateral build work.
add_library(anonsync_reporting_selftests_lib STATIC
  ${ANONSYNC_REPORTING_SELFTEST_SOURCE})
target_include_directories(anonsync_reporting_selftests_lib PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(anonsync_reporting_selftests_lib PUBLIC anonsync_core_lib)
target_compile_options(anonsync_reporting_selftests_lib PRIVATE
  -Wall -Wextra -Wpedantic)

add_library(anonsync_sync_domain_selftests_lib STATIC
  ${ANONSYNC_SYNC_DOMAIN_SELFTEST_SOURCE})
target_include_directories(anonsync_sync_domain_selftests_lib
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_domain_selftests_lib PUBLIC anonsync_core_lib)
target_compile_options(anonsync_sync_domain_selftests_lib PRIVATE
  -Wall -Wextra -Wpedantic)

# Replay-ledger restore diagnostics are a third owner. They depend on the
# runtime and focused lock owners, never the reverse. The diagnostic CLI alone
# links this corpus and its self-exec process boundary.
add_library(anonsync_sqlite_replay_ledger_selftests_lib STATIC
  ${ANONSYNC_SQLITE_REPLAY_LEDGER_SELFTEST_SOURCE})
target_include_directories(anonsync_sqlite_replay_ledger_selftests_lib
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence
    ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_sqlite_replay_ledger_selftests_lib
  PUBLIC anonsync_core_lib
  PRIVATE
    anonsync_sqlite_replay_ledger_restore_lock
    anonsync_sqlite_replay_ledger_write_gate)
target_compile_options(anonsync_sqlite_replay_ledger_selftests_lib PRIVATE
  -Wall -Wextra -Wpedantic)

add_library(anonsync_selftests_lib INTERFACE)
target_link_libraries(anonsync_selftests_lib INTERFACE
  anonsync_reporting_selftests_lib
  anonsync_sync_domain_selftests_lib
  anonsync_sqlite_replay_ledger_selftests_lib)

if(ANONSYNC_USE_BUNDLED_SQLITE)
  target_compile_definitions(anonsync_reporting_selftests_lib PRIVATE
    ANONSYNC_BUNDLED_SQLITE=1)
  target_compile_definitions(anonsync_sync_domain_selftests_lib PRIVATE
    ANONSYNC_BUNDLED_SQLITE=1)
  target_compile_definitions(anonsync_sqlite_replay_ledger_selftests_lib PRIVATE
    ANONSYNC_BUNDLED_SQLITE=1)
endif()

add_executable(anonsync_core src/anonsync_core.cpp)
target_link_libraries(anonsync_core PRIVATE anonsync_selftests_lib)
target_compile_options(anonsync_core PRIVATE -Wall -Wextra -Wpedantic)

# Offline immutable backup owner for the primary replica SQLite image. The
# owner reuses the bounded live-copy/seal implementation and deployment
# singleton; the shipping CLI is only a JSON/options adapter.
add_library(anonsync_sync_replica_database_backup STATIC
  src/sync_replica_database_backup.cpp
  src/sync_replica_database_replacement.cpp
  src/sync_replica_database_replacement_receipt.cpp)
target_include_directories(anonsync_sync_replica_database_backup PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_database_backup
  PUBLIC
    anonsync_sync_replica_deployment_manifest
    anonsync_sync_replica_sqlite_owner
  PRIVATE
    anonsync_sqlite_snapshot_seal
    anonsync_sqlite_live_backup
    anonsync_sha256_digest
    anonsync_sync_atomic_file_publication
    anonsync_sync_bounded_regular_file
    anonsync_sync_replica_deployment_binding
    anonsync_sync_replica_file_effect_sqlite_owner
    anonsync_sync_replica_folder_process
    anonsync_sync_replica_folder_scan_owner
    anonsync_sync_replica_operational_database
    anonsync_sync_replica_peer_service_singleton
    anonsync_sync_replica_tls_membership
    anonsync_sqlite_support)
target_compile_options(anonsync_sync_replica_database_backup PRIVATE
  -Wall -Wextra -Wpedantic)

# Product-spine executable. Unlike anonsync_core, this binary links no selftest
# implementation libraries: it exposes bounded status/clock operations,
# enqueue, membership, numeric-address sender, and one-shot receiver composition
# over the exact SQLite + durable payload + TLS + filesystem-effect authorities.
add_executable(anonsync_replica src/anonsync_replica.cpp)
target_include_directories(anonsync_replica PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_replica PRIVATE
  anonsync_sqlite_snapshot_seal
  anonsync_sqlite_path_security
  anonsync_sync_replica_bootstrap_record
  anonsync_sync_replica_deployment_binding
  anonsync_sync_replica_deployment_manifest
  anonsync_sync_replica_file_tls_server
  anonsync_sync_replica_file_payload_store
  anonsync_sync_atomic_file_publication
  anonsync_sync_replica_file_effect_sqlite_owner
  anonsync_sync_replica_sqlite_owner
  anonsync_sync_bounded_regular_file
  anonsync_sqlite_support
  anonsync_sha256_digest
  OpenSSL::SSL)
target_compile_options(anonsync_replica PRIVATE -Wall -Wextra -Wpedantic)

# Configured-folder product seam. This stays separate from the courier so the
# folder lifecycle can become a long-running service without turning transport
# command parsing into the owner of local scan/catalog policy.
add_executable(anonsync_folder src/anonsync_folder.cpp)
target_include_directories(anonsync_folder PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_folder PRIVATE
  anonsync_sqlite_snapshot_seal
  anonsync_sqlite_path_security
  anonsync_sync_replica_deployment_binding
  anonsync_sync_replica_deployment_manifest
  anonsync_sync_replica_file_payload_store
  anonsync_sync_replica_folder_process
  anonsync_sync_replica_folder_scan_owner
  anonsync_sync_replica_operational_database
  anonsync_sync_replica_sqlite_owner
  anonsync_sqlite_support)
target_compile_options(anonsync_folder PRIVATE -Wall -Wextra -Wpedantic)

# Bounded product synchronization command. It composes the existing configured
# folder and authenticated courier owners rather than introducing a parallel
# scheduler, and accepts the same direct/Tor/I2P outbound route vocabulary.
add_executable(anonsync_sync src/anonsync_sync.cpp)
target_include_directories(anonsync_sync PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync PRIVATE
  anonsync_sync_replica_database_backup
  anonsync_sha256_digest
  anonsync_sync_atomic_file_publication
  anonsync_sync_bounded_regular_file
  anonsync_sync_linked_peer_pairing
  anonsync_sync_local_share_setup
  anonsync_sync_manifest_validation
  anonsync_sync_replica_deployment_manifest
  anonsync_sync_replica_folder_process
  anonsync_sync_linked_peer_user_layout
  anonsync_sync_local_status_socket
  anonsync_sync_linux_process_resources
  anonsync_sync_replica_peer_service
  anonsync_sync_replica_peer_service_configuration
  anonsync_sync_replica_peer_service_provisioning
  anonsync_sync_replica_peer_service_singleton
  anonsync_sync_replica_peer_service_status
  anonsync_sync_replica_sync_once
  anonsync_sync_systemd_notify
  OpenSSL::SSL
  OpenSSL::Crypto)
target_compile_options(anonsync_sync PRIVATE -Wall -Wextra -Wpedantic)

# Deliberately narrow shipping component. Historical proof programs and the
# hidden corpus remain buildable but cannot leak into an ordinary product install.
install(TARGETS
    anonsync_replica
    anonsync_folder
    anonsync_sync
  RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
  COMPONENT anonsync_runtime)
install(FILES "${ANONSYNC_CONFIGURED_SYSTEMD_USER_UNIT}"
  DESTINATION "${ANONSYNC_SYSTEMD_USER_UNIT_INSTALL_DIR}"
  COMPONENT anonsync_runtime)

# The peer-ingress lifecycle corpus lives in the runtime translation unit and
# does not need the unrelated sync-domain, reporting, or replay-ledger selftest
# libraries. Keep a focused driver for sanitizer and compiler lanes while the
# registered CLI test continues to prove the advertised command-line route.
add_executable(anonsync_sync_peer_ingress_lifecycle_selftest
  tests/sync_peer_ingress_lifecycle_selftest_main.cpp)
target_link_libraries(anonsync_sync_peer_ingress_lifecycle_selftest PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_sync_peer_ingress_lifecycle_selftest PRIVATE
  -Wall -Wextra -Wpedantic)
get_target_property(ANONSYNC_PEER_INGRESS_LIFECYCLE_SELFTEST_LINK_LIBRARIES
  anonsync_sync_peer_ingress_lifecycle_selftest LINK_LIBRARIES)
if(NOT ANONSYNC_PEER_INGRESS_LIFECYCLE_SELFTEST_LINK_LIBRARIES STREQUAL
    "anonsync_core_lib")
  message(FATAL_ERROR
    "focused peer-ingress lifecycle selftest must depend only on anonsync_core_lib")
endif()

add_executable(anonsync_sync_atomic_file_publication_test
  tests/sync_atomic_file_publication_test.cpp)
target_include_directories(anonsync_sync_atomic_file_publication_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_atomic_file_publication_test PRIVATE
  anonsync_sync_atomic_file_publication
  Threads::Threads)
target_compile_options(anonsync_sync_atomic_file_publication_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_posix_directory_resolution_test
  tests/sync_posix_directory_resolution_test.cpp)
target_include_directories(anonsync_sync_posix_directory_resolution_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_posix_directory_resolution_test PRIVATE
  anonsync_sync_directory_authority
  anonsync_sync_posix_directory_resolution)
target_compile_options(anonsync_sync_posix_directory_resolution_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_atomic_file_publication_prepared_test
  tests/sync_atomic_file_publication_prepared_test.cpp)
target_include_directories(anonsync_sync_atomic_file_publication_prepared_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_atomic_file_publication_prepared_test PRIVATE
  anonsync_sync_atomic_file_publication
  Threads::Threads)
target_compile_options(anonsync_sync_atomic_file_publication_prepared_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_atomic_file_publication_state_test
  tests/sync_atomic_file_publication_state_test.cpp)
target_include_directories(anonsync_sync_atomic_file_publication_state_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_atomic_file_publication_state_test PRIVATE
  anonsync_sync_atomic_file_publication_state)
target_compile_options(anonsync_sync_atomic_file_publication_state_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_atomic_file_publication_cutpoint_test
  tests/sync_atomic_file_publication_cutpoint_test.cpp)
target_include_directories(anonsync_sync_atomic_file_publication_cutpoint_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_atomic_file_publication_cutpoint_test PRIVATE
  anonsync_sync_atomic_file_publication
  Threads::Threads)
target_compile_options(anonsync_sync_atomic_file_publication_cutpoint_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_atomic_file_reconciliation_test
  tests/sync_atomic_file_reconciliation_test.cpp)
target_include_directories(anonsync_sync_atomic_file_reconciliation_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_atomic_file_reconciliation_test PRIVATE
  anonsync_sync_atomic_file_publication)
target_compile_options(anonsync_sync_atomic_file_reconciliation_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_file_effect_sqlite_owner_test
  tests/sync_replica_file_effect_sqlite_owner_test.cpp)
target_include_directories(anonsync_sync_replica_file_effect_sqlite_owner_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_effect_sqlite_owner_test PRIVATE
  anonsync_sync_replica_file_effect_sqlite_owner)
target_compile_options(anonsync_sync_replica_file_effect_sqlite_owner_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_file_delivery_protocol_test
  tests/sync_replica_file_delivery_protocol_test.cpp)
target_include_directories(anonsync_sync_replica_file_delivery_protocol_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_delivery_protocol_test PRIVATE
  anonsync_sync_replica_file_delivery_protocol)
target_compile_options(anonsync_sync_replica_file_delivery_protocol_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_file_payload_verification_index_test
  tests/sync_replica_file_payload_verification_index_test.cpp)
target_include_directories(anonsync_sync_replica_file_payload_verification_index_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_payload_verification_index_test PRIVATE
  anonsync_sync_replica_file_payload_verification_index
  anonsync_sync_posix_regular_file_snapshot_codec)
target_compile_options(anonsync_sync_replica_file_payload_verification_index_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_resumable_sha256_test
  tests/resumable_sha256_test.cpp)
target_include_directories(anonsync_resumable_sha256_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_resumable_sha256_test PRIVATE
  anonsync_resumable_sha256
  anonsync_sha256_digest)
target_compile_options(anonsync_resumable_sha256_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_file_payload_scrub_state_test
  tests/sync_replica_file_payload_scrub_state_test.cpp)
target_include_directories(anonsync_sync_replica_file_payload_scrub_state_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_payload_scrub_state_test PRIVATE
  anonsync_sync_replica_file_payload_scrub_state)
target_compile_options(anonsync_sync_replica_file_payload_scrub_state_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_file_payload_terminal_verification_state_test
  tests/sync_replica_file_payload_terminal_verification_state_test.cpp)
target_include_directories(anonsync_sync_replica_file_payload_terminal_verification_state_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_payload_terminal_verification_state_test PRIVATE
  anonsync_sha256_digest
  anonsync_sync_replica_file_payload_terminal_verification_state)
target_compile_options(anonsync_sync_replica_file_payload_terminal_verification_state_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_file_payload_retention_mark_test
  tests/sync_replica_file_payload_retention_mark_test.cpp)
target_include_directories(anonsync_sync_replica_file_payload_retention_mark_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_file_payload_retention_mark_test PRIVATE
  anonsync_sha256_digest
  anonsync_sync_replica_file_payload_retention_mark)
target_compile_options(anonsync_sync_replica_file_payload_retention_mark_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_source_manifest_checkpoint_test
  tests/sync_replica_source_manifest_checkpoint_test.cpp)
target_include_directories(anonsync_sync_replica_source_manifest_checkpoint_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_source_manifest_checkpoint_test PRIVATE
  anonsync_sha256_digest
  anonsync_sync_replica_source_manifest_checkpoint)
target_compile_options(anonsync_sync_replica_source_manifest_checkpoint_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_reconciliation_compact_manifest_test
  tests/sync_replica_reconciliation_compact_manifest_test.cpp)
target_include_directories(
  anonsync_sync_replica_reconciliation_compact_manifest_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(
  anonsync_sync_replica_reconciliation_compact_manifest_test PRIVATE
  anonsync_sha256_digest
  anonsync_sync_replica_reconciliation_compact_manifest)
target_compile_options(
  anonsync_sync_replica_reconciliation_compact_manifest_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_content_defined_chunker_test
  tests/sync_replica_content_defined_chunker_test.cpp)
target_include_directories(anonsync_sync_replica_content_defined_chunker_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_content_defined_chunker_test PRIVATE
  anonsync_sync_replica_content_defined_chunker)
target_compile_options(anonsync_sync_replica_content_defined_chunker_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_file_payload_store_test
  tests/sync_replica_file_payload_store_test.cpp)
target_include_directories(anonsync_sync_replica_file_payload_store_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_sync_replica_file_payload_store_test PRIVATE
  anonsync_sync_replica_file_payload_store)
target_compile_options(anonsync_sync_replica_file_payload_store_test PRIVATE
  -Wall -Wextra -Wpedantic)

# Test-only process fixture: create one exact completed staged prefix while
# deliberately deferring whole-target SHA-256. The retained service process
# must discover and finish this obligation without another authenticated peer
# turn.
add_executable(anonsync_sync_replica_terminal_verification_fixture
  tests/sync_replica_terminal_verification_fixture.cpp)
target_include_directories(anonsync_sync_replica_terminal_verification_fixture PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_terminal_verification_fixture PRIVATE
  anonsync_sha256_digest
  anonsync_sync_replica_deployment_manifest
  anonsync_sync_replica_file_payload_store)
target_compile_options(anonsync_sync_replica_terminal_verification_fixture PRIVATE
  -Wall -Wextra -Wpedantic)

# Test-only multi-process resource fixture. It owns one or two local status
# sockets and an optional touched anonymous mapping, but no replica, SQLite,
# payload, filesystem-root, TLS, or network authority.
add_executable(anonsync_sync_linux_process_resources_fixture
  tests/sync_linux_process_resources_fixture.cpp)
target_include_directories(anonsync_sync_linux_process_resources_fixture PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_linux_process_resources_fixture PRIVATE
  anonsync_sync_local_status_socket
  Threads::Threads)
target_compile_options(anonsync_sync_linux_process_resources_fixture PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_deployment_manifest_test
  tests/sync_replica_deployment_manifest_test.cpp)
target_include_directories(anonsync_sync_replica_deployment_manifest_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_deployment_manifest_test PRIVATE
  anonsync_sync_replica_deployment_manifest)
target_compile_options(anonsync_sync_replica_deployment_manifest_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_bootstrap_record_test
  tests/sync_replica_bootstrap_record_test.cpp)
target_include_directories(anonsync_sync_replica_bootstrap_record_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_bootstrap_record_test PRIVATE
  anonsync_sync_replica_bootstrap_record)
target_compile_options(anonsync_sync_replica_bootstrap_record_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_deployment_binding_test
  tests/sync_replica_deployment_binding_test.cpp)
target_include_directories(anonsync_sync_replica_deployment_binding_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_sync_replica_deployment_binding_test PRIVATE
  anonsync_sync_replica_deployment_binding
  anonsync_sqlite_support)
target_compile_options(anonsync_sync_replica_deployment_binding_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_file_delivery_service_test
  tests/sync_replica_file_delivery_service_test.cpp)
target_include_directories(anonsync_sync_replica_file_delivery_service_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_sync_replica_file_delivery_service_test PRIVATE
  anonsync_sync_replica_file_delivery_service
  anonsync_sync_replica_delivery_test_channel)
target_compile_options(anonsync_sync_replica_file_delivery_service_test PRIVATE
  -Wall -Wextra -Wpedantic)

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  # Link-time wrapping makes any future unlinkat() call observable and turns the
  # historical identity-check/path-delete race into a deterministic regression.
  add_executable(anonsync_sync_atomic_file_publication_unlink_authority_test
    tests/sync_atomic_file_publication_unlink_authority_test.cpp)
  target_include_directories(anonsync_sync_atomic_file_publication_unlink_authority_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src)
  target_link_libraries(anonsync_sync_atomic_file_publication_unlink_authority_test PRIVATE
    anonsync_sync_atomic_file_publication)
  target_compile_options(anonsync_sync_atomic_file_publication_unlink_authority_test PRIVATE
    -Wall -Wextra -Wpedantic)
  target_link_options(anonsync_sync_atomic_file_publication_unlink_authority_test PRIVATE
    -Wl,--wrap=unlinkat
    -Wl,--wrap=renameat2)
endif()

add_executable(anonsync_sync_checkpoint_scheduler_policy_test
  tests/sync_checkpoint_scheduler_policy_test.cpp)
target_include_directories(anonsync_sync_checkpoint_scheduler_policy_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_checkpoint_scheduler_policy_test PRIVATE
  anonsync_sync_checkpoint_scheduler_policy)
target_compile_options(anonsync_sync_checkpoint_scheduler_policy_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_checkpoint_owner_fence_policy_test
  tests/sync_checkpoint_owner_fence_policy_test.cpp)
target_include_directories(anonsync_sync_checkpoint_owner_fence_policy_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_checkpoint_owner_fence_policy_test PRIVATE
  anonsync_sync_checkpoint_owner_fence_policy)
target_compile_options(anonsync_sync_checkpoint_owner_fence_policy_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_checkpoint_owner_schema_test
  tests/sync_checkpoint_owner_schema_test.cpp)
target_include_directories(anonsync_sync_checkpoint_owner_schema_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_checkpoint_owner_schema_test PRIVATE
  anonsync_sync_checkpoint_owner_schema)
target_compile_options(anonsync_sync_checkpoint_owner_schema_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_checkpoint_owner_fence_sqlite_test
  tests/sync_checkpoint_owner_fence_sqlite_test.cpp)
target_include_directories(anonsync_sync_checkpoint_owner_fence_sqlite_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_checkpoint_owner_fence_sqlite_test PRIVATE
  anonsync_sync_checkpoint_owner_fence)
target_compile_options(anonsync_sync_checkpoint_owner_fence_sqlite_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_fuzz_json_codec fuzz/fuzz_json_codec.cpp)
target_link_libraries(anonsync_fuzz_json_codec PRIVATE
  anonsync_reporting_selftests_lib)
add_executable(anonsync_fuzz_jwt_codec fuzz/fuzz_jwt_codec.cpp)
target_link_libraries(anonsync_fuzz_jwt_codec PRIVATE
  anonsync_reporting_selftests_lib)
add_executable(anonsync_fuzz_route_event_ledger fuzz/fuzz_route_event_ledger.cpp)
target_link_libraries(anonsync_fuzz_route_event_ledger PRIVATE
  anonsync_reporting_selftests_lib)

# The three legacy fuzz-named binaries above are deterministic corpus
# selftests. This is the first actual coverage-guided fuzz target: it exercises
# SQLite row state, storage classes, malformed/aliased column maps, embedded
# bytes, and the value-free decoder error surface. Compile the three small
# boundary implementations directly so the fuzz lane instruments
# them without forcing sanitizer runtimes into every normal consumer of their
# static libraries.
if(ANONSYNC_ENABLE_LIBFUZZER)
  if(NOT CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    message(FATAL_ERROR
      "ANONSYNC_ENABLE_LIBFUZZER requires a matching Clang/libFuzzer toolchain")
  endif()
  add_executable(anonsync_fuzz_sqlite_projection_decoder
    fuzz/fuzz_sqlite_projection_decoder.cpp
    ${ANONSYNC_SQLITE_EXACT_VALUE_SOURCE}
    ${ANONSYNC_CANONICAL_PROJECTION_VERIFIER_SOURCE}
    ${ANONSYNC_SQLITE_PROJECTION_DECODER_SOURCE})
  target_include_directories(anonsync_fuzz_sqlite_projection_decoder PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
  target_link_libraries(anonsync_fuzz_sqlite_projection_decoder PRIVATE
    ${ANONSYNC_SQLITE_TARGET})
  set(ANONSYNC_LIBFUZZER_SANITIZERS "fuzzer,undefined")
  if(ANONSYNC_LIBFUZZER_WITH_ASAN)
    set(ANONSYNC_LIBFUZZER_SANITIZERS "fuzzer,address,undefined")
  endif()
  target_compile_options(anonsync_fuzz_sqlite_projection_decoder PRIVATE
    -Wall -Wextra -Wpedantic -Werror
    -fsanitize=${ANONSYNC_LIBFUZZER_SANITIZERS}
    -fno-omit-frame-pointer -D_GLIBCXX_ASSERTIONS)
  target_link_options(anonsync_fuzz_sqlite_projection_decoder PRIVATE
    -fsanitize=${ANONSYNC_LIBFUZZER_SANITIZERS})

  # A second real fuzz boundary explores the 100-byte SQLite header, stale
  # page-count evidence, exact file extents, and caller-tightenable hard caps.
  # Compile the pure owner directly so coverage is not diluted by the core.
  add_executable(anonsync_fuzz_sqlite_snapshot_geometry
    fuzz/fuzz_sqlite_snapshot_geometry.cpp
    ${ANONSYNC_SQLITE_SNAPSHOT_GEOMETRY_SOURCE})
  target_include_directories(anonsync_fuzz_sqlite_snapshot_geometry PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
  target_compile_options(anonsync_fuzz_sqlite_snapshot_geometry PRIVATE
    -Wall -Wextra -Wpedantic -Werror
    -fsanitize=${ANONSYNC_LIBFUZZER_SANITIZERS}
    -fno-omit-frame-pointer -D_GLIBCXX_ASSERTIONS)
  target_link_options(anonsync_fuzz_sqlite_snapshot_geometry PRIVATE
    -fsanitize=${ANONSYNC_LIBFUZZER_SANITIZERS})
endif()
add_executable(anonsync_sync_peer_transport_digest_bound_frame_test
  tests/sync_peer_transport_digest_bound_frame_test.cpp)
target_link_libraries(anonsync_sync_peer_transport_digest_bound_frame_test PRIVATE
  anonsync_sync_peer_transport_digest_bound_frame)
target_compile_options(anonsync_sync_peer_transport_digest_bound_frame_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_conflict_resolution_test
  tests/sync_conflict_resolution_test.cpp)
target_link_libraries(anonsync_sync_conflict_resolution_test PRIVATE
  anonsync_sync_conflict_resolution)
target_compile_options(anonsync_sync_conflict_resolution_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_manifest_validation_test
  tests/sync_manifest_validation_test.cpp)
target_link_libraries(anonsync_sync_manifest_validation_test PRIVATE
  anonsync_sync_manifest_validation)
target_compile_options(anonsync_sync_manifest_validation_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_manifest_stream_decoder_test
  tests/sync_manifest_stream_decoder_test.cpp)
target_link_libraries(anonsync_sync_manifest_stream_decoder_test PRIVATE
  anonsync_sync_manifest_stream_decoder)
target_compile_options(anonsync_sync_manifest_stream_decoder_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_sqlite_manifest_chunk_subset_test
  tests/sync_sqlite_manifest_chunk_subset_test.cpp)
target_link_libraries(anonsync_sync_sqlite_manifest_chunk_subset_test PRIVATE
  anonsync_sync_sqlite_manifest_chunk_subset)
target_compile_options(anonsync_sync_sqlite_manifest_chunk_subset_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_sqlite_sidecar_claimed_path_snapshot_test
  tests/sync_sqlite_sidecar_claimed_path_snapshot_test.cpp)
target_link_libraries(anonsync_sync_sqlite_sidecar_claimed_path_snapshot_test PRIVATE
  anonsync_sync_sqlite_sidecar_claimed_path_snapshot)
target_compile_options(anonsync_sync_sqlite_sidecar_claimed_path_snapshot_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_manifest_identity_test
  tests/sync_manifest_identity_test.cpp)
target_link_libraries(anonsync_sync_manifest_identity_test PRIVATE
  anonsync_sync_manifest_identity)
target_compile_options(anonsync_sync_manifest_identity_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_manifest_hash_locale_test
  tests/sync_manifest_hash_locale_test.cpp)
target_include_directories(anonsync_sync_manifest_hash_locale_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_manifest_hash_locale_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_sync_manifest_hash_locale_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_manifest_conflict_convergence_test
  tests/sync_manifest_conflict_convergence_test.cpp)
target_include_directories(anonsync_sync_manifest_conflict_convergence_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_manifest_conflict_convergence_test PRIVATE
  anonsync_core_lib
  anonsync_sync_conflict_resolution)
target_compile_options(anonsync_sync_manifest_conflict_convergence_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_network_model_test
  tests/sync_replica_network_model_test.cpp)
target_include_directories(anonsync_sync_replica_network_model_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_network_model_test PRIVATE
  anonsync_sync_replica_network_simulator
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_network_model_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_hash_graph_projection_test
  tests/sync_replica_hash_graph_projection_test.cpp)
target_include_directories(anonsync_sync_replica_hash_graph_projection_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_hash_graph_projection_test PRIVATE
  anonsync_sync_replica_model
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_hash_graph_projection_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_allocation_atomicity_test
  tests/sync_replica_allocation_atomicity_test.cpp)
target_include_directories(anonsync_sync_replica_allocation_atomicity_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_allocation_atomicity_test PRIVATE
  anonsync_sync_replica_model
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_allocation_atomicity_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_aggregate_budget_test
  tests/sync_replica_aggregate_budget_test.cpp)
target_include_directories(anonsync_sync_replica_aggregate_budget_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_aggregate_budget_test PRIVATE
  anonsync_sync_replica_model
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_aggregate_budget_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_capacity_backpressure_test
  tests/sync_replica_capacity_backpressure_test.cpp)
target_include_directories(anonsync_sync_replica_capacity_backpressure_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_capacity_backpressure_test PRIVATE
  anonsync_sync_replica_network_simulator
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_capacity_backpressure_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_outbox_lease_test
  tests/sync_replica_outbox_lease_test.cpp)
target_include_directories(anonsync_sync_replica_outbox_lease_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_outbox_lease_test PRIVATE
  anonsync_sync_replica_outbox_lease)
target_compile_options(anonsync_sync_replica_outbox_lease_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_outbox_clock_test
  tests/sync_replica_outbox_clock_test.cpp)
target_include_directories(anonsync_sync_replica_outbox_clock_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_outbox_clock_test PRIVATE
  anonsync_sync_replica_outbox_clock)
target_compile_options(anonsync_sync_replica_outbox_clock_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_delivery_protocol_test
  tests/sync_replica_delivery_protocol_test.cpp)
target_include_directories(anonsync_sync_replica_delivery_protocol_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_delivery_protocol_test PRIVATE
  anonsync_sync_replica_delivery_protocol)
target_compile_options(anonsync_sync_replica_delivery_protocol_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_selective_sync_policy_test
  tests/sync_replica_selective_sync_policy_test.cpp)
target_include_directories(
  anonsync_sync_replica_selective_sync_policy_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(
  anonsync_sync_replica_selective_sync_policy_test PRIVATE
  anonsync_sync_replica_selective_sync_policy)
target_compile_options(
  anonsync_sync_replica_selective_sync_policy_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_reconciliation_protocol_test
  tests/sync_replica_reconciliation_protocol_test.cpp)
target_include_directories(
  anonsync_sync_replica_reconciliation_protocol_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(
  anonsync_sync_replica_reconciliation_protocol_test PRIVATE
  anonsync_sync_replica_reconciliation_protocol)
target_compile_options(
  anonsync_sync_replica_reconciliation_protocol_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_reconciliation_frame_memory_test
  tests/sync_replica_reconciliation_frame_memory_test.cpp)
target_include_directories(
  anonsync_sync_replica_reconciliation_frame_memory_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(
  anonsync_sync_replica_reconciliation_frame_memory_test PRIVATE
  anonsync_sync_replica_reconciliation_protocol
  anonsync_sha256_digest)
target_compile_options(
  anonsync_sync_replica_reconciliation_frame_memory_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_reconciliation_memory_shape_test
  tests/sync_replica_reconciliation_memory_shape_test.cpp)
target_include_directories(
  anonsync_sync_replica_reconciliation_memory_shape_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(
  anonsync_sync_replica_reconciliation_memory_shape_test PRIVATE
  anonsync_sync_replica_reconciliation_protocol)
target_compile_options(
  anonsync_sync_replica_reconciliation_memory_shape_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_reconciliation_source_frame_memory_test
  tests/sync_replica_reconciliation_source_frame_memory_test.cpp)
target_include_directories(
  anonsync_sync_replica_reconciliation_source_frame_memory_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(
  anonsync_sync_replica_reconciliation_source_frame_memory_test PRIVATE
  anonsync_sync_replica_reconciliation_service
  anonsync_sync_replica_file_delivery_service
  anonsync_sync_replica_delivery_test_channel
  anonsync_sha256_digest
  anonsync_sqlite_support)
target_compile_options(
  anonsync_sync_replica_reconciliation_source_frame_memory_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_sqlite_owner_test
  tests/sync_replica_sqlite_owner_test.cpp)
target_include_directories(anonsync_sync_replica_sqlite_owner_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_sqlite_owner_test PRIVATE
  anonsync_sync_replica_sqlite_owner
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_sqlite_owner_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_prepared_publication_test
  tests/sync_replica_prepared_publication_test.cpp)
target_include_directories(anonsync_sync_replica_prepared_publication_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_prepared_publication_test PRIVATE
  anonsync_sync_replica_sqlite_owner
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_prepared_publication_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_folder_scan_owner_test
  tests/sync_replica_folder_scan_owner_test.cpp)
target_include_directories(anonsync_sync_replica_folder_scan_owner_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_folder_scan_owner_test PRIVATE
  anonsync_sync_replica_folder_scan_owner
  anonsync_sync_atomic_file_publication
  anonsync_sha256_digest
  anonsync_sqlite_support)
target_compile_options(anonsync_sync_replica_folder_scan_owner_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_peer_service_integrity_evidence_test
  tests/sync_replica_peer_service_integrity_evidence_test.cpp)
target_include_directories(
  anonsync_sync_replica_peer_service_integrity_evidence_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(
  anonsync_sync_replica_peer_service_integrity_evidence_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_folder_process_test
  tests/sync_replica_folder_process_test.cpp)
target_include_directories(anonsync_sync_replica_folder_process_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_folder_process_test PRIVATE
  anonsync_sync_replica_folder_process)
target_compile_options(anonsync_sync_replica_folder_process_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_sync_once_test
  tests/sync_replica_sync_once_test.cpp)
target_include_directories(anonsync_sync_replica_sync_once_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_sync_once_test PRIVATE
  anonsync_sync_replica_sync_once)
target_compile_options(anonsync_sync_replica_sync_once_test PRIVATE
  -Wall -Wextra -Wpedantic)

# Deterministic authority minting for service tests only. No production target
# links this constructor path.
add_library(anonsync_sync_replica_delivery_test_channel STATIC
  tests/sync_replica_delivery_test_channel.cpp)
target_include_directories(anonsync_sync_replica_delivery_test_channel PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_sync_replica_delivery_test_channel PUBLIC
  anonsync_sync_replica_delivery_channel)
target_compile_options(anonsync_sync_replica_delivery_test_channel PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_delivery_service_test
  tests/sync_replica_delivery_service_test.cpp)
target_include_directories(anonsync_sync_replica_delivery_service_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_sync_replica_delivery_service_test PRIVATE
  anonsync_sync_replica_delivery_service
  anonsync_sync_replica_delivery_test_channel)
target_compile_options(anonsync_sync_replica_delivery_service_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_source_manifest_restart_test
  tests/sync_replica_source_manifest_restart_test.cpp)
target_include_directories(
  anonsync_sync_replica_source_manifest_restart_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(
  anonsync_sync_replica_source_manifest_restart_test PRIVATE
  anonsync_sync_replica_reconciliation_service
  anonsync_sync_replica_delivery_test_channel
  anonsync_sqlite_support)
target_compile_options(
  anonsync_sync_replica_source_manifest_restart_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_reconciliation_service_test
  tests/sync_replica_reconciliation_service_test.cpp)
target_include_directories(
  anonsync_sync_replica_reconciliation_service_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(
  anonsync_sync_replica_reconciliation_service_test PRIVATE
  anonsync_sync_replica_reconciliation_service
  anonsync_sync_replica_delivery_test_channel
  anonsync_sqlite_support)
target_compile_options(
  anonsync_sync_replica_reconciliation_service_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_socket_readiness_identity_test
  tests/sync_socket_readiness_identity_test.cpp)
target_include_directories(anonsync_sync_socket_readiness_identity_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_socket_readiness_identity_test PRIVATE
  anonsync_sync_stream_socket_deadline_poll)
target_compile_options(anonsync_sync_socket_readiness_identity_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_local_status_socket_test
  tests/sync_local_status_socket_test.cpp)
target_include_directories(anonsync_sync_local_status_socket_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_local_status_socket_test PRIVATE
  anonsync_sync_local_status_socket
  anonsync_sync_replica_peer_service_status
  anonsync_json_parser
  Threads::Threads)
target_compile_options(anonsync_sync_local_status_socket_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_linux_process_resources_test
  tests/sync_linux_process_resources_test.cpp)
target_include_directories(anonsync_sync_linux_process_resources_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(anonsync_sync_linux_process_resources_test PRIVATE
  anonsync_sync_linux_process_resources
  anonsync_json_parser
  Threads::Threads)
target_compile_options(anonsync_sync_linux_process_resources_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_systemd_notify_test
  tests/sync_systemd_notify_test.cpp)
target_include_directories(anonsync_sync_systemd_notify_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_systemd_notify_test PRIVATE
  anonsync_sync_systemd_notify)
target_compile_options(anonsync_sync_systemd_notify_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_linked_peer_user_layout_test
  tests/sync_linked_peer_user_layout_test.cpp)
target_include_directories(anonsync_sync_linked_peer_user_layout_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_linked_peer_user_layout_test PRIVATE
  anonsync_sync_linked_peer_user_layout)
target_compile_options(anonsync_sync_linked_peer_user_layout_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_folder_wake_test
  tests/sync_replica_folder_wake_test.cpp)
target_include_directories(anonsync_sync_replica_folder_wake_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_folder_wake_test PRIVATE
  anonsync_sync_replica_folder_wake)
target_compile_options(anonsync_sync_replica_folder_wake_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_tls_io_policy_test
  tests/sync_replica_tls_io_policy_test.cpp)
target_include_directories(anonsync_sync_replica_tls_io_policy_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_tls_io_policy_test PRIVATE
  anonsync_sync_replica_tls_io_policy)
target_compile_options(anonsync_sync_replica_tls_io_policy_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_session_supervisor_test
  tests/sync_replica_session_supervisor_test.cpp)
target_include_directories(anonsync_sync_replica_session_supervisor_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_session_supervisor_test PRIVATE
  anonsync_sync_replica_file_tls_server)
target_compile_options(anonsync_sync_replica_session_supervisor_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_stream_connector_test
  tests/sync_replica_stream_connector_test.cpp)
target_include_directories(anonsync_sync_replica_stream_connector_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_stream_connector_test PRIVATE
  anonsync_sync_replica_file_tls_server Threads::Threads)
target_compile_options(anonsync_sync_replica_stream_connector_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_tls_transport_test
  tests/sync_replica_tls_transport_test.cpp
  tests/sync_replica_tls_membership_sqlite_owner_test.cpp
  tests/sync_replica_tls_membership_anchor_sqlite_owner_test.cpp)
target_include_directories(anonsync_sync_replica_tls_transport_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_replica_tls_transport_test PRIVATE
  anonsync_sync_replica_file_tls_dispatch
  anonsync_sync_replica_file_tls_exchange
  anonsync_sync_replica_file_tls_server
  anonsync_sync_replica_delivery_service
  anonsync_sync_replica_reconciliation_tls_exchange
  anonsync_sync_replica_tls_poll
  Threads::Threads)
target_compile_options(anonsync_sync_replica_tls_transport_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_bounded_regular_file_test
  tests/sync_bounded_regular_file_test.cpp)
target_link_libraries(anonsync_sync_bounded_regular_file_test PRIVATE
  anonsync_sync_bounded_regular_file)
target_compile_options(anonsync_sync_bounded_regular_file_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_replica_folder_observer_test
  tests/sync_replica_folder_observer_test.cpp)
target_link_libraries(anonsync_sync_replica_folder_observer_test PRIVATE
  anonsync_sync_replica_folder_observer
  anonsync_sha256_digest)
target_compile_options(anonsync_sync_replica_folder_observer_test PRIVATE
  -Wall -Wextra -Wpedantic)

if(CMAKE_SYSTEM_NAME STREQUAL "Linux" AND
    CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  # Deterministically replace a file name and a directory name from inside the
  # observer's first pread(2). The retained descriptors continue to name the old
  # objects, so the post-read no-follow rebinding must reject both substitutions.
  add_executable(anonsync_sync_replica_folder_observer_race_test
    tests/sync_replica_folder_observer_race_test.cpp)
  target_link_libraries(anonsync_sync_replica_folder_observer_race_test PRIVATE
    anonsync_sync_replica_folder_observer)
  target_link_options(anonsync_sync_replica_folder_observer_race_test PRIVATE
    -Wl,--wrap=pread -Wl,--wrap=EVP_DigestUpdate)
  target_compile_options(anonsync_sync_replica_folder_observer_race_test PRIVATE
    -Wall -Wextra -Wpedantic)
endif()

add_executable(anonsync_sync_daemon_heartbeat_document_test
  tests/sync_daemon_heartbeat_document_test.cpp)
target_link_libraries(anonsync_sync_daemon_heartbeat_document_test PRIVATE
  anonsync_sync_daemon_heartbeat_document)
target_compile_options(anonsync_sync_daemon_heartbeat_document_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_sync_daemon_heartbeat_publication_test
  tests/sync_daemon_heartbeat_publication_test.cpp)
target_link_libraries(anonsync_sync_daemon_heartbeat_publication_test PRIVATE
  anonsync_sync_daemon_heartbeat_publication)
target_compile_options(anonsync_sync_daemon_heartbeat_publication_test PRIVATE
  -Wall -Wextra -Wpedantic)

if(CMAKE_SYSTEM_NAME STREQUAL "Linux" AND
    CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  # Linker wrapping gives this focused proof deterministic control over every
  # descriptor transition without racing the host filesystem or scheduler.
  add_executable(anonsync_sync_bounded_regular_file_syscall_test
    tests/sync_bounded_regular_file_syscall_test.cpp)
  target_link_libraries(anonsync_sync_bounded_regular_file_syscall_test PRIVATE
    anonsync_sync_bounded_regular_file)
  target_link_options(anonsync_sync_bounded_regular_file_syscall_test PRIVATE
    -Wl,--wrap=open
    -Wl,--wrap=fstat
    -Wl,--wrap=pread
    -Wl,--wrap=close)
  target_compile_options(anonsync_sync_bounded_regular_file_syscall_test PRIVATE
    -Wall -Wextra -Wpedantic)
endif()

add_executable(anonsync_process_incarnation_test
  tests/process_incarnation_tests.cpp)
target_include_directories(anonsync_process_incarnation_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_process_incarnation_test PRIVATE
  anonsync_process_incarnation)
target_compile_options(anonsync_process_incarnation_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_thread_incarnation_test
  tests/thread_incarnation_tests.cpp)
target_include_directories(anonsync_thread_incarnation_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_thread_incarnation_test PRIVATE
  anonsync_thread_incarnation)
target_compile_options(anonsync_thread_incarnation_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_process_identity_observation_test
  tests/sync_process_identity_observation_test.cpp)
target_include_directories(anonsync_process_identity_observation_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_process_identity_observation_test PRIVATE
  anonsync_process_identity_observation)
target_compile_options(anonsync_process_identity_observation_test PRIVATE
  -Wall -Wextra -Wpedantic)

add_executable(anonsync_system_epoch_identity_test
  tests/sync_system_epoch_identity_test.cpp)
target_include_directories(anonsync_system_epoch_identity_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_system_epoch_identity_test PRIVATE
  anonsync_system_epoch_identity)
target_compile_options(anonsync_system_epoch_identity_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_exact_value_test
  tests/persistence/sqlite_exact_value_tests.cpp)
target_include_directories(anonsync_sqlite_exact_value_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_exact_value_test PRIVATE
  anonsync_sqlite_exact_value)
target_compile_options(anonsync_sqlite_exact_value_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_ingress_sender_replay_record_test
  tests/persistence/ingress_sender_replay_record_tests.cpp)
target_include_directories(anonsync_ingress_sender_replay_record_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_ingress_sender_replay_record_test PRIVATE
  anonsync_ingress_sender_replay_record)
target_compile_options(anonsync_ingress_sender_replay_record_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_replay_ledger_schema_contract_test
  tests/persistence/sqlite_replay_ledger_schema_contract_tests.cpp)
target_include_directories(anonsync_sqlite_replay_ledger_schema_contract_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_replay_ledger_schema_contract_test PRIVATE
  anonsync_sqlite_replay_ledger_schema_contract)
target_compile_options(anonsync_sqlite_replay_ledger_schema_contract_test PRIVATE
  -Wall -Wextra -Wpedantic)
# Crash and fail-stop tests must not execute C++ or SQLite directly in a
# post-fork child. This Linux test-only owner uses posix_spawn plus self-exec,
# closes every inherited non-standard descriptor, supplies a small allowlisted
# environment, resets signal state, and bounds every wait with kill-and-reap.
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  add_library(anonsync_self_exec_test_process STATIC
    tests/self_exec_test_process.cpp)
  target_include_directories(anonsync_self_exec_test_process PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/tests)
  target_link_libraries(anonsync_self_exec_test_process PRIVATE
    anonsync_test_process_topology_owner)
  target_compile_options(anonsync_self_exec_test_process PRIVATE
    -Wall -Wextra -Wpedantic)
  target_link_libraries(
    anonsync_sync_replica_source_manifest_restart_test PRIVATE
    anonsync_self_exec_test_process)
  target_link_libraries(anonsync_sqlite_replay_ledger_selftests_lib PRIVATE
    anonsync_self_exec_test_process)

  foreach(ANONSYNC_SELF_EXEC_ATOMIC_TARGET
      anonsync_sync_atomic_file_publication_test
      anonsync_sync_atomic_file_publication_cutpoint_test)
    target_include_directories(${ANONSYNC_SELF_EXEC_ATOMIC_TARGET} PRIVATE
      ${CMAKE_CURRENT_SOURCE_DIR}/tests)
    target_link_libraries(${ANONSYNC_SELF_EXEC_ATOMIC_TARGET} PRIVATE
      anonsync_self_exec_test_process)
  endforeach()
  target_include_directories(anonsync_sync_replica_sqlite_owner_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/tests)
  target_link_libraries(anonsync_sync_replica_sqlite_owner_test PRIVATE
    anonsync_self_exec_test_process)

  add_executable(anonsync_self_exec_test_process_test
    tests/self_exec_test_process_test.cpp)
  target_include_directories(anonsync_self_exec_test_process_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/tests)
  target_link_libraries(anonsync_self_exec_test_process_test PRIVATE
    anonsync_self_exec_test_process)
  target_compile_options(anonsync_self_exec_test_process_test PRIVATE
    -Wall -Wextra -Wpedantic)
endif()

add_executable(anonsync_sqlite_replay_ledger_reset_test
  tests/persistence/sqlite_replay_ledger_reset_tests.cpp)
target_include_directories(anonsync_sqlite_replay_ledger_reset_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_replay_ledger_reset_test PRIVATE
  anonsync_sqlite_replay_ledger_reset
  anonsync_sqlite_replay_ledger_write_gate
  anonsync_sqlite_replay_ledger_schema_contract
  anonsync_sha256_digest)
target_compile_options(anonsync_sqlite_replay_ledger_reset_test PRIVATE
  -Wall -Wextra -Wpedantic)
if(TARGET anonsync_self_exec_test_process)
  target_include_directories(anonsync_sqlite_replay_ledger_reset_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/tests)
  target_link_libraries(anonsync_sqlite_replay_ledger_reset_test PRIVATE
    anonsync_self_exec_test_process)
endif()
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  add_executable(anonsync_sqlite_replay_ledger_reset_crash_frontier_test
    tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp)
  target_include_directories(
    anonsync_sqlite_replay_ledger_reset_crash_frontier_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence
    ${CMAKE_CURRENT_SOURCE_DIR}/tests
    ${CMAKE_CURRENT_SOURCE_DIR}/tests/persistence)
  target_link_libraries(
    anonsync_sqlite_replay_ledger_reset_crash_frontier_test PRIVATE
    anonsync_sqlite_replay_ledger_reset
    anonsync_sqlite_replay_ledger_reset_documents
    anonsync_sqlite_replay_ledger_reset_receipt_protocol
    anonsync_sync_atomic_file_publication
    anonsync_sha256_digest
    anonsync_self_exec_test_process)
  target_compile_options(
    anonsync_sqlite_replay_ledger_reset_crash_frontier_test PRIVATE
    -Wall -Wextra -Wpedantic)
endif()
add_executable(anonsync_sqlite_replay_ledger_reset_documents_test
  tests/persistence/sqlite_replay_ledger_reset_documents_tests.cpp)
target_include_directories(anonsync_sqlite_replay_ledger_reset_documents_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_replay_ledger_reset_documents_test PRIVATE
  anonsync_sqlite_replay_ledger_reset_documents
  anonsync_sha256_digest)
target_compile_options(anonsync_sqlite_replay_ledger_reset_documents_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_replay_ledger_schema_integrity_test
  tests/sqlite_replay_ledger_schema_integrity_test.cpp)
target_link_libraries(anonsync_sqlite_replay_ledger_schema_integrity_test PRIVATE
  anonsync_core_lib
  anonsync_sqlite_snapshot_seal)
target_include_directories(anonsync_sqlite_replay_ledger_schema_integrity_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_compile_options(anonsync_sqlite_replay_ledger_schema_integrity_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_restore_namespace_authority_test
  tests/sqlite_restore_namespace_authority_test.cpp)
target_link_libraries(anonsync_sqlite_restore_namespace_authority_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_sqlite_restore_namespace_authority_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_backup_namespace_authority_test
  tests/sqlite_backup_namespace_authority_test.cpp)
target_include_directories(anonsync_sqlite_backup_namespace_authority_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_backup_namespace_authority_test PRIVATE
  anonsync_core_lib
  anonsync_sqlite_snapshot_seal)
target_compile_options(anonsync_sqlite_backup_namespace_authority_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_live_backup_test
  tests/persistence/sqlite_live_backup_tests.cpp)
target_include_directories(anonsync_sqlite_live_backup_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_live_backup_test PRIVATE
  anonsync_sqlite_live_backup)
target_compile_options(anonsync_sqlite_live_backup_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_snapshot_seal_test
  tests/persistence/sqlite_snapshot_seal_tests.cpp)
target_include_directories(anonsync_sqlite_snapshot_seal_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_snapshot_seal_test PRIVATE
  anonsync_sqlite_snapshot_seal)
target_compile_options(anonsync_sqlite_snapshot_seal_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_snapshot_geometry_test
  tests/persistence/sqlite_snapshot_geometry_tests.cpp)
target_include_directories(anonsync_sqlite_snapshot_geometry_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_snapshot_geometry_test PRIVATE
  anonsync_sqlite_snapshot_geometry)
target_compile_options(anonsync_sqlite_snapshot_geometry_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_verification_budget_test
  tests/persistence/sqlite_verification_budget_tests.cpp)
target_include_directories(anonsync_sqlite_verification_budget_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_verification_budget_test PRIVATE
  anonsync_sqlite_verification_budget)
target_compile_options(anonsync_sqlite_verification_budget_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_busy_handler_owner_test
  tests/persistence/sqlite_busy_handler_owner_tests.cpp)
target_include_directories(anonsync_sqlite_busy_handler_owner_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_busy_handler_owner_test PRIVATE
  anonsync_sqlite_busy_handler_owner)
target_compile_options(anonsync_sqlite_busy_handler_owner_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_owned_authorizer_policy_test
  tests/sqlite_owned_authorizer_policy_test.cpp)
target_include_directories(anonsync_sqlite_owned_authorizer_policy_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_owned_authorizer_policy_test PRIVATE
  anonsync_sqlite_owned_authorizer_policy)
target_compile_options(anonsync_sqlite_owned_authorizer_policy_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_authorizer_owner_test
  tests/persistence/sqlite_authorizer_owner_tests.cpp)
target_include_directories(anonsync_sqlite_authorizer_owner_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_authorizer_owner_test PRIVATE
  anonsync_sqlite_authorizer_owner)
target_compile_options(anonsync_sqlite_authorizer_owner_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_persistence_process_authority_fork_test
  tests/persistence/sqlite_persistence_process_authority_fork_test.cpp)
target_include_directories(
  anonsync_sqlite_persistence_process_authority_fork_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(
  anonsync_sqlite_persistence_process_authority_fork_test PRIVATE
  anonsync_sqlite_path_security
  anonsync_sqlite_snapshot_seal
  anonsync_sqlite_verification_budget
  anonsync_sqlite_busy_handler_owner)
target_compile_options(
  anonsync_sqlite_persistence_process_authority_fork_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_snapshot_geometry_binding_test
  tests/persistence/sqlite_snapshot_geometry_binding_test.cpp)
target_include_directories(anonsync_sqlite_snapshot_geometry_binding_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_snapshot_geometry_binding_test PRIVATE
  anonsync_sqlite_snapshot_seal)
target_compile_options(anonsync_sqlite_snapshot_geometry_binding_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_snapshot_sidecar_binding_test
  tests/sqlite_snapshot_sidecar_binding_test.cpp)
target_link_libraries(anonsync_sqlite_snapshot_sidecar_binding_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_sqlite_snapshot_sidecar_binding_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_ingress_sender_replay_integrity_test
  tests/sqlite_ingress_sender_replay_integrity_test.cpp)
target_link_libraries(anonsync_sqlite_ingress_sender_replay_integrity_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_sqlite_ingress_sender_replay_integrity_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_runtime_policy_test tests/sqlite_runtime_policy_test.cpp)
target_link_libraries(anonsync_sqlite_runtime_policy_test PRIVATE anonsync_sqlite_runtime)
target_compile_options(anonsync_sqlite_runtime_policy_test PRIVATE -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_support_test tests/sqlite_support_test.cpp)
target_link_libraries(anonsync_sqlite_support_test PRIVATE anonsync_sqlite_support)
target_compile_options(anonsync_sqlite_support_test PRIVATE -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_connection_authority_test
  tests/sqlite_connection_authority_test.cpp)
target_include_directories(anonsync_sqlite_connection_authority_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_connection_authority_test PRIVATE
  anonsync_sqlite_support)
target_compile_options(anonsync_sqlite_connection_authority_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_transaction_exception_composition_test
  tests/sqlite_transaction_exception_composition_test.cpp)
target_include_directories(
  anonsync_sqlite_transaction_exception_composition_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(
  anonsync_sqlite_transaction_exception_composition_test PRIVATE
  anonsync_sqlite_support)
target_compile_options(
  anonsync_sqlite_transaction_exception_composition_test PRIVATE
  -Wall -Wextra -Wpedantic)
if(CMAKE_SYSTEM_NAME STREQUAL "Linux" AND ANONSYNC_USE_BUNDLED_SQLITE)
  # SQLite's global allocator can only be replaced before initialization. The
  # campaign therefore self-execs one fresh worker for every transaction-stack
  # cut and drains bounded stdout/stderr through the test-only process owner.
  add_executable(anonsync_sqlite_transaction_allocator_fault_test
    tests/sqlite_transaction_allocator_fault_test.cpp)
  target_include_directories(
    anonsync_sqlite_transaction_allocator_fault_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/tests)
  target_link_libraries(
    anonsync_sqlite_transaction_allocator_fault_test PRIVATE
    anonsync_sqlite_support
    anonsync_self_exec_test_process)
  target_compile_options(
    anonsync_sqlite_transaction_allocator_fault_test PRIVATE
    -Wall -Wextra -Wpedantic)
endif()
add_executable(anonsync_sqlite_process_authority_fork_test
  tests/sqlite_process_authority_fork_test.cpp)
target_include_directories(anonsync_sqlite_process_authority_fork_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_process_authority_fork_test PRIVATE
  anonsync_sqlite_support)
target_compile_options(anonsync_sqlite_process_authority_fork_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_owner_generation_borrow_test
  tests/sqlite_owner_generation_borrow_test.cpp)
target_include_directories(anonsync_sqlite_owner_generation_borrow_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_owner_generation_borrow_test PRIVATE
  anonsync_sqlite_support)
target_compile_options(anonsync_sqlite_owner_generation_borrow_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_source_first_move_test
  tests/sqlite_source_first_move_test.cpp)
target_include_directories(anonsync_sqlite_source_first_move_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_source_first_move_test PRIVATE
  anonsync_sqlite_support)
target_compile_options(anonsync_sqlite_source_first_move_test PRIVATE
  -Wall -Wextra -Wpedantic)
if(TARGET anonsync_self_exec_test_process)
  target_link_libraries(anonsync_sqlite_connection_authority_test PRIVATE
    anonsync_self_exec_test_process)
  target_link_libraries(anonsync_sqlite_owner_generation_borrow_test PRIVATE
    anonsync_self_exec_test_process)
endif()
add_executable(anonsync_sync_peer_ingress_wire_test
  tests/sync_peer_ingress_wire_test.cpp)
target_include_directories(anonsync_sync_peer_ingress_wire_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_peer_ingress_wire_test PRIVATE anonsync_core_lib)
target_compile_options(anonsync_sync_peer_ingress_wire_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_peer_ingress_wire_adversarial_test
  tests/sync_peer_ingress_wire_adversarial_test.cpp)
target_include_directories(anonsync_peer_ingress_wire_adversarial_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_peer_ingress_wire_adversarial_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_peer_ingress_wire_adversarial_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sync_peer_wire_compatibility_test
  tests/sync_peer_wire_compatibility_test.cpp)
target_include_directories(anonsync_sync_peer_wire_compatibility_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_sync_peer_wire_compatibility_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_sync_peer_wire_compatibility_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_runtime_payload_store_test
  tests/sqlite_runtime_payload_store_test.cpp)
target_include_directories(anonsync_sqlite_runtime_payload_store_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_sqlite_runtime_payload_store_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_sqlite_runtime_payload_store_test PRIVATE
  -Wall -Wextra -Wpedantic)
if(ANONSYNC_USE_BUNDLED_SQLITE)
  target_compile_definitions(anonsync_sqlite_runtime_payload_store_test PRIVATE
    ANONSYNC_BUNDLED_SQLITE=1)
endif()
if(TARGET anonsync_self_exec_test_process)
  target_link_libraries(anonsync_sqlite_runtime_payload_store_test PRIVATE
    anonsync_self_exec_test_process)
endif()
add_executable(anonsync_canonical_projection_verifier_test
  tests/persistence/canonical_projection_verifier_tests.cpp)
target_include_directories(anonsync_canonical_projection_verifier_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_canonical_projection_verifier_test PRIVATE
  anonsync_canonical_projection_verifier)
target_compile_options(anonsync_canonical_projection_verifier_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_local_jsonl_replay_publication_test
  tests/persistence/local_jsonl_replay_publication_tests.cpp)
target_include_directories(anonsync_local_jsonl_replay_publication_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_local_jsonl_replay_publication_test PRIVATE
  anonsync_local_jsonl_replay_publication)
target_compile_options(anonsync_local_jsonl_replay_publication_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_local_jsonl_replay_directory_authority_test
  tests/persistence/local_jsonl_replay_directory_authority_tests.cpp)
target_include_directories(
  anonsync_local_jsonl_replay_directory_authority_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(
  anonsync_local_jsonl_replay_directory_authority_test PRIVATE
  anonsync_local_jsonl_replay_directory_authority
  anonsync_process_incarnation)
target_compile_options(
  anonsync_local_jsonl_replay_directory_authority_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_local_jsonl_replay_namespace_test
  tests/persistence/local_jsonl_replay_namespace_tests.cpp)
target_include_directories(anonsync_local_jsonl_replay_namespace_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_local_jsonl_replay_namespace_test PRIVATE
  anonsync_local_jsonl_replay_namespace
  anonsync_process_incarnation)
target_compile_options(anonsync_local_jsonl_replay_namespace_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_local_jsonl_replay_backend_namespace_test
  tests/local_jsonl_replay_backend_namespace_test.cpp)
target_include_directories(anonsync_local_jsonl_replay_backend_namespace_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_local_jsonl_replay_backend_namespace_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_local_jsonl_replay_backend_namespace_test PRIVATE
  -Wall -Wextra -Wpedantic)

# Keep every inherited-state consumer in one exact build-graph inventory. The
# matching source audits discover wrapper call sites independently and reject
# both unlisted consumers and stale listed targets.
if(TARGET anonsync_inherited_test_process)
  foreach(ANONSYNC_INHERITED_PROCESS_CONSUMER
      anonsync_local_jsonl_replay_backend_namespace_test
      anonsync_local_jsonl_replay_directory_authority_test
      anonsync_local_jsonl_replay_namespace_test
      anonsync_process_incarnation_test
      anonsync_thread_incarnation_test
      anonsync_sqlite_owner_generation_borrow_test
      anonsync_sqlite_owned_authorizer_policy_test
      anonsync_sqlite_persistence_process_authority_fork_test
      anonsync_sqlite_verification_budget_test
      anonsync_sqlite_process_authority_fork_test
      anonsync_sqlite_replay_ledger_selftests_lib
      anonsync_sqlite_source_first_move_test
      anonsync_sync_replica_tls_transport_test
      anonsync_sync_atomic_file_publication_prepared_test
      anonsync_sync_posix_directory_resolution_test
      anonsync_sync_replica_file_payload_store_test)
    target_link_libraries(${ANONSYNC_INHERITED_PROCESS_CONSUMER} PRIVATE
      anonsync_inherited_test_process)
  endforeach()
endif()
add_executable(anonsync_local_jsonl_replay_crash_state_machine_test
  tests/local_jsonl_replay_crash_state_machine_test.cpp)
target_include_directories(
  anonsync_local_jsonl_replay_crash_state_machine_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(
  anonsync_local_jsonl_replay_crash_state_machine_test PRIVATE
  anonsync_core_lib)
target_compile_options(
  anonsync_local_jsonl_replay_crash_state_machine_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_effect_transition_intent_publication_test
  tests/persistence/effect_transition_intent_publication_tests.cpp)
target_include_directories(anonsync_effect_transition_intent_publication_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_effect_transition_intent_publication_test PRIVATE
  anonsync_effect_transition_intent_publication)
target_compile_options(anonsync_effect_transition_intent_publication_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_effect_transition_record_material_test
  tests/persistence/effect_transition_record_material_tests.cpp)
target_include_directories(anonsync_effect_transition_record_material_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_effect_transition_record_material_test PRIVATE
  anonsync_effect_transition_record_material)
target_compile_options(anonsync_effect_transition_record_material_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_snapshot_manifest_publication_test
  tests/persistence/sqlite_snapshot_manifest_publication_tests.cpp)
target_include_directories(anonsync_sqlite_snapshot_manifest_publication_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_snapshot_manifest_publication_test PRIVATE
  anonsync_sqlite_snapshot_manifest_publication)
target_compile_options(anonsync_sqlite_snapshot_manifest_publication_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_projection_decoder_test
  tests/persistence/sqlite_projection_decoder_tests.cpp)
target_include_directories(anonsync_sqlite_projection_decoder_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_projection_decoder_test PRIVATE
  anonsync_sqlite_projection_decoder)
target_compile_options(anonsync_sqlite_projection_decoder_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_peer_ingress_projection_integrity_test
  tests/peer_ingress_projection_integrity_test.cpp)
target_include_directories(anonsync_peer_ingress_projection_integrity_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_peer_ingress_projection_integrity_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_peer_ingress_projection_integrity_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_peer_ingress_retention_integrity_test
  tests/peer_ingress_retention_integrity_test.cpp)
target_include_directories(anonsync_peer_ingress_retention_integrity_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_peer_ingress_retention_integrity_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_peer_ingress_retention_integrity_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_peer_ingress_schema_attestation_test
  tests/peer_ingress_schema_attestation_test.cpp)
target_include_directories(anonsync_peer_ingress_schema_attestation_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_peer_ingress_schema_attestation_test PRIVATE
  anonsync_peer_ingress_schema)
target_compile_options(anonsync_peer_ingress_schema_attestation_test PRIVATE
  -Wall -Wextra -Wpedantic)
if(TARGET anonsync_self_exec_test_process)
  target_include_directories(anonsync_peer_ingress_schema_attestation_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/tests)
  target_link_libraries(anonsync_peer_ingress_schema_attestation_test PRIVATE
    anonsync_self_exec_test_process)
endif()
# rev0789: independently compiled and executable proof for the durable,
# exact-VFS peer-ingress connection publication boundary.  Linking this test
# back through anonsync_core_lib would silently restore the 26-translation-unit
# dependency fan-out that this boundary exists to eliminate.
add_executable(anonsync_peer_ingress_connection_profile_test
  tests/persistence/peer_ingress_connection_profile_test.cpp)
target_include_directories(anonsync_peer_ingress_connection_profile_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_peer_ingress_connection_profile_test PRIVATE
  anonsync_peer_ingress_connection_profile)
target_compile_options(anonsync_peer_ingress_connection_profile_test PRIVATE
  -Wall -Wextra -Wpedantic)
get_target_property(ANONSYNC_PROFILE_TEST_LINK_LIBRARIES
  anonsync_peer_ingress_connection_profile_test LINK_LIBRARIES)
list(FIND ANONSYNC_PROFILE_TEST_LINK_LIBRARIES anonsync_core_lib
  ANONSYNC_PROFILE_TEST_CORE_LINK_INDEX)
if(NOT ANONSYNC_PROFILE_TEST_CORE_LINK_INDEX EQUAL -1)
  message(FATAL_ERROR
    "focused connection-profile proof must not link anonsync_core_lib")
endif()
get_target_property(ANONSYNC_PROFILE_LIBRARY_LINK_LIBRARIES
  anonsync_peer_ingress_connection_profile LINK_LIBRARIES)
list(FIND ANONSYNC_PROFILE_LIBRARY_LINK_LIBRARIES anonsync_core_lib
  ANONSYNC_PROFILE_LIBRARY_CORE_LINK_INDEX)
if(NOT ANONSYNC_PROFILE_LIBRARY_CORE_LINK_INDEX EQUAL -1)
  message(FATAL_ERROR
    "connection-profile library must not depend on anonsync_core_lib")
endif()

foreach(ANONSYNC_FOCUSED_BOUNDARY_TARGET
    anonsync_sync_bounded_regular_file
    anonsync_sync_bounded_regular_file_test
    anonsync_sync_replica_folder_observer
    anonsync_sync_replica_folder_observer_test
    anonsync_sync_replica_folder_scan_owner
    anonsync_sync_replica_folder_scan_owner_test
    anonsync_sync_replica_peer_service_integrity_evidence_test
    anonsync_sync_daemon_heartbeat_document
    anonsync_sync_daemon_heartbeat_document_test
    anonsync_sync_daemon_heartbeat_publication
    anonsync_sync_daemon_heartbeat_publication_test
    anonsync_sync_atomic_file_publication_state
    anonsync_sync_posix_directory_resolution
    anonsync_sync_posix_mount_namespace_authority
    anonsync_sync_posix_directory_resolution_test
    anonsync_sync_directory_authority
    anonsync_sync_atomic_file_publication
    anonsync_sync_atomic_file_publication_state_test
    anonsync_sync_atomic_file_publication_cutpoint_test
    anonsync_sync_atomic_file_publication_test
    anonsync_sync_atomic_file_publication_prepared_test
    anonsync_sync_atomic_file_reconciliation_test
    anonsync_sync_replica_file_effect_identity
    anonsync_sync_replica_file_delivery_protocol
    anonsync_sync_replica_file_effect_sqlite_owner
    anonsync_sync_replica_file_delivery_service
    anonsync_sync_replica_file_tls_dispatch
  anonsync_sync_replica_file_tls_exchange
    anonsync_sync_replica_file_effect_sqlite_owner_test
    anonsync_sync_replica_file_delivery_protocol_test
    anonsync_sync_replica_file_delivery_service_test
    anonsync_sync_checkpoint_owner_fence_policy
    anonsync_sync_checkpoint_owner_fence_policy_test
    anonsync_sync_checkpoint_owner_schema
    anonsync_sync_checkpoint_owner_schema_test
    anonsync_sync_checkpoint_owner_fence
    anonsync_sync_checkpoint_owner_fence_sqlite_test
    anonsync_process_incarnation
    anonsync_process_incarnation_test
    anonsync_system_epoch_identity
    anonsync_system_epoch_identity_test
    anonsync_thread_incarnation
    anonsync_thread_incarnation_test
    anonsync_sync_socket_readiness_identity
    anonsync_sync_socket_readiness_identity_test
    anonsync_process_identity_observation
    anonsync_process_identity_observation_test
    anonsync_sqlite_exact_value
    anonsync_sqlite_exact_value_test
    anonsync_ingress_sender_replay_record
    anonsync_ingress_sender_replay_record_test
    anonsync_sqlite_replay_ledger_schema_contract
    anonsync_sqlite_replay_ledger_schema_contract_test
    anonsync_sqlite_replay_ledger_write_gate
    anonsync_sqlite_replay_ledger_restore_lock
    anonsync_sqlite_replay_ledger_reset
    anonsync_sqlite_replay_ledger_reset_documents
    anonsync_sqlite_replay_ledger_reset_receipt_protocol
    anonsync_sqlite_replay_ledger_reset_test
    anonsync_sqlite_replay_ledger_reset_documents_test
    anonsync_sqlite_path_security
    anonsync_sqlite_snapshot_geometry
    anonsync_sqlite_snapshot_geometry_test
    anonsync_sqlite_live_backup
    anonsync_sqlite_live_backup_test
    anonsync_sqlite_retained_callback_claim
    anonsync_sqlite_verification_budget
    anonsync_sqlite_verification_budget_test
    anonsync_sqlite_busy_handler_owner
    anonsync_sqlite_busy_handler_owner_test
    anonsync_sqlite_owned_authorizer_policy
    anonsync_sqlite_owned_authorizer_policy_test
    anonsync_sqlite_authorizer_owner
    anonsync_sqlite_authorizer_owner_test
    anonsync_sqlite_persistence_process_authority_fork_test
    anonsync_sqlite_snapshot_seal
    anonsync_sqlite_snapshot_seal_test
    anonsync_sqlite_snapshot_geometry_binding_test
    anonsync_local_jsonl_replay_publication
    anonsync_local_jsonl_replay_publication_test
    anonsync_local_jsonl_replay_directory_authority
    anonsync_local_jsonl_replay_directory_authority_test
    anonsync_local_jsonl_replay_namespace
    anonsync_local_jsonl_replay_namespace_test
    anonsync_effect_transition_intent_publication
    anonsync_effect_transition_record_material
    anonsync_sqlite_snapshot_manifest_publication
    anonsync_effect_transition_intent_publication_test
    anonsync_effect_transition_record_material_test
    anonsync_sqlite_snapshot_manifest_publication_test
    anonsync_canonical_projection_verifier
    anonsync_sqlite_projection_decoder
    anonsync_canonical_projection_verifier_test
    anonsync_sqlite_projection_decoder_test
    anonsync_sha256_digest
    anonsync_sqlite_schema_identity
    anonsync_peer_ingress_schema
    anonsync_peer_ingress_schema_attestation_test
    anonsync_sqlite_source_first_move_test)
  get_target_property(ANONSYNC_FOCUSED_BOUNDARY_LINK_LIBRARIES
    ${ANONSYNC_FOCUSED_BOUNDARY_TARGET} LINK_LIBRARIES)
  list(FIND ANONSYNC_FOCUSED_BOUNDARY_LINK_LIBRARIES anonsync_core_lib
    ANONSYNC_FOCUSED_BOUNDARY_CORE_LINK_INDEX)
  if(NOT ANONSYNC_FOCUSED_BOUNDARY_CORE_LINK_INDEX EQUAL -1)
    message(FATAL_ERROR
      "focused persistence boundary must not depend on anonsync_core_lib: ${ANONSYNC_FOCUSED_BOUNDARY_TARGET}")
  endif()
endforeach()
if(TARGET anonsync_sync_bounded_regular_file_syscall_test)
  get_target_property(ANONSYNC_BOUNDED_READ_SYSCALL_LINK_LIBRARIES
    anonsync_sync_bounded_regular_file_syscall_test LINK_LIBRARIES)
  list(FIND ANONSYNC_BOUNDED_READ_SYSCALL_LINK_LIBRARIES anonsync_core_lib
    ANONSYNC_BOUNDED_READ_SYSCALL_CORE_LINK_INDEX)
  if(NOT ANONSYNC_BOUNDED_READ_SYSCALL_CORE_LINK_INDEX EQUAL -1)
    message(FATAL_ERROR
      "focused bounded-read syscall proof must not link anonsync_core_lib")
  endif()
endif()
if(TARGET anonsync_sync_atomic_file_publication_unlink_authority_test)
  get_target_property(ANONSYNC_UNLINK_AUTHORITY_LINK_LIBRARIES
    anonsync_sync_atomic_file_publication_unlink_authority_test LINK_LIBRARIES)
  list(FIND ANONSYNC_UNLINK_AUTHORITY_LINK_LIBRARIES anonsync_core_lib
    ANONSYNC_UNLINK_AUTHORITY_CORE_LINK_INDEX)
  if(NOT ANONSYNC_UNLINK_AUTHORITY_CORE_LINK_INDEX EQUAL -1)
    message(FATAL_ERROR
      "focused unlink-authority proof must not link anonsync_core_lib")
  endif()
endif()
if(TARGET anonsync_sqlite_replay_ledger_reset_crash_frontier_test)
  get_target_property(ANONSYNC_RESET_CRASH_FRONTIER_LINK_LIBRARIES
    anonsync_sqlite_replay_ledger_reset_crash_frontier_test LINK_LIBRARIES)
  list(FIND ANONSYNC_RESET_CRASH_FRONTIER_LINK_LIBRARIES anonsync_core_lib
    ANONSYNC_RESET_CRASH_FRONTIER_CORE_LINK_INDEX)
  if(NOT ANONSYNC_RESET_CRASH_FRONTIER_CORE_LINK_INDEX EQUAL -1)
    message(FATAL_ERROR
      "combined reset/publication crash-frontier proof must not link anonsync_core_lib")
  endif()
endif()
if(TARGET anonsync_test_process_topology_owner)
  get_target_property(ANONSYNC_TEST_PROCESS_TOPOLOGY_LINK_LIBRARIES
    anonsync_test_process_topology_owner LINK_LIBRARIES)
  if(ANONSYNC_TEST_PROCESS_TOPOLOGY_LINK_LIBRARIES)
    message(FATAL_ERROR
      "test process topology owner must remain dependency-free")
  endif()
endif()
if(TARGET anonsync_inherited_test_process)
  get_target_property(ANONSYNC_INHERITED_TEST_PROCESS_LINK_LIBRARIES
    anonsync_inherited_test_process LINK_LIBRARIES)
  if(NOT ANONSYNC_INHERITED_TEST_PROCESS_LINK_LIBRARIES STREQUAL
      "anonsync_test_process_topology_owner")
    message(FATAL_ERROR
      "inherited test process must depend only on the topology owner")
  endif()
endif()
if(TARGET anonsync_self_exec_test_process)
  get_target_property(ANONSYNC_SELF_EXEC_TEST_PROCESS_LINK_LIBRARIES
    anonsync_self_exec_test_process LINK_LIBRARIES)
  if(NOT ANONSYNC_SELF_EXEC_TEST_PROCESS_LINK_LIBRARIES STREQUAL
      "anonsync_test_process_topology_owner")
    message(FATAL_ERROR
      "self-exec test process must depend only on the topology owner")
  endif()
endif()
if(ANONSYNC_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  set(ANONSYNC_SANITIZER_COMPILE_TARGETS
    anonsync_core_lib
    anonsync_reporting_selftests_lib
    anonsync_sync_domain_selftests_lib
    anonsync_sqlite_replay_ledger_selftests_lib
    anonsync_sync_atomic_file_publication_state
    anonsync_sync_posix_directory_resolution
    anonsync_sync_posix_mount_namespace_authority
    anonsync_sync_posix_directory_resolution_test
    anonsync_sync_directory_authority
    anonsync_sync_atomic_file_publication
    anonsync_sync_bounded_regular_file
    anonsync_sync_bounded_regular_file_test
    anonsync_sync_replica_folder_observer
    anonsync_sync_replica_folder_observer_test
    anonsync_sync_daemon_heartbeat_document
    anonsync_sync_daemon_heartbeat_document_test
    anonsync_sync_daemon_heartbeat_publication
    anonsync_sync_daemon_heartbeat_publication_test
    anonsync_sync_atomic_file_publication_state_test
    anonsync_sync_atomic_file_publication_cutpoint_test
    anonsync_sync_atomic_file_publication_test
    anonsync_sync_atomic_file_publication_prepared_test
    anonsync_sync_checkpoint_scheduler_policy
    anonsync_sync_checkpoint_scheduler_policy_test
    anonsync_sync_checkpoint_owner_fence_policy
    anonsync_sync_checkpoint_owner_fence_policy_test
    anonsync_sync_checkpoint_owner_schema
    anonsync_sync_checkpoint_owner_schema_test
    anonsync_sync_checkpoint_owner_fence
    anonsync_sync_checkpoint_owner_fence_sqlite_test
    anonsync_sha256_digest
    anonsync_sync_peer_transport_digest_bound_frame
    anonsync_sync_peer_transport_digest_bound_frame_test
    anonsync_security_tuple_digest
    anonsync_sqlite_schema_identity
    anonsync_peer_ingress_schema
    anonsync_process_incarnation
    anonsync_thread_incarnation
    anonsync_system_epoch_identity
    anonsync_process_identity_observation
    anonsync_peer_ingress_connection_profile
    anonsync_sqlite_database_mutex_guard
    anonsync_sqlite_retained_callback_claim
    anonsync_sqlite_busy_handler_owner
    anonsync_sqlite_busy_handler_owner_test
    anonsync_sqlite_owned_authorizer_policy
    anonsync_sqlite_owned_authorizer_policy_test
    anonsync_sqlite_authorizer_owner
    anonsync_sqlite_authorizer_owner_test
    anonsync_sqlite_exact_value
    anonsync_ingress_sender_replay_record
    anonsync_sqlite_replay_ledger_schema_contract
    anonsync_sqlite_replay_ledger_write_gate
    anonsync_sqlite_replay_ledger_restore_lock
    anonsync_sqlite_replay_ledger_reset
    anonsync_sqlite_replay_ledger_reset_documents
    anonsync_sqlite_replay_ledger_reset_receipt_protocol
    anonsync_sqlite_path_security
    anonsync_sqlite_snapshot_geometry
    anonsync_sqlite_live_backup
    anonsync_sqlite_verification_budget
    anonsync_sqlite_snapshot_seal
    anonsync_local_jsonl_replay_directory_authority
    anonsync_local_jsonl_replay_publication
    anonsync_local_jsonl_replay_namespace
    anonsync_effect_transition_intent_publication
    anonsync_effect_transition_record_material
    anonsync_sqlite_snapshot_manifest_publication
    anonsync_canonical_projection_verifier
    anonsync_sqlite_projection_decoder
    anonsync_sqlite_runtime
    anonsync_sqlite_support
    anonsync_sqlite_exact_value_test
    anonsync_ingress_sender_replay_record_test
    anonsync_sqlite_replay_ledger_schema_contract_test
    anonsync_sqlite_replay_ledger_reset_test
    anonsync_sqlite_replay_ledger_reset_documents_test
    anonsync_sqlite_snapshot_geometry_test
    anonsync_sqlite_live_backup_test
    anonsync_sqlite_verification_budget_test
    anonsync_process_incarnation_test
    anonsync_thread_incarnation_test
    anonsync_system_epoch_identity_test
    anonsync_process_identity_observation_test
    anonsync_sqlite_persistence_process_authority_fork_test
    anonsync_sqlite_snapshot_seal_test
    anonsync_sqlite_snapshot_geometry_binding_test
    anonsync_local_jsonl_replay_directory_authority_test
    anonsync_local_jsonl_replay_publication_test
    anonsync_local_jsonl_replay_namespace_test
    anonsync_local_jsonl_replay_backend_namespace_test
    anonsync_local_jsonl_replay_crash_state_machine_test
    anonsync_effect_transition_intent_publication_test
    anonsync_effect_transition_record_material_test
    anonsync_sqlite_snapshot_manifest_publication_test
    anonsync_sqlite_snapshot_sidecar_binding_test
    anonsync_sqlite_replay_ledger_schema_integrity_test
    anonsync_sqlite_restore_namespace_authority_test
    anonsync_sqlite_backup_namespace_authority_test
    anonsync_sqlite_ingress_sender_replay_integrity_test
    anonsync_sqlite_runtime_policy_test
    anonsync_sqlite_support_test
    anonsync_sqlite_connection_authority_test
    anonsync_sqlite_transaction_exception_composition_test
    anonsync_sqlite_process_authority_fork_test
    anonsync_sqlite_owner_generation_borrow_test
    anonsync_sqlite_source_first_move_test
    anonsync_core
    anonsync_sync_peer_ingress_lifecycle_selftest
    anonsync_json_parser
    anonsync_sync_manifest_validation
    anonsync_sync_manifest_validation_test
    anonsync_sync_manifest_stream_decoder
    anonsync_sync_manifest_stream_decoder_test
    anonsync_sync_sqlite_manifest_chunk_subset
    anonsync_sync_sqlite_manifest_chunk_subset_test
    anonsync_sync_sqlite_sidecar_claimed_path_snapshot
    anonsync_sync_sqlite_sidecar_claimed_path_snapshot_test
    anonsync_sync_manifest_identity
    anonsync_sync_manifest_identity_test
    anonsync_sync_manifest_hash_locale_test
    anonsync_sync_conflict_resolution
    anonsync_sync_conflict_resolution_test
    anonsync_sync_manifest_conflict_convergence_test
    anonsync_sync_replica_model
    anonsync_sync_replica_outbox_lease
    anonsync_sync_replica_sqlite_owner
    anonsync_sync_replica_folder_scan_owner
    anonsync_sync_replica_operational_database
    anonsync_sync_replica_folder_process
    anonsync_sync_replica_folder_wake
    anonsync_sync_replica_sync_once
    anonsync_sync_replica_peer_server_owner
    anonsync_sync_replica_peer_service
    anonsync_sync_replica_peer_service_singleton
    anonsync_sync_replica_peer_service_configuration
    anonsync_sync_replica_peer_service_provisioning
    anonsync_sync_replica_peer_service_status
    anonsync_sync_linked_peer_pairing
    anonsync_sync_local_share_setup
    anonsync_sync_linked_peer_user_layout
    anonsync_sync_sibling_process
    anonsync_sync_local_status_socket
    anonsync_sync_linux_process_resources
    anonsync_sync_systemd_notify
    anonsync_sync_replica_delivery_protocol
    anonsync_sync_replica_reconciliation_protocol
    anonsync_sync_replica_delivery_channel
    anonsync_sync_replica_delivery_service
    anonsync_sync_replica_reconciliation_service
    anonsync_sync_replica_file_effect_identity
    anonsync_sync_replica_file_delivery_protocol
    anonsync_sync_replica_file_effect_sqlite_owner
    anonsync_sync_replica_file_delivery_service
    anonsync_sync_replica_file_tls_dispatch
    anonsync_sync_replica_file_tls_exchange
    anonsync_sync_replica_reconciliation_tls_exchange
    anonsync_sync_replica_file_tls_server
    anonsync_sync_replica_session_supervisor_test
    anonsync_sync_replica_stream_connector_test
    anonsync_replica
    anonsync_folder
    anonsync_sync
    anonsync_sync_replica_folder_process_test
    anonsync_sync_replica_folder_wake_test
    anonsync_sync_replica_sync_once_test
    anonsync_sync_socket_readiness_identity
    anonsync_sync_replica_tls_transport
    anonsync_sync_replica_tls_poll
    anonsync_sync_replica_network_simulator
    anonsync_sync_replica_network_model_test
    anonsync_sync_replica_hash_graph_projection_test
    anonsync_sync_replica_allocation_atomicity_test
    anonsync_sync_replica_aggregate_budget_test
    anonsync_sync_replica_capacity_backpressure_test
    anonsync_sync_replica_outbox_clock
    anonsync_sync_replica_outbox_lease_test
    anonsync_sync_replica_outbox_clock_test
    anonsync_sync_replica_delivery_protocol_test
    anonsync_sync_replica_selective_sync_policy_test
    anonsync_sync_replica_reconciliation_protocol_test
    anonsync_sync_replica_reconciliation_frame_memory_test
    anonsync_sync_replica_reconciliation_memory_shape_test
    anonsync_sync_replica_reconciliation_source_frame_memory_test
    anonsync_sync_replica_source_manifest_restart_test
    anonsync_sync_replica_sqlite_owner_test
    anonsync_sync_replica_prepared_publication_test
    anonsync_sync_replica_folder_scan_owner_test
    anonsync_sync_replica_peer_service_integrity_evidence_test
    anonsync_sync_replica_delivery_test_channel
    anonsync_sync_replica_delivery_service_test
    anonsync_sync_replica_reconciliation_service_test
    anonsync_sync_atomic_file_reconciliation_test
    anonsync_sync_replica_file_effect_sqlite_owner_test
    anonsync_sync_replica_file_delivery_protocol_test
    anonsync_sync_replica_file_delivery_service_test
    anonsync_resumable_sha256
    anonsync_resumable_sha256_test
    anonsync_sync_replica_file_payload_verification_index
    anonsync_sync_replica_file_payload_verification_index_test
    anonsync_sync_replica_file_payload_scrub_state
    anonsync_sync_replica_file_payload_scrub_state_test
    anonsync_sync_replica_file_payload_terminal_verification_state
    anonsync_sync_replica_file_payload_terminal_verification_state_test
    anonsync_sync_replica_file_payload_retention_mark
    anonsync_sync_replica_file_payload_retention_mark_test
    anonsync_sync_replica_source_manifest_checkpoint
    anonsync_sync_replica_source_manifest_checkpoint_test
    anonsync_sync_replica_reconciliation_compact_manifest
    anonsync_sync_replica_reconciliation_compact_manifest_test
    anonsync_sync_posix_regular_file_snapshot_codec
    anonsync_sync_replica_file_payload_store
    anonsync_sync_replica_file_payload_store_test
    anonsync_sync_replica_terminal_verification_fixture
    anonsync_sync_replica_deployment_identity
    anonsync_sync_replica_deployment_manifest
    anonsync_sync_replica_deployment_manifest_test
    anonsync_sync_replica_bootstrap_record
    anonsync_sync_replica_bootstrap_record_test
    anonsync_sync_replica_deployment_binding
    anonsync_sync_replica_deployment_binding_test
    anonsync_sync_socket_readiness_identity_test
    anonsync_sync_local_status_socket_test
    anonsync_sync_linux_process_resources_test
    anonsync_sync_linux_process_resources_fixture
    anonsync_sync_systemd_notify_test
    anonsync_sync_linked_peer_user_layout_test
    anonsync_sync_replica_tls_transport_test
    anonsync_fuzz_json_codec
    anonsync_fuzz_jwt_codec
    anonsync_fuzz_route_event_ledger
    anonsync_sync_peer_ingress_wire_test
    anonsync_peer_ingress_wire_adversarial_test
    anonsync_sync_peer_wire_compatibility_test
    anonsync_sqlite_runtime_payload_store_test
    anonsync_canonical_projection_verifier_test
    anonsync_sqlite_projection_decoder_test
    anonsync_peer_ingress_projection_integrity_test
    anonsync_peer_ingress_retention_integrity_test
    anonsync_peer_ingress_schema_attestation_test
    anonsync_peer_ingress_connection_profile_test)
  if(TARGET anonsync_sync_bounded_regular_file_syscall_test)
    list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS
      anonsync_sync_bounded_regular_file_syscall_test)
  endif()
  if(TARGET anonsync_sync_replica_folder_observer_race_test)
    list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS
      anonsync_sync_replica_folder_observer_race_test)
  endif()
  if(TARGET anonsync_sync_atomic_file_publication_unlink_authority_test)
    list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS
      anonsync_sync_atomic_file_publication_unlink_authority_test)
  endif()
  if(TARGET anonsync_sqlite_replay_ledger_reset_crash_frontier_test)
    list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS
      anonsync_sqlite_replay_ledger_reset_crash_frontier_test)
  endif()
  if(TARGET anonsync_test_process_topology_owner)
    list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS
      anonsync_test_process_topology_owner)
  endif()
  if(TARGET anonsync_test_process_topology_owner_test)
    list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS
      anonsync_test_process_topology_owner_test)
  endif()
  if(TARGET anonsync_inherited_test_process)
    list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS
      anonsync_inherited_test_process
      anonsync_inherited_test_process_test)
  endif()
  if(TARGET anonsync_self_exec_test_process)
    list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS
      anonsync_self_exec_test_process
      anonsync_self_exec_test_process_test)
  endif()
  if(TARGET anonsync_sqlite_transaction_allocator_fault_test)
    list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS
      anonsync_sqlite_transaction_allocator_fault_test)
  endif()
  # Keep the multi-megabyte reviewed amalgamation out of the default C++
  # sanitizer lane. Instrumenting it dominates cloud builds and can prevent
  # the AnonSync ownership code from being exercised at all. A dedicated job
  # can still opt in when auditing the third-party boundary itself.
  if(TARGET anonsync_sqlite3 AND ANONSYNC_SANITIZE_BUNDLED_SQLITE)
    list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS anonsync_sqlite3)
  endif()
  # This inherited graph keeps explicit compile and final-link sanitizer
  # inventories. Keep both in sync for every executable: an instrumented static
  # dependency can otherwise compile normally and fail only at the clean
  # sanitizer link frontier. The source-audit corpus currently parses this exact
  # split, so collapsing it is a separate audit-refactor rather than a drive-by
  # product change.
  foreach(tgt IN LISTS ANONSYNC_SANITIZER_COMPILE_TARGETS)
    target_compile_options(${tgt} PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
  endforeach()
  foreach(tgt
      anonsync_core
      anonsync_sync_peer_ingress_lifecycle_selftest
      anonsync_sync_manifest_validation_test
      anonsync_sync_manifest_stream_decoder_test
      anonsync_sync_sqlite_manifest_chunk_subset_test
      anonsync_sync_sqlite_sidecar_claimed_path_snapshot_test
      anonsync_sync_manifest_identity_test
      anonsync_sync_manifest_hash_locale_test
      anonsync_sync_peer_transport_digest_bound_frame_test
      anonsync_sync_conflict_resolution_test
      anonsync_sync_manifest_conflict_convergence_test
      anonsync_sync_replica_network_model_test
      anonsync_sync_replica_hash_graph_projection_test
      anonsync_sync_replica_allocation_atomicity_test
      anonsync_sync_replica_aggregate_budget_test
      anonsync_sync_replica_capacity_backpressure_test
      anonsync_sync_replica_outbox_lease_test
      anonsync_sync_replica_outbox_clock_test
      anonsync_sync_replica_delivery_protocol_test
      anonsync_sync_replica_selective_sync_policy_test
      anonsync_sync_replica_reconciliation_protocol_test
      anonsync_sync_replica_reconciliation_frame_memory_test
      anonsync_sync_replica_reconciliation_memory_shape_test
      anonsync_sync_replica_reconciliation_source_frame_memory_test
      anonsync_sync_replica_source_manifest_restart_test
      anonsync_sync_replica_sqlite_owner_test
      anonsync_sync_replica_prepared_publication_test
      anonsync_sync_replica_folder_scan_owner_test
      anonsync_sync_replica_peer_service_integrity_evidence_test
      anonsync_sync_replica_delivery_service_test
      anonsync_sync_replica_reconciliation_service_test
      anonsync_sync_atomic_file_reconciliation_test
      anonsync_sync_replica_file_effect_sqlite_owner_test
      anonsync_sync_replica_file_delivery_protocol_test
      anonsync_sync_replica_file_delivery_service_test
      anonsync_resumable_sha256_test
      anonsync_sync_replica_file_payload_verification_index_test
      anonsync_sync_replica_file_payload_scrub_state_test
      anonsync_sync_replica_file_payload_terminal_verification_state_test
      anonsync_sync_replica_file_payload_retention_mark_test
      anonsync_sync_replica_source_manifest_checkpoint_test
      anonsync_sync_replica_reconciliation_compact_manifest_test
      anonsync_sync_replica_file_payload_store_test
      anonsync_sync_replica_terminal_verification_fixture
      anonsync_sync_replica_deployment_manifest_test
      anonsync_sync_replica_bootstrap_record_test
      anonsync_sync_replica_deployment_binding_test
      anonsync_sync_replica_session_supervisor_test
      anonsync_sync_replica_stream_connector_test
      anonsync_replica
      anonsync_folder
      anonsync_sync
      anonsync_sync_replica_database_backup
      anonsync_sync_replica_folder_process_test
      anonsync_sync_replica_folder_wake_test
      anonsync_sync_replica_sync_once_test
      anonsync_sync_socket_readiness_identity_test
      anonsync_sync_local_status_socket_test
      anonsync_sync_linux_process_resources_test
      anonsync_sync_linux_process_resources_fixture
      anonsync_sync_systemd_notify_test
      anonsync_sync_linked_peer_user_layout_test
      anonsync_sync_replica_tls_transport_test
      anonsync_fuzz_json_codec
      anonsync_fuzz_jwt_codec
      anonsync_fuzz_route_event_ledger
      anonsync_sync_bounded_regular_file_test
      anonsync_sync_replica_folder_observer_test
      anonsync_sync_daemon_heartbeat_document_test
      anonsync_sync_daemon_heartbeat_publication_test
      anonsync_sync_atomic_file_publication_state_test
      anonsync_sync_atomic_file_publication_cutpoint_test
      anonsync_sync_atomic_file_publication_test
      anonsync_sync_posix_directory_resolution_test
      anonsync_sync_atomic_file_publication_prepared_test
      anonsync_sync_checkpoint_scheduler_policy_test
      anonsync_sync_checkpoint_owner_fence_policy_test
      anonsync_sync_checkpoint_owner_schema_test
      anonsync_sqlite_exact_value_test
      anonsync_ingress_sender_replay_record_test
      anonsync_sqlite_replay_ledger_schema_contract_test
      anonsync_sqlite_replay_ledger_reset_test
      anonsync_sqlite_replay_ledger_reset_documents_test
      anonsync_sqlite_snapshot_geometry_test
      anonsync_sqlite_live_backup_test
      anonsync_sqlite_verification_budget_test
      anonsync_process_incarnation_test
      anonsync_thread_incarnation_test
      anonsync_system_epoch_identity_test
      anonsync_process_identity_observation_test
      anonsync_sqlite_persistence_process_authority_fork_test
      anonsync_sqlite_snapshot_seal_test
      anonsync_sqlite_snapshot_geometry_binding_test
      anonsync_local_jsonl_replay_directory_authority_test
      anonsync_local_jsonl_replay_publication_test
      anonsync_local_jsonl_replay_namespace_test
      anonsync_local_jsonl_replay_backend_namespace_test
      anonsync_local_jsonl_replay_crash_state_machine_test
      anonsync_effect_transition_intent_publication_test
      anonsync_effect_transition_record_material_test
      anonsync_sqlite_snapshot_manifest_publication_test
      anonsync_sqlite_snapshot_sidecar_binding_test
      anonsync_sqlite_replay_ledger_schema_integrity_test
      anonsync_sqlite_restore_namespace_authority_test
      anonsync_sqlite_backup_namespace_authority_test
      anonsync_sqlite_ingress_sender_replay_integrity_test
      anonsync_sqlite_runtime_policy_test
      anonsync_sqlite_support_test
      anonsync_sqlite_connection_authority_test
      anonsync_sqlite_busy_handler_owner_test
      anonsync_sqlite_owned_authorizer_policy_test
      anonsync_sqlite_authorizer_owner_test
      anonsync_sqlite_transaction_exception_composition_test
      anonsync_sqlite_process_authority_fork_test
      anonsync_sqlite_owner_generation_borrow_test
      anonsync_sqlite_source_first_move_test
      anonsync_sync_checkpoint_owner_fence_sqlite_test
      anonsync_sync_peer_ingress_wire_test
      anonsync_peer_ingress_wire_adversarial_test
      anonsync_sync_peer_wire_compatibility_test
      anonsync_sqlite_runtime_payload_store_test
      anonsync_canonical_projection_verifier_test
      anonsync_sqlite_projection_decoder_test
      anonsync_peer_ingress_projection_integrity_test
      anonsync_peer_ingress_retention_integrity_test
      anonsync_peer_ingress_schema_attestation_test
      anonsync_peer_ingress_connection_profile_test)
    target_link_options(${tgt} PRIVATE -fsanitize=address,undefined)
  endforeach()
  if(TARGET anonsync_sync_bounded_regular_file_syscall_test)
    target_link_options(anonsync_sync_bounded_regular_file_syscall_test PRIVATE
      -fsanitize=address,undefined)
  endif()
  if(TARGET anonsync_sync_replica_folder_observer_race_test)
    target_link_options(anonsync_sync_replica_folder_observer_race_test PRIVATE
      -fsanitize=address,undefined)
  endif()
  if(TARGET anonsync_sync_atomic_file_publication_unlink_authority_test)
    target_link_options(anonsync_sync_atomic_file_publication_unlink_authority_test PRIVATE
      -fsanitize=address,undefined)
  endif()
  if(TARGET anonsync_sqlite_replay_ledger_reset_crash_frontier_test)
    target_link_options(
      anonsync_sqlite_replay_ledger_reset_crash_frontier_test PRIVATE
      -fsanitize=address,undefined)
  endif()
  if(TARGET anonsync_test_process_topology_owner_test)
    target_link_options(anonsync_test_process_topology_owner_test PRIVATE
      -fsanitize=address,undefined)
  endif()
  if(TARGET anonsync_inherited_test_process_test)
    target_link_options(anonsync_inherited_test_process_test PRIVATE
      -fsanitize=address,undefined)
  endif()
  if(TARGET anonsync_self_exec_test_process_test)
    target_link_options(anonsync_self_exec_test_process_test PRIVATE
      -fsanitize=address,undefined)
  endif()
  if(TARGET anonsync_sqlite_transaction_allocator_fault_test)
    target_link_options(anonsync_sqlite_transaction_allocator_fault_test PRIVATE
      -fsanitize=address,undefined)
  endif()
endif()

# One deliberately small build surface for the shipping replica path. It does
# not join the default all-target graph; developers can build this target and
# run the matching CTest label without maintaining a long target/test regex.
add_custom_target(anonsync_product_lane
  DEPENDS
    anonsync_replica
    anonsync_folder
    anonsync_sync
    anonsync_sync_linked_peer_user_layout_test
    anonsync_sync_local_status_socket_test
    anonsync_sync_linux_process_resources_test
    anonsync_sync_linux_process_resources_fixture
    anonsync_sync_systemd_notify_test
    anonsync_sync_replica_folder_observer_test
    anonsync_sync_replica_network_model_test
    anonsync_sync_replica_sqlite_owner_test
    anonsync_sync_replica_prepared_publication_test
    anonsync_sync_replica_folder_scan_owner_test
    anonsync_sync_replica_peer_service_integrity_evidence_test
    anonsync_sync_replica_folder_process_test
    anonsync_sync_replica_folder_wake_test
    anonsync_sync_replica_sync_once_test
    anonsync_sync_replica_delivery_service_test
    anonsync_sync_replica_selective_sync_policy_test
    anonsync_sync_replica_reconciliation_protocol_test
    anonsync_sync_replica_reconciliation_frame_memory_test
    anonsync_sync_replica_reconciliation_memory_shape_test
    anonsync_sync_replica_reconciliation_source_frame_memory_test
    anonsync_sync_replica_source_manifest_restart_test
    anonsync_sync_replica_reconciliation_service_test
    anonsync_sync_replica_session_supervisor_test
    anonsync_sync_replica_stream_connector_test
    anonsync_sync_replica_tls_transport_test
    anonsync_sync_replica_file_delivery_service_test
    anonsync_resumable_sha256_test
    anonsync_sync_replica_file_payload_verification_index_test
    anonsync_sync_replica_file_payload_scrub_state_test
    anonsync_sync_replica_file_payload_terminal_verification_state_test
    anonsync_sync_replica_terminal_verification_fixture
    anonsync_sync_replica_file_payload_retention_mark_test
    anonsync_sync_replica_source_manifest_checkpoint_test
    anonsync_sync_replica_reconciliation_compact_manifest_test
    anonsync_sync_replica_content_defined_chunker_test)
if(TARGET anonsync_sync_replica_folder_observer_race_test)
  add_dependencies(anonsync_product_lane
    anonsync_sync_replica_folder_observer_race_test)
endif()

include(CTest)
if(ANONSYNC_ENABLE_LIBFUZZER)
  add_test(NAME anonsync_fuzz_sqlite_projection_decoder_smoke
    COMMAND anonsync_fuzz_sqlite_projection_decoder
      -runs=10000 -max_len=512 -seed=789
      -print_funcs=0 -print_final_stats=1)
  add_test(NAME anonsync_fuzz_sqlite_snapshot_geometry_smoke
    COMMAND anonsync_fuzz_sqlite_snapshot_geometry
      -runs=10000 -max_len=256 -seed=798
      -print_funcs=0 -print_final_stats=1)
endif()
add_test(NAME anonsync_core_help COMMAND anonsync_core --help)
add_test(NAME anonsync_sync_peer_transport_digest_bound_frame_test
  COMMAND anonsync_sync_peer_transport_digest_bound_frame_test)
add_test(NAME anonsync_sync_conflict_resolution_test
  COMMAND anonsync_sync_conflict_resolution_test)
add_test(NAME anonsync_sync_manifest_validation_test
  COMMAND anonsync_sync_manifest_validation_test)
add_test(NAME anonsync_sync_manifest_stream_decoder_test
  COMMAND anonsync_sync_manifest_stream_decoder_test)
add_test(NAME anonsync_sync_sqlite_manifest_chunk_subset_test
  COMMAND anonsync_sync_sqlite_manifest_chunk_subset_test)
add_test(NAME anonsync_sync_sqlite_sidecar_claimed_path_snapshot_test
  COMMAND anonsync_sync_sqlite_sidecar_claimed_path_snapshot_test)
add_test(NAME anonsync_sync_manifest_identity_test
  COMMAND anonsync_sync_manifest_identity_test)
add_test(NAME anonsync_sync_manifest_hash_locale_test
  COMMAND anonsync_sync_manifest_hash_locale_test)
add_test(NAME anonsync_sync_manifest_conflict_convergence_test
  COMMAND anonsync_sync_manifest_conflict_convergence_test)
add_test(NAME anonsync_sync_replica_network_model_test
  COMMAND anonsync_sync_replica_network_model_test)
add_test(NAME anonsync_sync_replica_hash_graph_projection_test
  COMMAND anonsync_sync_replica_hash_graph_projection_test)
add_test(NAME anonsync_sync_replica_allocation_atomicity_test
  COMMAND anonsync_sync_replica_allocation_atomicity_test)
add_test(NAME anonsync_sync_replica_aggregate_budget_test
  COMMAND anonsync_sync_replica_aggregate_budget_test)
add_test(NAME anonsync_sync_replica_capacity_backpressure_test
  COMMAND anonsync_sync_replica_capacity_backpressure_test)
set_tests_properties(anonsync_sync_replica_capacity_backpressure_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sync_replica_outbox_lease_test
  COMMAND anonsync_sync_replica_outbox_lease_test)
add_test(NAME anonsync_sync_replica_outbox_clock_test
  COMMAND anonsync_sync_replica_outbox_clock_test)
add_test(NAME anonsync_sync_replica_delivery_protocol_test
  COMMAND anonsync_sync_replica_delivery_protocol_test)
add_test(NAME anonsync_sync_replica_selective_sync_policy_test
  COMMAND anonsync_sync_replica_selective_sync_policy_test)
set_tests_properties(anonsync_sync_replica_selective_sync_policy_test
  PROPERTIES TIMEOUT 20 LABELS "product")
add_test(NAME anonsync_sync_replica_reconciliation_protocol_test
  COMMAND anonsync_sync_replica_reconciliation_protocol_test)
set_tests_properties(anonsync_sync_replica_reconciliation_protocol_test
  PROPERTIES TIMEOUT 30 LABELS "product")
add_test(NAME anonsync_sync_replica_reconciliation_frame_memory_test
  COMMAND anonsync_sync_replica_reconciliation_frame_memory_test)
set_tests_properties(anonsync_sync_replica_reconciliation_frame_memory_test
  PROPERTIES TIMEOUT 30 LABELS "product")
add_test(NAME anonsync_sync_replica_reconciliation_memory_shape_test
  COMMAND anonsync_sync_replica_reconciliation_memory_shape_test)
set_tests_properties(anonsync_sync_replica_reconciliation_memory_shape_test
  PROPERTIES TIMEOUT 30 LABELS "product")
add_test(NAME anonsync_sync_replica_reconciliation_source_frame_memory_test
  COMMAND anonsync_sync_replica_reconciliation_source_frame_memory_test)
set_tests_properties(
  anonsync_sync_replica_reconciliation_source_frame_memory_test
  PROPERTIES TIMEOUT 120 LABELS "product")
add_test(NAME anonsync_sync_replica_source_manifest_restart_test
  COMMAND anonsync_sync_replica_source_manifest_restart_test)
set_tests_properties(anonsync_sync_replica_source_manifest_restart_test
  PROPERTIES TIMEOUT 120 LABELS "product")
add_test(NAME anonsync_sync_replica_sqlite_owner_test
  COMMAND anonsync_sync_replica_sqlite_owner_test)
set_tests_properties(anonsync_sync_replica_sqlite_owner_test
  PROPERTIES TIMEOUT 60)
add_test(NAME anonsync_sync_replica_prepared_publication_test
  COMMAND anonsync_sync_replica_prepared_publication_test)
set_tests_properties(anonsync_sync_replica_prepared_publication_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sync_replica_folder_scan_owner_test
  COMMAND anonsync_sync_replica_folder_scan_owner_test)
# This executable intentionally includes large-file streaming, restart, crash-
# residue, path-race, and many-file convergence cases. Keep the ordinary build
# at a sixty-second stall detector, but account explicitly for the measured
# Clang ASan+UBSan expansion instead of letting instrumentation race the timeout.
set(ANONSYNC_FOLDER_SCAN_OWNER_TEST_TIMEOUT_SECONDS 60)
if(ANONSYNC_ENABLE_SANITIZERS)
  set(ANONSYNC_FOLDER_SCAN_OWNER_TEST_TIMEOUT_SECONDS 120)
endif()
set_tests_properties(anonsync_sync_replica_folder_scan_owner_test
  PROPERTIES
    TIMEOUT ${ANONSYNC_FOLDER_SCAN_OWNER_TEST_TIMEOUT_SECONDS}
    LABELS "product")
add_test(NAME anonsync_sync_replica_peer_service_integrity_evidence_test
  COMMAND anonsync_sync_replica_peer_service_integrity_evidence_test)
set_tests_properties(
  anonsync_sync_replica_peer_service_integrity_evidence_test
  PROPERTIES TIMEOUT 20 LABELS "product")
add_test(NAME anonsync_sync_replica_folder_process_test
  COMMAND anonsync_sync_replica_folder_process_test)
set_tests_properties(anonsync_sync_replica_folder_process_test
  PROPERTIES TIMEOUT 20 LABELS "product")
add_test(NAME anonsync_sync_replica_folder_wake_test
  COMMAND anonsync_sync_replica_folder_wake_test)
set_tests_properties(anonsync_sync_replica_folder_wake_test
  PROPERTIES TIMEOUT 20 LABELS "product")
add_test(NAME anonsync_sync_replica_sync_once_test
  COMMAND anonsync_sync_replica_sync_once_test)
set_tests_properties(anonsync_sync_replica_sync_once_test
  PROPERTIES TIMEOUT 20 LABELS "product")
add_test(NAME anonsync_sync_replica_delivery_service_test
  COMMAND anonsync_sync_replica_delivery_service_test)
set_tests_properties(anonsync_sync_replica_delivery_service_test
  PROPERTIES TIMEOUT 60)
add_test(NAME anonsync_sync_replica_reconciliation_service_test
  COMMAND anonsync_sync_replica_reconciliation_service_test)
set_tests_properties(anonsync_sync_replica_reconciliation_service_test
  PROPERTIES TIMEOUT 180 LABELS "product")
add_test(NAME anonsync_sync_local_status_socket_test
  COMMAND anonsync_sync_local_status_socket_test)
set_tests_properties(anonsync_sync_local_status_socket_test
  PROPERTIES TIMEOUT 20 LABELS "product")
add_test(NAME anonsync_sync_linux_process_resources_test
  COMMAND anonsync_sync_linux_process_resources_test)
set_tests_properties(anonsync_sync_linux_process_resources_test
  PROPERTIES TIMEOUT 20 LABELS "product")
add_test(NAME anonsync_sync_systemd_notify_test
  COMMAND anonsync_sync_systemd_notify_test)
set_tests_properties(anonsync_sync_systemd_notify_test
  PROPERTIES TIMEOUT 20 LABELS "product")
add_test(NAME anonsync_sync_linked_peer_user_layout_test
  COMMAND anonsync_sync_linked_peer_user_layout_test)
set_tests_properties(anonsync_sync_linked_peer_user_layout_test
  PROPERTIES TIMEOUT 20 LABELS "product")
add_test(NAME anonsync_sync_socket_readiness_identity_test
  COMMAND anonsync_sync_socket_readiness_identity_test)
set_tests_properties(anonsync_sync_socket_readiness_identity_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sync_replica_tls_io_policy_test
  COMMAND anonsync_sync_replica_tls_io_policy_test)
set_tests_properties(anonsync_sync_replica_tls_io_policy_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sync_replica_session_supervisor_test
  COMMAND anonsync_sync_replica_session_supervisor_test)
set_tests_properties(anonsync_sync_replica_session_supervisor_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sync_replica_stream_connector_test
  COMMAND anonsync_sync_replica_stream_connector_test)
set_tests_properties(anonsync_sync_replica_stream_connector_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sync_replica_tls_transport_test
  COMMAND anonsync_sync_replica_tls_transport_test)
set_tests_properties(anonsync_sync_replica_tls_transport_test
  PROPERTIES TIMEOUT 60)
set_tests_properties(
  anonsync_sync_replica_network_model_test
  anonsync_sync_replica_sqlite_owner_test
  anonsync_sync_replica_prepared_publication_test
  anonsync_sync_replica_folder_scan_owner_test
  anonsync_sync_replica_peer_service_integrity_evidence_test
  anonsync_sync_replica_folder_process_test
  anonsync_sync_replica_folder_wake_test
  anonsync_sync_replica_sync_once_test
  anonsync_sync_replica_delivery_service_test
  anonsync_sync_replica_selective_sync_policy_test
  anonsync_sync_replica_reconciliation_protocol_test
  anonsync_sync_replica_reconciliation_service_test
  anonsync_sync_local_status_socket_test
  anonsync_sync_systemd_notify_test
  anonsync_sync_replica_session_supervisor_test
  anonsync_sync_replica_stream_connector_test
  anonsync_sync_replica_tls_transport_test
  PROPERTIES LABELS "product")
set_tests_properties(
  anonsync_sync_peer_transport_digest_bound_frame_test
  anonsync_sync_conflict_resolution_test
  anonsync_sync_manifest_validation_test
  anonsync_sync_manifest_stream_decoder_test
  anonsync_sync_sqlite_manifest_chunk_subset_test
  anonsync_sync_sqlite_sidecar_claimed_path_snapshot_test
  anonsync_sync_manifest_identity_test
  anonsync_sync_manifest_hash_locale_test
  anonsync_sync_manifest_conflict_convergence_test
  anonsync_sync_replica_network_model_test
  anonsync_sync_replica_hash_graph_projection_test
  anonsync_sync_replica_allocation_atomicity_test
  anonsync_sync_replica_aggregate_budget_test
  anonsync_sync_replica_capacity_backpressure_test
  PROPERTIES TIMEOUT 20)
# The generated network model and graph oracle deliberately retain their full
# differential corpora. ASan+UBSan can take materially longer than an ordinary
# Debug build in a contended CI/container environment; keep both stress corpora
# intact instead of weakening them to fit the generic focused-test timeout.
set_tests_properties(
  anonsync_sync_replica_network_model_test
  anonsync_sync_replica_hash_graph_projection_test
  PROPERTIES TIMEOUT 60)
add_test(NAME anonsync_sync_bounded_regular_file_test
  COMMAND anonsync_sync_bounded_regular_file_test)
set_tests_properties(anonsync_sync_bounded_regular_file_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sync_replica_folder_observer_test
  COMMAND anonsync_sync_replica_folder_observer_test)
set_tests_properties(anonsync_sync_replica_folder_observer_test
  PROPERTIES TIMEOUT 20 LABELS "product")
if(TARGET anonsync_sync_replica_folder_observer_race_test)
  add_test(NAME anonsync_sync_replica_folder_observer_race_test
    COMMAND anonsync_sync_replica_folder_observer_race_test)
  set_tests_properties(anonsync_sync_replica_folder_observer_race_test
    PROPERTIES TIMEOUT 20 LABELS "product")
endif()
add_test(NAME anonsync_sync_daemon_heartbeat_document_test
  COMMAND anonsync_sync_daemon_heartbeat_document_test)
set_tests_properties(anonsync_sync_daemon_heartbeat_document_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sync_daemon_heartbeat_publication_test
  COMMAND anonsync_sync_daemon_heartbeat_publication_test)
set_tests_properties(anonsync_sync_daemon_heartbeat_publication_test
  PROPERTIES TIMEOUT 20)
if(TARGET anonsync_sync_bounded_regular_file_syscall_test)
  add_test(NAME anonsync_sync_bounded_regular_file_syscall_test
    COMMAND anonsync_sync_bounded_regular_file_syscall_test)
  set_tests_properties(anonsync_sync_bounded_regular_file_syscall_test
    PROPERTIES TIMEOUT 20)
endif()
add_test(NAME anonsync_sync_atomic_file_publication_test
  COMMAND anonsync_sync_atomic_file_publication_test)
add_test(NAME anonsync_sync_posix_directory_resolution_test
  COMMAND anonsync_sync_posix_directory_resolution_test)
add_test(NAME anonsync_sync_atomic_file_publication_prepared_test
  COMMAND anonsync_sync_atomic_file_publication_prepared_test)
add_test(NAME anonsync_sync_atomic_file_publication_state_test
  COMMAND anonsync_sync_atomic_file_publication_state_test)
add_test(NAME anonsync_sync_atomic_file_publication_cutpoint_test
  COMMAND anonsync_sync_atomic_file_publication_cutpoint_test)
add_test(NAME anonsync_sync_atomic_file_reconciliation_test
  COMMAND anonsync_sync_atomic_file_reconciliation_test)
add_test(NAME anonsync_sync_replica_file_effect_sqlite_owner_test
  COMMAND anonsync_sync_replica_file_effect_sqlite_owner_test)
add_test(NAME anonsync_sync_replica_file_delivery_protocol_test
  COMMAND anonsync_sync_replica_file_delivery_protocol_test)
add_test(NAME anonsync_sync_replica_file_payload_verification_index_test
  COMMAND anonsync_sync_replica_file_payload_verification_index_test)
set_tests_properties(anonsync_sync_replica_file_payload_verification_index_test
  PROPERTIES LABELS "product" TIMEOUT 30)
add_test(NAME anonsync_resumable_sha256_test
  COMMAND anonsync_resumable_sha256_test)
set_tests_properties(anonsync_resumable_sha256_test
  PROPERTIES LABELS "product" TIMEOUT 30)
add_test(NAME anonsync_sync_replica_file_payload_scrub_state_test
  COMMAND anonsync_sync_replica_file_payload_scrub_state_test)
set_tests_properties(anonsync_sync_replica_file_payload_scrub_state_test
  PROPERTIES LABELS "product" TIMEOUT 30)
add_test(NAME anonsync_sync_replica_file_payload_terminal_verification_state_test
  COMMAND anonsync_sync_replica_file_payload_terminal_verification_state_test)
set_tests_properties(anonsync_sync_replica_file_payload_terminal_verification_state_test
  PROPERTIES LABELS "product" TIMEOUT 30)
add_test(NAME anonsync_sync_replica_file_payload_retention_mark_test
  COMMAND anonsync_sync_replica_file_payload_retention_mark_test)
set_tests_properties(anonsync_sync_replica_file_payload_retention_mark_test
  PROPERTIES LABELS "product" TIMEOUT 30)
add_test(NAME anonsync_sync_replica_source_manifest_checkpoint_test
  COMMAND anonsync_sync_replica_source_manifest_checkpoint_test)
set_tests_properties(anonsync_sync_replica_source_manifest_checkpoint_test
  PROPERTIES LABELS "product" TIMEOUT 30)
add_test(NAME anonsync_sync_replica_reconciliation_compact_manifest_test
  COMMAND anonsync_sync_replica_reconciliation_compact_manifest_test)
set_tests_properties(
  anonsync_sync_replica_reconciliation_compact_manifest_test
  PROPERTIES LABELS "product" TIMEOUT 30)
add_test(NAME anonsync_sync_replica_content_defined_chunker_test
  COMMAND anonsync_sync_replica_content_defined_chunker_test)
set_tests_properties(anonsync_sync_replica_content_defined_chunker_test
  PROPERTIES LABELS "product" TIMEOUT 30)
add_test(NAME anonsync_sync_replica_file_payload_store_test
  COMMAND anonsync_sync_replica_file_payload_store_test)
# The complete durable-store regression intentionally performs several full-byte
# proofs.  Keep the registry ceiling above its measured non-sanitized frontier.
set_tests_properties(anonsync_sync_replica_file_payload_store_test
  PROPERTIES TIMEOUT 90)
add_test(NAME anonsync_sync_replica_deployment_manifest_test
  COMMAND anonsync_sync_replica_deployment_manifest_test)
set_tests_properties(anonsync_sync_replica_deployment_manifest_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sync_replica_bootstrap_record_test
  COMMAND anonsync_sync_replica_bootstrap_record_test)
set_tests_properties(anonsync_sync_replica_bootstrap_record_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sync_replica_deployment_binding_test
  COMMAND anonsync_sync_replica_deployment_binding_test)
set_tests_properties(anonsync_sync_replica_deployment_binding_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sync_replica_file_delivery_service_test
  COMMAND anonsync_sync_replica_file_delivery_service_test)
set_tests_properties(anonsync_sync_replica_file_delivery_service_test
  PROPERTIES LABELS "product")
if(TARGET anonsync_sync_atomic_file_publication_unlink_authority_test)
  add_test(NAME anonsync_sync_atomic_file_publication_unlink_authority_test
    COMMAND anonsync_sync_atomic_file_publication_unlink_authority_test)
  set_tests_properties(
    anonsync_sync_atomic_file_publication_unlink_authority_test
    PROPERTIES TIMEOUT 30)
endif()
add_test(NAME anonsync_sync_checkpoint_scheduler_policy_test
  COMMAND anonsync_sync_checkpoint_scheduler_policy_test)
add_test(NAME anonsync_sync_checkpoint_owner_fence_policy_test
  COMMAND anonsync_sync_checkpoint_owner_fence_policy_test)
add_test(NAME anonsync_sync_checkpoint_owner_schema_test
  COMMAND anonsync_sync_checkpoint_owner_schema_test)
add_test(NAME anonsync_sync_checkpoint_owner_fence_sqlite_test
  COMMAND anonsync_sync_checkpoint_owner_fence_sqlite_test)
add_test(NAME anonsync_core_sync_domain_model_selftest COMMAND anonsync_core --selftest-sync-domain-model)
add_test(NAME anonsync_core_sync_peer_ingress_lifecycle_selftest
  COMMAND anonsync_core --selftest-sync-peer-ingress-lifecycle)
add_test(NAME anonsync_core_sync_peer_ingress_wire_codec_test COMMAND anonsync_sync_peer_ingress_wire_test)
add_test(NAME anonsync_peer_ingress_wire_adversarial_test
  COMMAND anonsync_peer_ingress_wire_adversarial_test)
add_test(NAME anonsync_sync_peer_wire_compatibility_test
  COMMAND anonsync_sync_peer_wire_compatibility_test)
add_test(NAME anonsync_sqlite_runtime_payload_store_test
  COMMAND anonsync_sqlite_runtime_payload_store_test)
add_test(NAME anonsync_canonical_projection_verifier_test
  COMMAND anonsync_canonical_projection_verifier_test)
add_test(NAME anonsync_local_jsonl_replay_publication_test
  COMMAND anonsync_local_jsonl_replay_publication_test)
add_test(NAME anonsync_local_jsonl_replay_directory_authority_test
  COMMAND anonsync_local_jsonl_replay_directory_authority_test)
set_tests_properties(anonsync_local_jsonl_replay_directory_authority_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_local_jsonl_replay_namespace_test
  COMMAND anonsync_local_jsonl_replay_namespace_test)
set_tests_properties(anonsync_local_jsonl_replay_namespace_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_local_jsonl_replay_backend_namespace_test
  COMMAND anonsync_local_jsonl_replay_backend_namespace_test)
set_tests_properties(anonsync_local_jsonl_replay_backend_namespace_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_local_jsonl_replay_crash_state_machine_test
  COMMAND anonsync_local_jsonl_replay_crash_state_machine_test)
set_tests_properties(anonsync_local_jsonl_replay_crash_state_machine_test
  PROPERTIES TIMEOUT 60)
add_test(NAME anonsync_effect_transition_intent_publication_test
  COMMAND anonsync_effect_transition_intent_publication_test)
add_test(NAME anonsync_effect_transition_record_material_test
  COMMAND anonsync_effect_transition_record_material_test)
add_test(NAME anonsync_sqlite_snapshot_manifest_publication_test
  COMMAND anonsync_sqlite_snapshot_manifest_publication_test)
add_test(NAME anonsync_sqlite_projection_decoder_test
  COMMAND anonsync_sqlite_projection_decoder_test)
add_test(NAME anonsync_peer_ingress_projection_integrity_test
  COMMAND anonsync_peer_ingress_projection_integrity_test)
add_test(NAME anonsync_peer_ingress_retention_integrity_test
  COMMAND anonsync_peer_ingress_retention_integrity_test)
add_test(NAME anonsync_peer_ingress_schema_attestation_test
  COMMAND anonsync_peer_ingress_schema_attestation_test)
set_tests_properties(
  anonsync_sync_atomic_file_publication_state_test
  PROPERTIES TIMEOUT 90)
set_tests_properties(
  anonsync_sync_atomic_file_publication_test
  anonsync_sync_atomic_file_publication_prepared_test
  anonsync_peer_ingress_schema_attestation_test
  PROPERTIES TIMEOUT 60)
set_tests_properties(
  anonsync_sync_atomic_file_publication_cutpoint_test
  anonsync_sqlite_runtime_payload_store_test
  PROPERTIES TIMEOUT 120)
add_test(NAME anonsync_peer_ingress_connection_profile_test
  COMMAND anonsync_peer_ingress_connection_profile_test)
if(ANONSYNC_USE_BUNDLED_SQLITE)
  add_test(NAME anonsync_bundled_sqlite_native_profile_audit
    COMMAND "${CMAKE_COMMAND}"
      "-DANONSYNC_SOURCE_ROOT:PATH=${CMAKE_CURRENT_SOURCE_DIR}"
      -P "${CMAKE_CURRENT_SOURCE_DIR}/cmake/AnonSyncVerifyBundledSqliteAtBuild.cmake")
  set_tests_properties(anonsync_bundled_sqlite_native_profile_audit
    PROPERTIES TIMEOUT 20)
endif()
find_package(Python3 COMPONENTS Interpreter QUIET)
if(Python3_Interpreter_FOUND)
  add_test(NAME anonsync_active_implementation_projection_policy_test
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_active_implementation_projection.py)
  set_tests_properties(anonsync_active_implementation_projection_policy_test
    PROPERTIES TIMEOUT 20)
  if(ANONSYNC_USE_BUNDLED_SQLITE)
    add_test(NAME anonsync_bundled_sqlite_profile_audit
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_bundled_sqlite_profile.py
        --root ${CMAKE_CURRENT_SOURCE_DIR}
        --compact)
    set_tests_properties(anonsync_bundled_sqlite_profile_audit
      PROPERTIES TIMEOUT 20)
    add_test(NAME anonsync_bundled_sqlite_profile_adversarial_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_verify_bundled_sqlite_profile.py
        --root ${CMAKE_CURRENT_SOURCE_DIR})
    set_tests_properties(anonsync_bundled_sqlite_profile_adversarial_test
      PROPERTIES TIMEOUT 60)
    add_test(NAME anonsync_bundled_sqlite_native_build_gate_adversarial_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_bundled_sqlite_native_build_gate.py
        --root ${CMAKE_CURRENT_SOURCE_DIR}
        --cmake ${CMAKE_COMMAND})
    set_tests_properties(
      anonsync_bundled_sqlite_native_build_gate_adversarial_test
      PROPERTIES TIMEOUT 90)
  endif()
  if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    add_test(NAME anonsync_replica_cli_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_replica_cli.py
        --replica $<TARGET_FILE:anonsync_replica>)
    set_tests_properties(anonsync_replica_cli_process_test
      PROPERTIES TIMEOUT 60)
    add_test(NAME anonsync_folder_cli_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_folder_cli.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_folder_cli_process_test
      PROPERTIES TIMEOUT 60)
    add_test(NAME anonsync_replica_reconciliation_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_replica_reconciliation_process.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>)
    set_tests_properties(anonsync_replica_reconciliation_process_test
      PROPERTIES TIMEOUT 240)
    add_test(NAME anonsync_sync_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_sync_process.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_process_test
      PROPERTIES TIMEOUT 60)
    add_test(NAME anonsync_sync_process_resources_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_process_resources.py
        --sync $<TARGET_FILE:anonsync_sync>
        --fixture $<TARGET_FILE:anonsync_sync_linux_process_resources_fixture>)
    set_tests_properties(anonsync_sync_process_resources_process_test
      PROPERTIES TIMEOUT 30 LABELS "product")
    add_test(NAME anonsync_sync_sparse_multiterabyte_selective_resources_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_sparse_multiterabyte_selective_resources.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(
      anonsync_sync_sparse_multiterabyte_selective_resources_process_test
      PROPERTIES TIMEOUT 120 LABELS "product")
    add_test(NAME anonsync_sync_share_create_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_share_create.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_share_create_process_test
      PROPERTIES TIMEOUT 90)
    add_test(NAME anonsync_sync_service_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_service_process.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_service_process_test
      PROPERTIES TIMEOUT 90)
    add_test(NAME anonsync_sync_database_recovery_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_database_recovery.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_database_recovery_process_test
      PROPERTIES TIMEOUT 90)
    add_test(NAME anonsync_sync_database_role_backup_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_database_role_backup.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_database_role_backup_process_test
      PROPERTIES TIMEOUT 90)
    add_test(NAME anonsync_sync_service_configuration_status_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_service_configuration_status.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_service_configuration_status_process_test
      PROPERTIES TIMEOUT 60)
    add_test(NAME anonsync_sync_service_terminal_verification_scheduler_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_service_terminal_verification_scheduler.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>
        --fixture $<TARGET_FILE:anonsync_sync_replica_terminal_verification_fixture>)
    set_tests_properties(
      anonsync_sync_service_terminal_verification_scheduler_process_test
      PROPERTIES TIMEOUT 60)
    add_test(NAME anonsync_sync_service_source_manifest_scheduler_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_service_source_manifest_scheduler.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(
      anonsync_sync_service_source_manifest_scheduler_process_test
      PROPERTIES TIMEOUT 120)
    add_test(NAME anonsync_sync_provisioning_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_provisioning.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_provisioning_process_test
      PROPERTIES TIMEOUT 90)
    add_test(NAME anonsync_sync_linking_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_linking.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_linking_process_test
      PROPERTIES TIMEOUT 90)
    add_test(NAME anonsync_sync_share_join_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_share_join.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_share_join_process_test
      PROPERTIES TIMEOUT 90)
    add_test(NAME anonsync_sync_service_folder_wake_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_service_folder_wake.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_service_folder_wake_process_test
      PROPERTIES TIMEOUT 60)
    add_test(NAME anonsync_sync_service_i2p_ingress_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_service_i2p_ingress.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_service_i2p_ingress_process_test
      PROPERTIES TIMEOUT 120)
    add_test(NAME anonsync_runtime_install_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_runtime_install.py
        --cmake ${CMAKE_COMMAND}
        --build-dir ${CMAKE_BINARY_DIR}
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>
        --install-prefix ${CMAKE_INSTALL_PREFIX}
        --bindir ${CMAKE_INSTALL_BINDIR}
        --unit-install-dir ${ANONSYNC_SYSTEMD_USER_UNIT_INSTALL_DIR}
        --configured-bindir ${CMAKE_INSTALL_FULL_BINDIR}
        --stop-timeout-seconds
          ${ANONSYNC_INSTALLED_SERVICE_STOP_TIMEOUT_SECONDS})
    set_tests_properties(anonsync_runtime_install_process_test
      PROPERTIES TIMEOUT 30)
    add_test(NAME anonsync_replica_anonymous_routes_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_replica_anonymous_routes.py
        --replica $<TARGET_FILE:anonsync_replica>)
    set_tests_properties(anonsync_replica_anonymous_routes_process_test
      PROPERTIES TIMEOUT 90)
    add_test(NAME anonsync_sync_anonymous_routes_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_sync_anonymous_routes.py
        --replica $<TARGET_FILE:anonsync_replica>
        --folder $<TARGET_FILE:anonsync_folder>
        --sync $<TARGET_FILE:anonsync_sync>)
    set_tests_properties(anonsync_sync_anonymous_routes_process_test
      PROPERTIES TIMEOUT 90)
    add_test(NAME anonsync_replica_bootstrap_resume_process_test
      COMMAND ${Python3_EXECUTABLE} -B -S
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_anonsync_replica_bootstrap_resume.py
        --replica $<TARGET_FILE:anonsync_replica>)
    set_tests_properties(anonsync_replica_bootstrap_resume_process_test
      PROPERTIES TIMEOUT 60)
    set_tests_properties(
      anonsync_replica_cli_process_test
      anonsync_folder_cli_process_test
      anonsync_replica_reconciliation_process_test
      anonsync_sync_process_test
      anonsync_sync_share_create_process_test
      anonsync_sync_service_process_test
      anonsync_sync_database_recovery_process_test
      anonsync_sync_database_role_backup_process_test
      anonsync_sync_service_configuration_status_process_test
      anonsync_sync_service_terminal_verification_scheduler_process_test
      anonsync_sync_service_source_manifest_scheduler_process_test
      anonsync_sync_provisioning_process_test
      anonsync_sync_linking_process_test
      anonsync_sync_share_join_process_test
      anonsync_sync_service_folder_wake_process_test
      anonsync_sync_service_i2p_ingress_process_test
      anonsync_runtime_install_process_test
      anonsync_replica_anonymous_routes_process_test
      anonsync_sync_anonymous_routes_process_test
      anonsync_replica_bootstrap_resume_process_test
      PROPERTIES LABELS "product")
  endif()
  add_test(NAME anonsync_replica_database_open_policy_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_anonsync_replica_database_open_policy.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_replica_database_open_policy_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_database_backup_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_database_backup.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_database_backup_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_database_role_backup_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_database_role_backup.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_database_role_backup_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_content_defined_delta_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_content_defined_delta.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_content_defined_delta_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_source_chunk_index_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_source_chunk_index.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_source_chunk_index_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_multi_range_window_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_multi_range_window.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_multi_range_window_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_response_frame_memory_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_response_frame_memory.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_response_frame_memory_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_response_memory_shape_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_response_memory_shape.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_response_memory_shape_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_direct_source_frame_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_direct_source_frame.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_direct_source_frame_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_bounded_history_access_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_bounded_history_access.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_bounded_history_access_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_cross_file_delta_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_cross_file_delta.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_cross_file_delta_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_bounded_cross_file_projection_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_bounded_cross_file_projection.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_bounded_cross_file_projection_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_bounded_local_reuse_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_bounded_local_reuse.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_bounded_local_reuse_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_manifest_reference_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_manifest_reference.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_manifest_reference_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_bounded_predecessor_projection_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_bounded_predecessor_projection.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_bounded_predecessor_projection_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_terminal_verification_continuation_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_terminal_verification_continuation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_terminal_verification_continuation_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_targeted_terminal_local_pulse_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_targeted_terminal_local_pulse.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_targeted_terminal_local_pulse_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_receiver_local_terminal_scheduler_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_receiver_local_terminal_scheduler.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_receiver_local_terminal_scheduler_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_bounded_source_manifest_projection_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_bounded_source_manifest_projection.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_bounded_source_manifest_projection_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_source_local_manifest_scheduler_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_source_local_manifest_scheduler.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_source_local_manifest_scheduler_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_durable_source_manifest_checkpoint_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_durable_source_manifest_checkpoint.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_durable_source_manifest_checkpoint_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_source_manifest_checkpoint_memory_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_source_manifest_checkpoint_memory.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_source_manifest_checkpoint_memory_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_compact_source_manifest_cache_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_compact_source_manifest_cache.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_compact_source_manifest_cache_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_fixed_binary_manifest_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_fixed_binary_manifest.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_fixed_binary_manifest_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_borrowed_manifest_frame_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_borrowed_manifest_frame.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_borrowed_manifest_frame_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_active_source_manifest_memory_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_active_source_manifest_memory.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_active_source_manifest_memory_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_service_startup_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_service_startup.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_service_startup_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_sparse_multiterabyte_selective_resources_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_sparse_multiterabyte_selective_resources.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_sparse_multiterabyte_selective_resources_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_identity_preserving_rename_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_identity_preserving_rename.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_identity_preserving_rename_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_bounded_rename_planning_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_bounded_rename_planning.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_bounded_rename_planning_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_linux_process_resources_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_linux_process_resources.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_linux_process_resources_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_terminal_manifest_cache_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_terminal_manifest_cache.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_terminal_manifest_cache_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_targeted_source_access_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_targeted_source_access.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_targeted_source_access_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_selective_sync_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_selective_sync.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_selective_sync_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_targeted_catalog_cutpoint_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_targeted_catalog_cutpoint.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_targeted_catalog_cutpoint_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_targeted_path_cutpoint_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_targeted_path_cutpoint.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_targeted_path_cutpoint_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_targeted_local_publication_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_targeted_local_publication.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_targeted_local_publication_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_database_replacement_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_database_replacement.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_database_replacement_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_replica_bootstrap_authority_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_anonsync_replica_bootstrap_authority.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_replica_bootstrap_authority_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_replica_deployment_binding_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_anonsync_replica_deployment_binding.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_replica_deployment_binding_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_release_package_path_policy_test
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_release_package_path_policy.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_release_package_path_policy_test
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_manifest_validation_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_manifest_validation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_manifest_validation_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_manifest_stream_decoder_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_manifest_stream_decoder.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_manifest_stream_decoder_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_sqlite_manifest_chunk_subset_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_sqlite_manifest_chunk_subset.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_sqlite_manifest_chunk_subset_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_sqlite_sidecar_snapshot_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_sqlite_sidecar_snapshot.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_sqlite_sidecar_snapshot_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_manifest_identity_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_manifest_identity.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_manifest_identity_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_conflict_convergence_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_conflict_convergence.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_conflict_convergence_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_aggregate_budget_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_aggregate_budget.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_aggregate_budget_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_capacity_backpressure_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_capacity_backpressure.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(
    anonsync_sync_replica_capacity_backpressure_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_outbox_lease_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_outbox_lease.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_outbox_lease_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_outbox_clock_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_outbox_clock.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_outbox_clock_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_sqlite_owner_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_sqlite_owner.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_sqlite_owner_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_delivery_channel_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_delivery_channel.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_delivery_channel_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_replica_file_delivery_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_replica_file_delivery.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_replica_file_delivery_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_file_payload_snapshot_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_file_payload_snapshot.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_file_payload_snapshot_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_file_payload_store_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_file_payload_store.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_file_payload_store_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_file_tls_dispatch_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_file_tls_dispatch.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_file_tls_dispatch_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_file_tls_exchange_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_file_tls_exchange.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_file_tls_exchange_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_file_tls_receiver_session_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_file_tls_receiver_session.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_file_tls_receiver_session_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_tls_receive_continuation_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_tls_receive_continuation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_tls_receive_continuation_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_socket_readiness_identity_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_socket_readiness_identity.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_socket_readiness_identity_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_file_tls_server_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_file_tls_server.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_file_tls_server_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_tls_membership_snapshot_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_tls_membership_snapshot.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_tls_membership_snapshot_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_tls_membership_sqlite_owner_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_tls_membership_sqlite_owner.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_tls_membership_sqlite_owner_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_tls_membership_anchor_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_tls_membership_anchor.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_tls_membership_anchor_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_authority_callback_boundaries_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_authority_callback_boundaries.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_authority_callback_boundaries_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_tls_transport_anchor_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_tls_transport_anchor.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_tls_transport_anchor_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_tls_io_policy_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_tls_io_policy.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_tls_io_policy_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_tls_write_continuation_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_tls_write_continuation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_tls_write_continuation_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_tls_poll_owner_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_tls_poll_owner.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_tls_poll_owner_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_release_path_policy_test
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_verify_release_package_policy.py)
  set_tests_properties(anonsync_release_path_policy_test
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_file_effect_path_capability_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_file_effect_path_capability.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_file_effect_path_capability_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_file_effect_capacity_accounting_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_file_effect_capacity_accounting.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_file_effect_capacity_accounting_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_outbox_dispatch_guard_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_outbox_dispatch_guard.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_outbox_dispatch_guard_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_effect_root_authority_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_effect_root_authority.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_effect_root_authority_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_mount_boundary_authority_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_mount_boundary_authority.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_mount_boundary_authority_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_daemon_heartbeat_document_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_daemon_heartbeat_document.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_daemon_heartbeat_document_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_process_identity_observation_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_process_identity_observation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_process_identity_observation_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_bounded_regular_file_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_bounded_regular_file.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sync_bounded_regular_file_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_peer_ingress_connection_profile_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_peer_ingress_connection_profile.py
      ${CMAKE_CURRENT_SOURCE_DIR}
      src/sync_domain.cpp)
  add_test(NAME anonsync_sqlite_scalar_extraction_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_scalar_extraction.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_ingress_sender_replay_integrity_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_ingress_sender_replay_integrity.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_replay_ledger_schema_contract_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_replay_ledger_schema_contract.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_snapshot_seal_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_snapshot_seal.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_snapshot_geometry_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_snapshot_geometry.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_live_backup_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_live_backup.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_verification_budget_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_verification_budget.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_busy_handler_owner_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_busy_handler_owner.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sqlite_busy_handler_owner_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sqlite_authorizer_owner_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_authorizer_owner.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_sqlite_authorizer_owner_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sync_process_incarnation_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_process_incarnation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sync_thread_incarnation_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_thread_incarnation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_process_authority_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_process_authority.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_mutex_capability_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_mutex_capability.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_owner_generation_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_owner_generation.py)
  add_test(NAME anonsync_sqlite_transaction_stack_authority_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_transaction_stack_authority.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_transaction_exception_composition_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_transaction_exception_composition.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_transaction_allocator_fault_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_transaction_allocator_fault.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_source_first_move_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_source_first_move.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_peer_ingress_schema_owner_generation_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_peer_ingress_schema_owner_generation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_active_persistence_boundary_inventory_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/rev0763_persistence_boundary_audit.py
      ${CMAKE_CURRENT_SOURCE_DIR}
      --enforce)
  add_test(NAME anonsync_core_selftest_registration_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_selftest_registration.py
      --root ${CMAKE_CURRENT_SOURCE_DIR}
      --binary $<TARGET_FILE:anonsync_core>)
  add_test(NAME anonsync_runtime_selftest_separation_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_runtime_selftest_separation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_replay_ledger_selftest_separation_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_replay_ledger_selftest_separation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sync_domain_selftest_separation_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_domain_selftest_separation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sync_checkpoint_scheduler_separation_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_checkpoint_scheduler_separation.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sync_checkpoint_owner_fence_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_checkpoint_owner_fence.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sync_atomic_file_publication_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sync_atomic_file_publication.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_restore_publication_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_restore_publication.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_backup_publication_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_backup_publication.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_inherited_test_process_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_inherited_test_process.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_inherited_test_process_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_self_exec_test_process_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_self_exec_test_process.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_self_exec_test_process_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_test_process_topology_owner_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_test_process_topology_owner.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_test_process_topology_owner_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_raw_fork_boundary_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_raw_fork_boundaries.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_raw_fork_boundary_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sqlite_replay_ledger_reset_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_replay_ledger_reset.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_replay_ledger_reset_crash_frontier_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_replay_ledger_reset_crash_frontier.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_replay_ledger_reset_receipt_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_replay_ledger_reset_receipt.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_replay_ledger_reset_receipt_protocol_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_replay_ledger_reset_receipt_protocol.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_replay_ledger_load_authority_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_replay_ledger_load_authority.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_local_jsonl_replay_crash_protocol_source_audit
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_local_jsonl_replay_crash_protocol.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  set_tests_properties(anonsync_local_jsonl_replay_crash_protocol_source_audit
    PROPERTIES TIMEOUT 20)
  add_test(NAME anonsync_sqlite_replay_ledger_reset_cli_test
    COMMAND ${Python3_EXECUTABLE} -B -S
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/test_sqlite_replay_ledger_reset_cli.py
      --core $<TARGET_FILE:anonsync_core>
      --fixture $<TARGET_FILE:anonsync_sqlite_replay_ledger_reset_test>)
  set_tests_properties(anonsync_sqlite_replay_ledger_reset_cli_test
    PROPERTIES TIMEOUT 60)
endif()
set_tests_properties(
  anonsync_core_sync_domain_model_selftest
  anonsync_core_sync_peer_ingress_lifecycle_selftest
  PROPERTIES RESOURCE_LOCK anonsync_peer_ingress_lifecycle_fixture)
set_tests_properties(anonsync_core_sync_domain_model_selftest
  PROPERTIES RUN_SERIAL TRUE)
add_test(NAME anonsync_core_json_parser_boundary_selftest COMMAND anonsync_core --selftest-json-parser)
add_test(NAME anonsync_core_sqlite_wal_verified_claims_selftest COMMAND anonsync_core --selftest-ledger-sqlite-wal)
add_test(NAME anonsync_sqlite_exact_value_test COMMAND anonsync_sqlite_exact_value_test)
add_test(NAME anonsync_process_identity_observation_test
  COMMAND anonsync_process_identity_observation_test)
set_tests_properties(anonsync_process_identity_observation_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_system_epoch_identity_test
  COMMAND anonsync_system_epoch_identity_test)
set_tests_properties(anonsync_system_epoch_identity_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_process_incarnation_test
  COMMAND anonsync_process_incarnation_test)
add_test(NAME anonsync_thread_incarnation_test
  COMMAND anonsync_thread_incarnation_test)
set_tests_properties(
  anonsync_process_incarnation_test
  anonsync_thread_incarnation_test
  PROPERTIES TIMEOUT 20)
if(TARGET anonsync_test_process_topology_owner_test)
  add_test(NAME anonsync_test_process_topology_owner_test
    COMMAND anonsync_test_process_topology_owner_test)
  set_tests_properties(anonsync_test_process_topology_owner_test
    PROPERTIES TIMEOUT 20)
endif()
if(TARGET anonsync_inherited_test_process_test)
  add_test(NAME anonsync_inherited_test_process_test
    COMMAND anonsync_inherited_test_process_test)
  set_tests_properties(anonsync_inherited_test_process_test
    PROPERTIES TIMEOUT 20)
endif()
if(TARGET anonsync_self_exec_test_process_test)
  add_test(NAME anonsync_self_exec_test_process_test
    COMMAND anonsync_self_exec_test_process_test)
  set_tests_properties(anonsync_self_exec_test_process_test
    PROPERTIES TIMEOUT 20)
endif()
add_test(NAME anonsync_ingress_sender_replay_record_test
  COMMAND anonsync_ingress_sender_replay_record_test)
add_test(NAME anonsync_sqlite_replay_ledger_schema_contract_test
  COMMAND anonsync_sqlite_replay_ledger_schema_contract_test)
add_test(NAME anonsync_sqlite_replay_ledger_reset_test
  COMMAND anonsync_sqlite_replay_ledger_reset_test)
set_tests_properties(anonsync_sqlite_replay_ledger_reset_test
  PROPERTIES TIMEOUT 60)
if(TARGET anonsync_sqlite_replay_ledger_reset_crash_frontier_test)
  add_test(NAME anonsync_sqlite_replay_ledger_reset_crash_frontier_test
    COMMAND anonsync_sqlite_replay_ledger_reset_crash_frontier_test)
  set_tests_properties(
    anonsync_sqlite_replay_ledger_reset_crash_frontier_test
    PROPERTIES TIMEOUT 120)
endif()
add_test(NAME anonsync_sqlite_replay_ledger_reset_documents_test
  COMMAND anonsync_sqlite_replay_ledger_reset_documents_test)
set_tests_properties(anonsync_sqlite_replay_ledger_reset_documents_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sqlite_snapshot_seal_test
  COMMAND anonsync_sqlite_snapshot_seal_test)
add_test(NAME anonsync_sqlite_snapshot_geometry_test
  COMMAND anonsync_sqlite_snapshot_geometry_test)
add_test(NAME anonsync_sqlite_live_backup_test
  COMMAND anonsync_sqlite_live_backup_test)
set_tests_properties(anonsync_sqlite_live_backup_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sqlite_verification_budget_test
  COMMAND anonsync_sqlite_verification_budget_test)
set_tests_properties(anonsync_sqlite_verification_budget_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sqlite_busy_handler_owner_test
  COMMAND anonsync_sqlite_busy_handler_owner_test)
set_tests_properties(anonsync_sqlite_busy_handler_owner_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sqlite_owned_authorizer_policy_test
  COMMAND anonsync_sqlite_owned_authorizer_policy_test)
set_tests_properties(anonsync_sqlite_owned_authorizer_policy_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sqlite_authorizer_owner_test
  COMMAND anonsync_sqlite_authorizer_owner_test)
set_tests_properties(anonsync_sqlite_authorizer_owner_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sqlite_persistence_process_authority_fork_test
  COMMAND anonsync_sqlite_persistence_process_authority_fork_test)
set_tests_properties(anonsync_sqlite_persistence_process_authority_fork_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sqlite_snapshot_geometry_binding_test
  COMMAND anonsync_sqlite_snapshot_geometry_binding_test)
set_tests_properties(anonsync_sqlite_snapshot_geometry_binding_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sqlite_snapshot_sidecar_binding_test
  COMMAND anonsync_sqlite_snapshot_sidecar_binding_test)
set_tests_properties(anonsync_sqlite_snapshot_sidecar_binding_test
  PROPERTIES TIMEOUT 30)
set_tests_properties(
  anonsync_sqlite_snapshot_seal_test
  anonsync_sqlite_snapshot_geometry_binding_test
  anonsync_sqlite_snapshot_sidecar_binding_test
  PROPERTIES RESOURCE_LOCK anonsync_sqlite_snapshot_staging_fixture)
add_test(NAME anonsync_sqlite_replay_ledger_schema_integrity_test
  COMMAND anonsync_sqlite_replay_ledger_schema_integrity_test)
set_tests_properties(anonsync_sqlite_replay_ledger_schema_integrity_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sqlite_restore_namespace_authority_test
  COMMAND anonsync_sqlite_restore_namespace_authority_test)
set_tests_properties(anonsync_sqlite_restore_namespace_authority_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sqlite_backup_namespace_authority_test
  COMMAND anonsync_sqlite_backup_namespace_authority_test)
set_tests_properties(anonsync_sqlite_backup_namespace_authority_test
  PROPERTIES TIMEOUT 90)
add_test(NAME anonsync_sqlite_ingress_sender_replay_integrity_test
  COMMAND anonsync_sqlite_ingress_sender_replay_integrity_test)
set_tests_properties(anonsync_sqlite_ingress_sender_replay_integrity_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sqlite_runtime_policy_test COMMAND anonsync_sqlite_runtime_policy_test)
add_test(NAME anonsync_sqlite_support_test COMMAND anonsync_sqlite_support_test)
add_test(NAME anonsync_sqlite_connection_authority_test
  COMMAND anonsync_sqlite_connection_authority_test)
set_tests_properties(anonsync_sqlite_connection_authority_test
  PROPERTIES TIMEOUT 15)
add_test(NAME anonsync_sqlite_transaction_exception_composition_test
  COMMAND anonsync_sqlite_transaction_exception_composition_test)
set_tests_properties(anonsync_sqlite_transaction_exception_composition_test
  PROPERTIES TIMEOUT 15)
if(TARGET anonsync_sqlite_transaction_allocator_fault_test)
  add_test(NAME anonsync_sqlite_transaction_allocator_fault_test
    COMMAND anonsync_sqlite_transaction_allocator_fault_test)
  set_tests_properties(anonsync_sqlite_transaction_allocator_fault_test
    PROPERTIES TIMEOUT 120)
endif()
add_test(NAME anonsync_sqlite_process_authority_fork_test
  COMMAND anonsync_sqlite_process_authority_fork_test)
set_tests_properties(anonsync_sqlite_process_authority_fork_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sqlite_owner_generation_borrow_test
  COMMAND anonsync_sqlite_owner_generation_borrow_test)
set_tests_properties(anonsync_sqlite_owner_generation_borrow_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sqlite_source_first_move_test
  COMMAND anonsync_sqlite_source_first_move_test)
set_tests_properties(anonsync_sqlite_source_first_move_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_core_sqlite_runtime_profile_selftest COMMAND anonsync_core --selftest-ledger-host-capability-probe)
add_test(NAME anonsync_core_event_identity_replay_selftest COMMAND anonsync_core --selftest-ledger-event-identity-replay)
add_test(NAME anonsync_core_effect_idempotency_selftest COMMAND anonsync_core --selftest-ledger-effect-idempotency)
add_test(NAME anonsync_core_sqlite_effect_transition_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-transition)
add_test(NAME anonsync_core_sqlite_effect_pending_recovery_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-pending-recovery)
add_test(NAME anonsync_core_sqlite_effect_signed_transition_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-signed-transition)
add_test(NAME anonsync_core_sqlite_effect_outbox_claim_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-outbox-claim)
add_test(NAME anonsync_core_sqlite_effect_relay_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-relay)
add_test(NAME anonsync_core_sqlite_effect_relay_configured_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-relay-configured)
add_test(NAME anonsync_core_sqlite_effect_relay_handle_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-relay-handle)
add_test(NAME anonsync_core_backend_capability_exact_version_selftest COMMAND anonsync_core --selftest-ledger-backend-capabilities)
add_test(NAME anonsync_core_jwt_codec_fuzz_selftest COMMAND anonsync_core --selftest-fuzz-jwt)
add_test(NAME anonsync_core_route_event_ledger_fuzz_selftest COMMAND anonsync_core --selftest-fuzz-route-event-ledger)
add_test(NAME anonsync_core_sqlite_snapshot_corpus_selftest COMMAND anonsync_core --selftest-ledger-sqlite-snapshot-corpus)
add_test(NAME anonsync_core_sqlite_restore_corpus_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-corpus)
add_test(NAME anonsync_core_snapshot_manifest_verifier_selftest COMMAND anonsync_core --selftest-ledger-snapshot-manifest-verifier)
add_test(NAME anonsync_core_sqlite_restore_rollback_guard_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-rollback-guard)
add_test(NAME anonsync_core_sqlite_restore_atomicity_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-atomicity)
add_test(NAME anonsync_core_sqlite_restore_locking_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-locking)
add_test(NAME anonsync_core_sqlite_restore_manifest_binding_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-manifest-binding)
add_test(NAME anonsync_core_sqlite_restore_write_gate_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-write-gate)
add_test(NAME anonsync_core_sqlite_restore_prefix_continuity_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-prefix-continuity)
add_test(NAME anonsync_core_sqlite_readonly_snapshot_verifier_selftest COMMAND anonsync_core --selftest-ledger-sqlite-readonly-snapshot-verifier)

# Every public selftest advertised by `anonsync_core --help` is a release-gate
# obligation.  Keep these older but still supported adversarial and durability
# paths visible to CTest rather than allowing the public CLI to drift beyond the
# executable proof surface.
add_test(NAME anonsync_core_boundary_fuzz_selftest COMMAND anonsync_core --selftest-boundary-fuzz)
add_test(NAME anonsync_core_json_codec_fuzz_selftest COMMAND anonsync_core --selftest-fuzz-json)
add_test(NAME anonsync_core_ledger_durable_io_selftest COMMAND anonsync_core --selftest-ledger-durable-io)
add_test(NAME anonsync_core_ledger_backend_adapter_selftest COMMAND anonsync_core --selftest-ledger-backend-adapter)
add_test(NAME anonsync_core_ledger_crash_injection_selftest COMMAND anonsync_core --selftest-ledger-crash-injection)
add_test(NAME anonsync_core_ledger_batch_transaction_selftest COMMAND anonsync_core --selftest-ledger-batch-transaction)
add_test(NAME anonsync_core_ledger_journal_hardening_selftest COMMAND anonsync_core --selftest-ledger-journal-hardening)
add_test(NAME anonsync_core_ledger_backend_interface_selftest COMMAND anonsync_core --selftest-ledger-backend-interface)
add_test(NAME anonsync_core_sqlite_hardening_selftest COMMAND anonsync_core --selftest-ledger-sqlite-hardening)
add_test(NAME anonsync_core_sqlite_crash_corpus_selftest COMMAND anonsync_core --selftest-ledger-sqlite-crash-corpus)
add_test(NAME anonsync_core_sqlite_backup_restore_selftest COMMAND anonsync_core --selftest-ledger-sqlite-backup-restore)
set_tests_properties(
  anonsync_core_boundary_fuzz_selftest
  anonsync_core_json_codec_fuzz_selftest
  anonsync_core_ledger_durable_io_selftest
  anonsync_core_ledger_backend_adapter_selftest
  anonsync_core_ledger_crash_injection_selftest
  anonsync_core_ledger_batch_transaction_selftest
  anonsync_core_ledger_journal_hardening_selftest
  anonsync_core_ledger_backend_interface_selftest
  anonsync_core_sqlite_hardening_selftest
  anonsync_core_sqlite_crash_corpus_selftest
  anonsync_core_sqlite_backup_restore_selftest
  PROPERTIES TIMEOUT 60)
set(ANONSYNC_REPO_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../..")
if(EXISTS "${ANONSYNC_REPO_ROOT}/fixtures/rev0618/cpp-slim-gateway-context.json")
  add_test(NAME anonsync_core_rev0648_slim_sqlite_stream
    COMMAND anonsync_core
      --controls "${ANONSYNC_REPO_ROOT}/fixtures/rev0618/cpp-slim-gateway-context.json"
      --cases-jsonl "${ANONSYNC_REPO_ROOT}/fixtures/rev0618/cpp-slim-gateway-cases.jsonl"
      --contracts "${ANONSYNC_REPO_ROOT}/gateway/rev0618-cpp-slim-normalization-contract-table.json"
      --ledger "${CMAKE_BINARY_DIR}/rev0648-ctest-ledger.sqlite"
      --ledger-backend sqlite-wal
      --ledger-backend-capabilities "${ANONSYNC_REPO_ROOT}/gateway/rev0648-cpp-ledger-backend-capabilities.json"
      --ledger-reset
      --ledger-commit-mode batch
      --report "${CMAKE_BINARY_DIR}/rev0648-ctest-report.json")
endif()

# One command for the edit/compile/test loop on the replacement-product spine.
# The dependency target compiles only shipping-path executables and their
# focused tests; CTest then runs the exact product label in bounded parallelism.
# This intentionally does not pull the inherited all-target assurance graph
# into every ordinary C++ iteration.
add_custom_target(anonsync_product_check
  COMMAND "${CMAKE_CTEST_COMMAND}"
    --test-dir "${CMAKE_BINARY_DIR}"
    --output-on-failure
    --label-regex "^product$"
    --parallel 4
  DEPENDS anonsync_product_lane
  USES_TERMINAL
  COMMENT "Run the focused AnonSync replacement-product lane")
