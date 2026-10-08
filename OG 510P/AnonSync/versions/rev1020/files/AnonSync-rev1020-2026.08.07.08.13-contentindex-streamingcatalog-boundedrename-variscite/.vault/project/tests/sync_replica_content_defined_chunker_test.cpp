#include "sync_replica_content_defined_chunker.hpp"

#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using anonsync::SyncReplicaContentDefinedChunker;
using anonsync::SyncReplicaContentDefinedChunkingParameters;

std::uint64_t checks = 0U;

void expect(bool condition, const char* label) {
    ++checks;
    if (!condition) throw std::runtime_error(label);
}

template <typename Function>
void expect_throw(Function&& function, const char* label) {
    ++checks;
    try {
        function();
    } catch (const std::exception&) {
        return;
    }
    throw std::runtime_error(label);
}

std::vector<std::uint64_t> project(
    const std::string& bytes,
    SyncReplicaContentDefinedChunkingParameters parameters) {
    SyncReplicaContentDefinedChunker chunker(parameters, "test chunker");
    std::vector<std::uint64_t> chunks;
    std::uint64_t pending = 0U;
    for (unsigned char byte : bytes) {
        ++pending;
        if (chunker.consume_byte(byte)) {
            chunks.push_back(pending);
            pending = 0U;
        }
    }
    if (pending != 0U) {
        chunker.finish_pending_chunk_or_throw();
        chunks.push_back(pending);
    }
    expect(chunker.completed_chunk_count() == chunks.size(),
           "chunker count disagrees with emitted boundaries");
    return chunks;
}

}  // namespace

int main() {
    try {
        const SyncReplicaContentDefinedChunkingParameters parameters{
            8U, 16U, 32U, 16U};
        anonsync::validate_sync_replica_content_defined_chunking_parameters_or_throw(
            parameters, "test parameters");
        ++checks;

        std::string bytes;
        for (std::uint64_t index = 0U; index < 257U; ++index) {
            bytes.push_back(static_cast<char>(
                (index * 73U + (index >> 2U) + 19U) & 0xffU));
        }
        const auto first = project(bytes, parameters);
        const auto second = project(bytes, parameters);
        expect(first == second, "chunk boundaries were not deterministic");
        std::uint64_t total = 0U;
        for (std::uint64_t size : first) {
            expect(size >= parameters.minimum_chunk_bytes ||
                       total + size == bytes.size(),
                   "nonfinal chunk was shorter than the minimum");
            expect(size <= parameters.maximum_chunk_bytes,
                   "chunk exceeded the maximum");
            total += size;
        }
        expect(total == bytes.size(), "chunking did not cover the input");

        const auto forced = project(std::string(65U, '\0'), parameters);
        expect(forced.size() >= 3U,
               "maximum boundary did not force bounded chunks");
        expect(forced.front() == parameters.maximum_chunk_bytes,
               "zero stream did not reach the exact forced maximum");

        std::string shifted = bytes;
        shifted.insert(41U, "inserted-content");
        const auto shifted_chunks = project(shifted, parameters);
        expect(!shifted_chunks.empty(), "shifted fixture emitted no chunks");
        expect(shifted_chunks != first,
               "inserted fixture did not alter any boundary");

        // A checkpoint is allocation-free scheduling state. Splitting at an
        // arbitrary interior byte must preserve every later boundary exactly.
        SyncReplicaContentDefinedChunker uninterrupted(
            parameters, "uninterrupted checkpoint fixture");
        SyncReplicaContentDefinedChunker prefix(
            parameters, "prefix checkpoint fixture");
        std::vector<std::uint64_t> uninterrupted_boundaries;
        std::vector<std::uint64_t> resumed_boundaries;
        constexpr std::size_t split = 71U;
        for (std::size_t index = 0U; index < bytes.size(); ++index) {
            if (uninterrupted.consume_byte(
                    static_cast<std::uint8_t>(
                        static_cast<unsigned char>(bytes[index])))) {
                uninterrupted_boundaries.push_back(index + 1U);
            }
            if (index < split && prefix.consume_byte(
                    static_cast<std::uint8_t>(
                        static_cast<unsigned char>(bytes[index])))) {
                resumed_boundaries.push_back(index + 1U);
            }
        }
        const auto checkpoint = prefix.checkpoint();
        anonsync::validate_sync_replica_content_defined_chunker_checkpoint_or_throw(
            parameters, checkpoint, "checkpoint fixture");
        ++checks;
        SyncReplicaContentDefinedChunker resumed(
            parameters, checkpoint, "resumed checkpoint fixture");
        for (std::size_t index = split; index < bytes.size(); ++index) {
            if (resumed.consume_byte(
                    static_cast<std::uint8_t>(
                        static_cast<unsigned char>(bytes[index])))) {
                resumed_boundaries.push_back(index + 1U);
            }
        }
        expect(
            resumed_boundaries == uninterrupted_boundaries,
            "resumed chunker changed a later boundary");
        expect(
            resumed.checkpoint() == uninterrupted.checkpoint(),
            "resumed chunker ended with different scalar state");

        expect_throw(
            [&] {
                anonsync::validate_sync_replica_content_defined_chunker_checkpoint_or_throw(
                    parameters,
                    {1U, 0U, 0U, false},
                    "noncanonical empty checkpoint");
            },
            "empty checkpoint accepted a nonzero gear hash");
        expect_throw(
            [&] {
                anonsync::validate_sync_replica_content_defined_chunker_checkpoint_or_throw(
                    parameters,
                    {0U, parameters.maximum_chunk_bytes, 0U, false},
                    "maximum pending checkpoint");
            },
            "maximum-sized pending checkpoint was accepted");
        expect_throw(
            [&] {
                anonsync::validate_sync_replica_content_defined_chunker_checkpoint_or_throw(
                    parameters,
                    {0U, 1U, parameters.maximum_chunk_count, false},
                    "exhausted checkpoint");
            },
            "exhausted checkpoint retained pending bytes");

        expect_throw(
            [] {
                anonsync::validate_sync_replica_content_defined_chunking_parameters_or_throw(
                    {8U, 15U, 32U, 4U}, "invalid");
            },
            "non-power-of-two average was accepted");
        expect_throw(
            [] {
                SyncReplicaContentDefinedChunker chunker(
                    {8U, 16U, 32U, 1U}, "count frontier");
                for (std::size_t index = 0U; index < 64U; ++index) {
                    (void)chunker.consume_byte(0U);
                }
            },
            "chunk-count frontier was not enforced");

        std::cout << "sync replica content-defined chunker tests passed: "
                  << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica content-defined chunker test failure: "
                  << error.what() << '\n';
        return 1;
    }
}
