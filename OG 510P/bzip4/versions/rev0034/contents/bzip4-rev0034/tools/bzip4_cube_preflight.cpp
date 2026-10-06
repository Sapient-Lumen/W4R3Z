#include "bzip4/zip_preflight.hpp"

#include <iostream>
#include <string>
#include <string_view>
#include <vector>

int main(int argc, char** argv) {
    bool pretty = true;
    bool probe_payload_duplicates = false;
    std::vector<std::string> paths;
    for (int index = 1; index < argc; ++index) {
        const std::string_view argument = argv[index];
        if (argument == "--compact") {
            pretty = false;
        } else if (argument == "--probe-payload-duplicates") {
            probe_payload_duplicates = true;
        } else {
            paths.emplace_back(argument);
        }
    }
    if (paths.empty()) {
        std::cerr
            << "usage: bzip4_cube_preflight [--compact] "
               "[--probe-payload-duplicates] ARCHIVE.zip [...]\n";
        return 64;
    }

    bzip4::ZipLimits limits;
    limits.probe_exact_payload_duplicates = probe_payload_duplicates;

    bool all_ok = true;
    const char* newline = pretty ? "\n" : "";
    const char* indent = pretty ? "  " : "";
    std::cout << '{' << newline << indent << "\"schema\":\"bzip4.zip-preflight-batch.v2\"," << newline
              << indent << "\"reports\":[";
    if (pretty) std::cout << '\n';
    for (std::size_t index = 0; index < paths.size(); ++index) {
        bzip4::ZipReport report;
        try {
            report = bzip4::preflight_zip(paths[index], limits);
        } catch (const std::exception& exception) {
            report.path = paths[index];
            report.issues.push_back({"exception", exception.what(), {}, true});
        }
        all_ok = all_ok && report.ok();
        if (pretty) std::cout << "    ";
        std::string json = bzip4::zip_report_json(report, false);
        if (!json.empty() && json.back() == '\n') json.pop_back();
        std::cout << json;
        if (index + 1 != paths.size()) std::cout << ',';
        if (pretty) std::cout << '\n';
    }
    std::cout << indent << "]," << newline << indent << "\"ok\":"
              << (all_ok ? "true" : "false") << newline << '}' << newline;
    return all_ok ? 0 : 2;
}
