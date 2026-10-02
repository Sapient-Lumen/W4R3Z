if(NOT DEFINED IOTOX_EXECUTABLE OR IOTOX_EXECUTABLE STREQUAL "")
    message(FATAL_ERROR "IOTOX_EXECUTABLE is required")
endif()

execute_process(
    COMMAND "${IOTOX_EXECUTABLE}" recall-generate
    RESULT_VARIABLE result
    OUTPUT_VARIABLE phrase
    ERROR_VARIABLE error_output
)
if(NOT result EQUAL 0)
    message(FATAL_ERROR
        "recall-generate failed with status ${result}: ${error_output}")
endif()

string(REGEX REPLACE "\n$" "" body "${phrase}")
if(NOT "${body}\n" STREQUAL "${phrase}")
    message(FATAL_ERROR "recall-generate must emit exactly one LF-terminated record")
endif()
if(NOT body MATCHES
   "^[a-z-]+ [a-z-]+ [a-z-]+ [a-z-]+ [a-z-]+ [a-z-]+ [a-z-]+ [a-z-]+$")
    message(FATAL_ERROR "recall-generate did not emit exactly eight lowercase word tokens")
endif()

# A generated RecallRoot is sovereign material even when a test immediately
# discards it. Validate inside this process and never echo it into CTest logs.
set(phrase "")
set(body "")
message(STATUS "recall-generate emitted one valid eight-word record; phrase suppressed")
