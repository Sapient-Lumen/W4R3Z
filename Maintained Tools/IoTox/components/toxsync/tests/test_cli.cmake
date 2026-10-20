cmake_minimum_required(VERSION 3.20)

if(NOT DEFINED TOXSYNC_CLI OR NOT EXISTS "${TOXSYNC_CLI}")
    message(FATAL_ERROR "TOXSYNC_CLI must name the built toxsync executable")
endif()
if(NOT DEFINED TOXSYNC_TEST_ROOT OR
   NOT TOXSYNC_TEST_ROOT MATCHES "toxsync-cli-transaction$")
    message(FATAL_ERROR "unsafe or missing TOXSYNC_TEST_ROOT")
endif()

function(run_ok)
    execute_process(
        COMMAND "${TOXSYNC_CLI}" ${ARGN}
        RESULT_VARIABLE result
        OUTPUT_VARIABLE output
        ERROR_VARIABLE error
    )
    if(NOT result EQUAL 0)
        message(FATAL_ERROR
            "toxsync command failed (${result}): ${ARGN}\n${output}${error}")
    endif()
    set(TOXSYNC_LAST_OUTPUT "${output}" PARENT_SCOPE)
endfunction()

function(run_fail)
    execute_process(
        COMMAND "${TOXSYNC_CLI}" ${ARGN}
        RESULT_VARIABLE result
        OUTPUT_VARIABLE output
        ERROR_VARIABLE error
    )
    if(result EQUAL 0)
        message(FATAL_ERROR
            "toxsync command unexpectedly succeeded: ${ARGN}\n${output}${error}")
    endif()
endfunction()

file(REMOVE_RECURSE "${TOXSYNC_TEST_ROOT}")
file(MAKE_DIRECTORY "${TOXSYNC_TEST_ROOT}/source/nested")
string(REPEAT "alpha-verified-content\n" 4096 alpha)
string(REPEAT "beta-verified-content\n" 2048 beta)
file(WRITE "${TOXSYNC_TEST_ROOT}/source/alpha.txt" "${alpha}")
file(WRITE "${TOXSYNC_TEST_ROOT}/source/nested/beta.txt" "${beta}")
string(REPEAT "11" 32 namespace)

# The portable builtin-SHA lane has no Ed25519 implementation. It must still
# exercise the content-store transaction rather than silently shrinking this
# test to a version check.
set(raw_artifact "${TOXSYNC_TEST_ROOT}/raw-artifact.bin")
file(WRITE "${raw_artifact}" "${alpha}${beta}")
set(raw_store "${TOXSYNC_TEST_ROOT}/raw-store")
set(raw_root "${TOXSYNC_TEST_ROOT}/raw-root.txp")
run_ok(content-build-paged "${raw_artifact}" "${raw_store}" "${raw_root}" auto 1)
run_ok(content-scan "${raw_root}" "${raw_store}" verify)
set(raw_reconstructed "${TOXSYNC_TEST_ROOT}/raw-reconstructed.bin")
run_ok(content-apply "${raw_root}" "${raw_store}" "${raw_reconstructed}")
file(SHA256 "${raw_artifact}" raw_artifact_digest)
file(SHA256 "${raw_reconstructed}" raw_reconstructed_digest)
if(NOT raw_artifact_digest STREQUAL raw_reconstructed_digest)
    message(FATAL_ERROR "raw content reconstruction differs from its input")
endif()

