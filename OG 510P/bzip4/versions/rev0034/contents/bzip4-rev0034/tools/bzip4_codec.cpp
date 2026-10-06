#include "bzip4/atomic_file.hpp"
#include "bzip4/codec.hpp"
#include "bzip4/libbz3.h"
#include "bzip4/parallel_codec.hpp"
#include "bzip4/pinned_file.hpp"
#include "bzip4/profile.hpp"
#include "bzip4/resource_plan.hpp"

#include <charconv>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>

namespace {

[[nodiscard]] std::uint64_t parse_u64(std::string_view value, std::string_view field) {
    std::uint64_t result = 0;
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size()) {
        throw std::invalid_argument(std::string(field) + " is not an unsigned integer");
    }
    return result;
}

[[nodiscard]] std::size_t parse_size(std::string_view value, std::string_view field) {
    const std::uint64_t parsed = parse_u64(value, field);
    if (parsed > std::numeric_limits<std::size_t>::max()) {
        throw std::invalid_argument(std::string(field) + " exceeds size_t");
    }
    return static_cast<std::size_t>(parsed);
}

[[nodiscard]] std::uint32_t parse_block_size(
    std::string_view value,
    std::string_view field = "block size") {
    const std::uint64_t parsed = parse_u64(value, field);
    if (parsed > std::numeric_limits<std::uint32_t>::max()) {
        throw std::invalid_argument(std::string(field) + " exceeds uint32");
    }
    return static_cast<std::uint32_t>(parsed);
}

[[nodiscard]] bool parse_bool_flag(std::string_view value, std::string_view field) {
    const std::size_t parsed = parse_size(value, field);
    if (parsed > 1) {
        throw std::invalid_argument(std::string(field) + " must be 0 or 1");
    }
    return parsed == 1;
}

[[nodiscard]] std::size_t process_size(
    const bzip4::PinnedFile& input,
    std::string_view field) {
    if (input.size() > std::numeric_limits<std::size_t>::max()) {
        throw std::invalid_argument(std::string(field) + " exceeds size_t");
    }
    return static_cast<std::size_t>(input.size());
}

[[nodiscard]] bzip4::RangeReader range_reader(const bzip4::PinnedFile& input) {
    return [&input](std::uint64_t offset, std::span<std::byte> output) {
        input.read_into(offset, output);
    };
}

[[nodiscard]] bzip4::ParallelFramePolicy parallel_policy(
    std::size_t lanes,
    std::size_t workspace_budget,
    bool serialize_reads) {
    if (lanes == 0) {
        throw std::invalid_argument("lane count must be at least one");
    }
    bzip4::ParallelFramePolicy policy;
    policy.activation.retained_background_workers = lanes - 1;
    policy.activation.max_active_lanes = lanes;
    policy.activation.caller_participates = true;
    policy.max_workspace_bytes = workspace_budget;
    policy.serialize_range_reads = serialize_reads;
    return policy;
}

void print_parallel_stats(const bzip4::ParallelFrameStats& stats) {
    std::cout << "\nactive_lanes=" << stats.activation.active_lanes
              << "\nretained_background_workers="
              << stats.retained_background_workers
              << "\nretained_workspace_bytes="
              << stats.retained_workspace_bytes
              << "\nbatches=" << stats.batches
              << "\nbackground_notifications="
              << stats.background_notifications;
}

void print_parallel_stats(const bzip4::ParallelDecodeStats& stats) {
    std::cout << "\nactive_lanes=" << stats.activation.active_lanes
              << "\nretained_background_workers="
              << stats.retained_background_workers
              << "\nretained_workspace_bytes="
              << stats.retained_workspace_bytes
              << "\nbatches=" << stats.batches
              << "\nbackground_notifications="
              << stats.background_notifications;
}