if(TOXSYNC_SIGNING_AVAILABLE)
    set(private_key "${TOXSYNC_TEST_ROOT}/writer.private")
    set(public_key "${TOXSYNC_TEST_ROOT}/writer.public")
    run_ok(head-keygen "${private_key}" "${public_key}")
    file(SHA256 "${private_key}" private_before)
    file(SHA256 "${public_key}" public_before)
    run_fail(head-keygen "${private_key}" "${public_key}")
    file(SHA256 "${private_key}" private_after)
    file(SHA256 "${public_key}" public_after)
    if(NOT private_before STREQUAL private_after OR
       NOT public_before STREQUAL public_after)
        message(FATAL_ERROR "refused key generation changed an existing key")
    endif()
    set(rollback_private "${TOXSYNC_TEST_ROOT}/rollback.private")
    set(occupied_public "${TOXSYNC_TEST_ROOT}/occupied.public")
    file(WRITE "${occupied_public}" "must-not-change")
    file(SHA256 "${occupied_public}" occupied_before)
    run_fail(head-keygen "${rollback_private}" "${occupied_public}")
    file(SHA256 "${occupied_public}" occupied_after)
    if(EXISTS "${rollback_private}" OR
       NOT occupied_before STREQUAL occupied_after)
        message(FATAL_ERROR
            "failed key-pair generation left a partial or changed output")
    endif()

    set(work "${TOXSYNC_TEST_ROOT}/work")
    set(store "${TOXSYNC_TEST_ROOT}/store")
    set(head "${TOXSYNC_TEST_ROOT}/head.txh")
    run_ok(
        publish-tree
        "${TOXSYNC_TEST_ROOT}/source" "${work}" "${store}"
        "${namespace}" 1 "${private_key}" "${head}" none retain
    )
    string(REGEX MATCH "retained-treepack=([^\r\n]+)" unused "${TOXSYNC_LAST_OUTPUT}")
    set(treepack "${CMAKE_MATCH_1}")
    string(REGEX MATCH "retained-root-manifest=([^\r\n]+)" unused "${TOXSYNC_LAST_OUTPUT}")
    set(root_manifest "${CMAKE_MATCH_1}")
    if(NOT EXISTS "${treepack}" OR NOT EXISTS "${root_manifest}")
        message(FATAL_ERROR "publish-tree did not retain its named immutable inputs")
    endif()

    run_ok(head-verify "${head}" "${public_key}")
    if(NOT TOXSYNC_LAST_OUTPUT STREQUAL "valid\n")
        message(FATAL_ERROR "head-verify did not report valid")
    endif()
    run_ok(head-evaluate "${head}" none "${public_key}")
    run_ok(content-scan "${root_manifest}" "${store}" verify)
    set(reconstructed "${TOXSYNC_TEST_ROOT}/reconstructed.txtree")
    run_ok(content-apply "${root_manifest}" "${store}" "${reconstructed}")
    file(SHA256 "${treepack}" treepack_digest)
    file(SHA256 "${reconstructed}" reconstructed_digest)
    if(NOT treepack_digest STREQUAL reconstructed_digest)
        message(FATAL_ERROR "content reconstruction differs from retained treepack")
    endif()

    set(active "${TOXSYNC_TEST_ROOT}/active")
    run_ok(activate-tree "${treepack}" "${active}" "${head}" "${public_key}")
    run_ok(activate-tree "${treepack}" "${active}" "${head}" "${public_key}")
    file(READ "${active}/current/alpha.txt" active_alpha)
    if(NOT active_alpha STREQUAL alpha)
        message(FATAL_ERROR "activated directory content differs from its publication")
    endif()

    run_ok(head-inspect "${head}")
    string(REGEX MATCH "index=([0-9a-f]+)" unused "${TOXSYNC_LAST_OUTPUT}")
    set(manifest_digest "${CMAKE_MATCH_1}")
    string(LENGTH "${manifest_digest}" manifest_digest_length)
    if(NOT manifest_digest_length EQUAL 64 OR
       NOT manifest_digest MATCHES "^[0-9a-f]+$")
        message(FATAL_ERROR "head-inspect did not expose a canonical manifest digest")
    endif()
    set(pin_journal "${TOXSYNC_TEST_ROOT}/pins.log")
    run_ok(pin-set "${pin_journal}" "${namespace}" 1 "${manifest_digest}" 0 1)
    run_ok(pin-list "${pin_journal}")
    run_ok(content-gc "${store}" "${pin_journal}" 1 1 dry-run)
    run_ok(pin-remove "${pin_journal}" "${namespace}" 1)
endif()

string(REPEAT "stable-basis-block\n" 1024 basis)
string(REPEAT "changed-target-block\n" 1024 changed)
file(WRITE "${TOXSYNC_TEST_ROOT}/basis.bin" "${basis}")
file(WRITE "${TOXSYNC_TEST_ROOT}/target.bin" "${basis}${changed}")
run_ok(index "${TOXSYNC_TEST_ROOT}/target.bin"
             "${TOXSYNC_TEST_ROOT}/target.txi" 4096)
run_ok(sync "${TOXSYNC_TEST_ROOT}/basis.bin"
            "${TOXSYNC_TEST_ROOT}/target.txi"
            "${TOXSYNC_TEST_ROOT}/target.bin"
            "${TOXSYNC_TEST_ROOT}/range-output.bin")
run_ok(verify "${TOXSYNC_TEST_ROOT}/target.txi"
              "${TOXSYNC_TEST_ROOT}/range-output.bin")

file(REMOVE_RECURSE "${TOXSYNC_TEST_ROOT}")