void print_plan_json(const bzip4::CompressionResourcePlan& compression) {
    const bzip4::ParallelResourcePlan& plan = compression.parallel;
    std::cout
        << "{\"schema\":\"bzip4.compression-resource-plan.v1\""
        << ",\"input_bytes\":" << compression.input_bytes
        << ",\"requested_block_size\":" << compression.requested_block_size
        << ",\"effective_block_size\":" << compression.effective_block_size
        << ",\"block_count\":" << plan.block_count
        << ",\"requested_lanes\":" << plan.requested_lanes
        << ",\"work_limited_lanes\":" << plan.work_limited_lanes
        << ",\"workspace_lane_capacity\":" << plan.workspace_lane_capacity
        << ",\"selected_lanes\":" << plan.selected_lanes
        << ",\"per_lane_workspace_bytes\":" << plan.per_lane_workspace_bytes
        << ",\"strict_workspace_bytes\":" << plan.strict_workspace_bytes
        << ",\"selected_workspace_bytes\":" << plan.selected_workspace_bytes
        << ",\"max_workspace_bytes\":" << plan.max_workspace_bytes
        << ",\"limited_by_work\":" << (plan.limited_by_work ? "true" : "false")
        << ",\"limited_by_workspace\":"
        << (plan.limited_by_workspace ? "true" : "false")
        << ",\"fits\":" << (plan.fits ? "true" : "false")
        << ",\"lane_count_changes_encoded_bytes\":false}\n";
}

void print_profile_plan_json(
    const bzip4::CodecProfile& profile,
    const bzip4::CompressionResourcePlan& compression) {
    const bzip4::ParallelResourcePlan& plan = compression.parallel;
    std::cout
        << "{\"schema\":\"bzip4.profile-resource-plan.v1\""
        << ",\"profile\":\"" << profile.id << "\""
        << ",\"input_bytes\":" << compression.input_bytes
        << ",\"requested_block_size\":" << compression.requested_block_size
        << ",\"effective_block_size\":" << compression.effective_block_size
        << ",\"block_count\":" << plan.block_count
        << ",\"requested_lanes\":" << plan.requested_lanes
        << ",\"work_limited_lanes\":" << plan.work_limited_lanes
        << ",\"workspace_lane_capacity\":" << plan.workspace_lane_capacity
        << ",\"selected_lanes\":" << plan.selected_lanes
        << ",\"per_lane_workspace_bytes\":" << plan.per_lane_workspace_bytes
        << ",\"selected_workspace_bytes\":" << plan.selected_workspace_bytes
        << ",\"max_workspace_bytes\":" << plan.max_workspace_bytes
        << ",\"limited_by_work\":" << (plan.limited_by_work ? "true" : "false")
        << ",\"limited_by_workspace\":"
        << (plan.limited_by_workspace ? "true" : "false")
        << ",\"fits\":" << (plan.fits ? "true" : "false")
        << ",\"lane_count_changes_encoded_bytes\":false}\n";
}

void print_profiles_json() {
    std::cout << "{\"schema\":\"bzip4.codec-profiles.v1\",\"profiles\":[";
    bool first = true;
    for (const bzip4::CodecProfile& profile : bzip4::codec_profiles()) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << "{\"id\":\"" << profile.id
                  << "\",\"purpose\":\"" << profile.purpose
                  << "\",\"requested_block_size\":" << profile.requested_block_size
                  << ",\"requested_lanes\":" << profile.requested_lanes
                  << ",\"default_workspace_bytes\":"
                  << profile.default_workspace_bytes << '}';
    }
    std::cout << "]}\n";
}

void usage() {
    std::cerr
        << "usage:\n"
        << "  bzip4_codec profiles\n"
        << "  bzip4_codec profile-plan PROFILE INPUT_SIZE [MAX_WORKSPACE_BYTES]\n"
        << "  bzip4_codec compress-profile PROFILE INPUT OUTPUT [MAX_WORKSPACE_BYTES [SERIALIZE_READS(0|1)]]\n"
        << "  bzip4_codec decompress-profile PROFILE INPUT OUTPUT MAX_OUTPUT_BYTES [MAX_WORKSPACE_BYTES [SERIALIZE_READS(0|1)]]\n"
        << "  bzip4_codec plan INPUT_SIZE BLOCK_SIZE LANES [MAX_WORKSPACE_BYTES]\n"
        << "  bzip4_codec compress INPUT OUTPUT [BLOCK_SIZE [LANES [MAX_WORKSPACE_BYTES [SERIALIZE_READS(0|1)]]]]\n"
        << "  bzip4_codec compress-fit INPUT OUTPUT BLOCK_SIZE LANES MAX_WORKSPACE_BYTES [SERIALIZE_READS(0|1)]\n"
        << "  bzip4_codec decompress INPUT OUTPUT MAX_OUTPUT_BYTES [MAX_WORKSPACE_BYTES [LANES [SERIALIZE_READS(0|1)]]]\n"
        << "  bzip4_codec decompress-fit INPUT OUTPUT MAX_OUTPUT_BYTES MAX_WORKSPACE_BYTES LANES [SERIALIZE_READS(0|1)]\n"
        << "  bzip4_codec inspect INPUT MAX_OUTPUT_BYTES [MAX_WORKSPACE_BYTES]\n"
        << "  bzip4_codec version\n";
}

} // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string_view(argv[1]) == "version") {
            std::cout << bzip4::translated_codec_version() << '\n';
            return 0;
        }
        if (argc < 2) {
            usage();
            return 64;
        }

        const std::string_view command = argv[1];
        if (command == "profiles" && argc == 2) {
            print_profiles_json();
            return 0;
        }

        if (command == "profile-plan" && (argc == 4 || argc == 5)) {
            const bzip4::CodecProfile& profile = bzip4::codec_profile(argv[2]);
            const std::size_t input_size = parse_size(argv[3], "input size");
            const std::size_t workspace = argc == 5
                ? parse_size(argv[4], "parallel workspace budget")
                : profile.default_workspace_bytes;
            print_profile_plan_json(
                profile,
                bzip4::plan_parallel_compression(
                    input_size,
                    profile.requested_block_size,
                    profile.requested_lanes,
                    workspace));
            return 0;
        }

        if (command == "compress-profile" && argc >= 5 && argc <= 7) {
            const bzip4::CodecProfile& profile = bzip4::codec_profile(argv[2]);
            bzip4::PinnedFile input(argv[3]);
            const std::size_t input_size = process_size(input, "input size");
            const bzip4::RangeReader reader = range_reader(input);
            const std::size_t workspace = argc >= 6
                ? parse_size(argv[5], "parallel workspace budget")
                : profile.default_workspace_bytes;
            const bool serialize_reads = argc == 7
                ? parse_bool_flag(argv[6], "serialize reads flag") : false;
            const bzip4::CompressionResourcePlan resource =
                bzip4::plan_parallel_compression(
                    input_size,
                    profile.requested_block_size,
                    profile.requested_lanes,
                    workspace);
            if (!resource.parallel.fits) {
                throw bzip4::CodecError(
                    BZ3_ERR_DATA_TOO_BIG,
                    "not even one profile codec lane fits the configured workspace budget");
            }

            bzip4::AtomicFileWriter output(argv[4]);
            const auto sink = [&](std::span<const std::byte> bytes) { output.write(bytes); };
            bzip4::FrameInfo info;
            bzip4::ParallelFrameStats stats;
            if (resource.parallel.block_count == 0) {
                info = bzip4::compress_frame_from(
                    input_size, profile.requested_block_size, reader, sink);
            } else {
                info = bzip4::compress_frame_parallel_from(
                    input_size, profile.requested_block_size, reader, sink,
                    parallel_policy(
                        resource.parallel.selected_lanes, workspace, serialize_reads),
                    &stats);
            }
            if (!bzip4::frame_is_compatible_with_profile(info, profile)) {
                throw std::logic_error("profile encoder emitted a mismatched block policy");
            }
            input.require_unchanged();
            output.commit();
            std::cout << "profile=" << profile.id
                      << "\ninput_bytes=" << input_size
                      << "\noutput_bytes=" << output.bytes_written()
                      << "\nrequested_block_size=" << profile.requested_block_size
                      << "\neffective_block_size=" << info.block_size
                      << "\nblock_count=" << info.block_count
                      << "\nrequested_lanes=" << profile.requested_lanes
                      << "\nselected_lanes=" << resource.parallel.selected_lanes
                      << "\nworkspace_limited="
                      << (resource.parallel.limited_by_workspace ? 1 : 0);
            if (resource.parallel.block_count != 0) print_parallel_stats(stats);
            std::cout << '\n';
            return 0;
        }

        if (command == "decompress-profile" && argc >= 6 && argc <= 8) {
            const bzip4::CodecProfile& profile = bzip4::codec_profile(argv[2]);
            bzip4::PinnedFile encoded(argv[3]);
            const std::size_t encoded_size = process_size(encoded, "encoded input size");
            const bzip4::RangeReader reader = range_reader(encoded);
            const std::size_t maximum = parse_size(argv[5], "maximum output size");
            const std::size_t workspace = argc >= 7
                ? parse_size(argv[6], "maximum workspace size")
                : profile.default_workspace_bytes;
            const bool serialize_reads = argc == 8
                ? parse_bool_flag(argv[7], "serialize reads flag") : false;

            const bzip4::FrameInfo inspected = bzip4::inspect_frame_from(
                encoded_size, reader, maximum, true,
                std::numeric_limits<std::size_t>::max());
            if (!bzip4::frame_is_compatible_with_profile(inspected, profile)) {
                throw bzip4::CodecError(
                    BZ3_ERR_MALFORMED_HEADER,
                    "validated frame does not match the requested codec profile");
            }
            const bzip4::ParallelResourcePlan resource =
                bzip4::plan_parallel_decompression(
                    inspected, profile.requested_lanes, workspace);
            if (!resource.fits) {
                throw bzip4::CodecError(
                    BZ3_ERR_DATA_TOO_BIG,
                    "not even one profile decoder lane fits the configured workspace budget");
            }

            bzip4::AtomicFileWriter output(argv[4]);
            const auto sink = [&](std::span<const std::byte> bytes) { output.write(bytes); };
            bzip4::FrameInfo info;
            bzip4::ParallelDecodeStats stats;
            if (inspected.block_count == 0) {
                info = bzip4::decompress_frame_from(
                    encoded_size, reader, maximum, sink, true, workspace);
            } else {
                info = bzip4::decompress_frame_parallel_from(
                    encoded_size, reader, maximum, sink,
                    parallel_policy(resource.selected_lanes, workspace, serialize_reads),
                    true, &stats);
            }
            if (output.bytes_written() != info.original_size) {
                throw std::logic_error("decoded output byte accounting mismatch");
            }
            encoded.require_unchanged();
            output.commit();
            std::cout << "profile=" << profile.id
                      << "\nencoded_bytes=" << encoded_size
                      << "\ndecoded_bytes=" << output.bytes_written()
                      << "\nblock_count=" << info.block_count
                      << "\ndeclared_block_size=" << info.block_size
                      << "\ndecoder_block_size=" << info.decoder_block_size
                      << "\ndecoder_workspace_bytes=" << info.decoder_workspace_bytes
                      << "\nrequested_lanes=" << profile.requested_lanes
                      << "\nselected_lanes=" << resource.selected_lanes
                      << "\nworkspace_limited="
                      << (resource.limited_by_workspace ? 1 : 0);
            if (inspected.block_count != 0) print_parallel_stats(stats);
            std::cout << '\n';
            return 0;
        }

        if (command == "plan" && (argc == 5 || argc == 6)) {
            const std::size_t input_size = parse_size(argv[2], "input size");
            const std::uint32_t block_size = parse_block_size(argv[3]);
            const std::size_t lanes = parse_size(argv[4], "lane count");
            const std::size_t workspace = argc == 6
                ? parse_size(argv[5], "parallel workspace budget")
                : bzip4::default_parallel_workspace_budget;
            print_plan_json(bzip4::plan_parallel_compression(
                input_size, block_size, lanes, workspace));
            return 0;
        }

        if (command == "compress" && argc >= 4 && argc <= 8) {
            bzip4::PinnedFile input(argv[2]);
            const std::size_t input_size = process_size(input, "input size");
            const bzip4::RangeReader reader = range_reader(input);

            std::uint32_t block_size = 16U * 1024U * 1024U;
            if (argc >= 5) {
                block_size = parse_block_size(argv[4]);
            }
            std::size_t lanes = 1;
            if (argc >= 6) {
                lanes = parse_size(argv[5], "lane count");
                if (lanes == 0) {
                    throw std::invalid_argument("lane count must be at least one");
                }
            }
            std::size_t parallel_budget = bzip4::default_parallel_workspace_budget;
            if (argc >= 7) {
                parallel_budget = parse_size(argv[6], "parallel workspace budget");
            }
            const bool serialize_reads = argc >= 8
                ? parse_bool_flag(argv[7], "serialize reads flag") : false;

            bzip4::AtomicFileWriter output(argv[3]);
            bzip4::FrameInfo info;
            bzip4::ParallelFrameStats parallel_stats;
            const auto sink = [&](std::span<const std::byte> bytes) { output.write(bytes); };
            if (argc >= 6) {
                info = bzip4::compress_frame_parallel_from(
                    input_size, block_size, reader, sink,
                    parallel_policy(lanes, parallel_budget, serialize_reads),
                    &parallel_stats);
            } else {
                info = bzip4::compress_frame_from(input_size, block_size, reader, sink);
            }

            input.require_unchanged();
            output.commit();
            std::cout << "input_bytes=" << input_size
                      << "\noutput_bytes=" << output.bytes_written()
                      << "\nblock_count=" << info.block_count;
            if (argc >= 6) {
                print_parallel_stats(parallel_stats);
            }
            std::cout << '\n';
            return 0;
        }

        if (command == "compress-fit" && (argc == 7 || argc == 8)) {
            bzip4::PinnedFile input(argv[2]);
            const std::size_t input_size = process_size(input, "input size");
            const bzip4::RangeReader reader = range_reader(input);
            const std::uint32_t block_size = parse_block_size(argv[4]);
            const std::size_t requested_lanes = parse_size(argv[5], "lane count");
            const std::size_t workspace = parse_size(argv[6], "parallel workspace budget");
            const bool serialize_reads = argc == 8
                ? parse_bool_flag(argv[7], "serialize reads flag") : false;
            const bzip4::CompressionResourcePlan resource =
                bzip4::plan_parallel_compression(
                    input_size, block_size, requested_lanes, workspace);
            if (!resource.parallel.fits) {
                throw bzip4::CodecError(
                    BZ3_ERR_DATA_TOO_BIG,
                    "not even one codec lane fits the configured workspace budget");
            }

            bzip4::AtomicFileWriter output(argv[3]);
            const auto sink = [&](std::span<const std::byte> bytes) { output.write(bytes); };
            bzip4::FrameInfo info;
            bzip4::ParallelFrameStats stats;
            if (resource.parallel.block_count == 0) {
                info = bzip4::compress_frame_from(input_size, block_size, reader, sink);
            } else {
                info = bzip4::compress_frame_parallel_from(
                    input_size, block_size, reader, sink,
                    parallel_policy(
                        resource.parallel.selected_lanes, workspace, serialize_reads),
                    &stats);
            }
            input.require_unchanged();
            output.commit();
            std::cout << "input_bytes=" << input_size
                      << "\noutput_bytes=" << output.bytes_written()
                      << "\nblock_count=" << info.block_count
                      << "\nrequested_lanes=" << requested_lanes
                      << "\nselected_lanes=" << resource.parallel.selected_lanes
                      << "\nworkspace_limited="
                      << (resource.parallel.limited_by_workspace ? 1 : 0);
            if (resource.parallel.block_count != 0) {
                print_parallel_stats(stats);
            }
            std::cout << '\n';
            return 0;
        }

        if (command == "decompress" && argc >= 5 && argc <= 8) {
            bzip4::PinnedFile encoded(argv[2]);
            const std::size_t encoded_size = process_size(encoded, "encoded input size");
            const bzip4::RangeReader reader = range_reader(encoded);
            const std::size_t maximum = parse_size(argv[4], "maximum output size");
            std::size_t workspace = bzip4::default_decoder_workspace_budget;
            if (argc >= 6) {
                workspace = parse_size(argv[5], "maximum workspace size");
            }
            std::size_t lanes = 1;
            if (argc >= 7) {
                lanes = parse_size(argv[6], "lane count");
                if (lanes == 0) {
                    throw std::invalid_argument("lane count must be at least one");
                }
            }
            const bool serialize_reads = argc >= 8
                ? parse_bool_flag(argv[7], "serialize reads flag") : false;

            bzip4::AtomicFileWriter output(argv[3]);
            bzip4::FrameInfo info;
            bzip4::ParallelDecodeStats parallel_stats;
            const auto sink = [&](std::span<const std::byte> bytes) { output.write(bytes); };
            if (argc >= 7) {
                info = bzip4::decompress_frame_parallel_from(
                    encoded_size, reader, maximum, sink,
                    parallel_policy(lanes, workspace, serialize_reads),
                    true, &parallel_stats);
            } else {
                info = bzip4::decompress_frame_from(
                    encoded_size, reader, maximum, sink, true, workspace);
            }
            if (output.bytes_written() != info.original_size) {
                throw std::logic_error("decoded output byte accounting mismatch");
            }
            encoded.require_unchanged();
            output.commit();
            std::cout << "encoded_bytes=" << encoded_size
                      << "\ndecoded_bytes=" << output.bytes_written()
                      << "\nblock_count=" << info.block_count
                      << "\ndeclared_block_size=" << info.block_size
                      << "\ndecoder_block_size=" << info.decoder_block_size
                      << "\ndecoder_workspace_bytes=" << info.decoder_workspace_bytes;
            if (argc >= 7) {
                print_parallel_stats(parallel_stats);
            }
            std::cout << '\n';
            return 0;
        }

        if (command == "decompress-fit" && (argc == 7 || argc == 8)) {
            bzip4::PinnedFile encoded(argv[2]);
            const std::size_t encoded_size = process_size(encoded, "encoded input size");
            const bzip4::RangeReader reader = range_reader(encoded);
            const std::size_t maximum = parse_size(argv[4], "maximum output size");
            const std::size_t workspace = parse_size(argv[5], "maximum workspace size");
            const std::size_t requested_lanes = parse_size(argv[6], "lane count");
            const bool serialize_reads = argc == 8
                ? parse_bool_flag(argv[7], "serialize reads flag") : false;

            // Envelope inspection allocates no codec state. Use the arithmetic
            // ceiling here, then apply the caller's real budget through the
            // explicit resource plan before any worker or codec arena exists.
            const bzip4::FrameInfo inspected = bzip4::inspect_frame_from(
                encoded_size, reader, maximum, true,
                std::numeric_limits<std::size_t>::max());
            const bzip4::ParallelResourcePlan resource =
                bzip4::plan_parallel_decompression(
                    inspected, requested_lanes, workspace);
            if (!resource.fits) {
                throw bzip4::CodecError(
                    BZ3_ERR_DATA_TOO_BIG,
                    "not even one decoder lane fits the configured workspace budget");
            }

            bzip4::AtomicFileWriter output(argv[3]);
            const auto sink = [&](std::span<const std::byte> bytes) { output.write(bytes); };
            bzip4::FrameInfo info;
            bzip4::ParallelDecodeStats stats;
            if (inspected.block_count == 0) {
                info = bzip4::decompress_frame_from(
                    encoded_size, reader, maximum, sink, true, workspace);
            } else {
                info = bzip4::decompress_frame_parallel_from(
                    encoded_size, reader, maximum, sink,
                    parallel_policy(resource.selected_lanes, workspace, serialize_reads),
                    true, &stats);
            }
            if (output.bytes_written() != info.original_size) {
                throw std::logic_error("decoded output byte accounting mismatch");
            }
            encoded.require_unchanged();
            output.commit();
            std::cout << "encoded_bytes=" << encoded_size
                      << "\ndecoded_bytes=" << output.bytes_written()
                      << "\nblock_count=" << info.block_count
                      << "\ndeclared_block_size=" << info.block_size
                      << "\ndecoder_block_size=" << info.decoder_block_size
                      << "\ndecoder_workspace_bytes=" << info.decoder_workspace_bytes
                      << "\nrequested_lanes=" << requested_lanes
                      << "\nselected_lanes=" << resource.selected_lanes
                      << "\nworkspace_limited="
                      << (resource.limited_by_workspace ? 1 : 0);
            if (inspected.block_count != 0) {
                print_parallel_stats(stats);
            }
            std::cout << '\n';
            return 0;
        }

        if (command == "inspect" && (argc == 4 || argc == 5)) {
            bzip4::PinnedFile encoded(argv[2]);
            const std::size_t encoded_size = process_size(encoded, "encoded input size");
            const bzip4::RangeReader reader = range_reader(encoded);
            const std::size_t maximum = parse_size(argv[3], "maximum output size");
            const std::size_t workspace = argc == 5
                ? parse_size(argv[4], "maximum workspace size")
                : bzip4::default_decoder_workspace_budget;
            const bzip4::FrameInfo info = bzip4::inspect_frame_from(
                encoded_size, reader, maximum, false, workspace);
            encoded.require_unchanged();
            std::cout << "{\"schema\":\"bzip4.frame-info.v2\",\"block_size\":"
                      << info.block_size
                      << ",\"decoder_block_size\":" << info.decoder_block_size
                      << ",\"block_count\":" << info.block_count
                      << ",\"original_size\":" << info.original_size
                      << ",\"encoded_block_bytes\":" << info.encoded_block_bytes
                      << ",\"decoder_workspace_bytes\":" << info.decoder_workspace_bytes
                      << ",\"trailing_bytes\":" << info.trailing_bytes << "}\n";
            return 0;
        }

        usage();
        return 64;
    } catch (const bzip4::CodecError& exception) {
        std::cerr << "codec error " << exception.code() << ": " << exception.what() << '\n';
        return 65;
    } catch (const std::exception& exception) {
        std::cerr << "error: " << exception.what() << '\n';
        return 1;
    }
}
