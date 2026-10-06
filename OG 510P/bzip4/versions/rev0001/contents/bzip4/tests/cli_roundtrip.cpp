#include <cstdlib>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <random>
#include <string>
#include <vector>

namespace fs = std::filesystem;

static std::string shell_quote(const fs::path& path) {
    std::string value = path.string();
    std::string quoted = "'";
    for (const char ch : value) {
        if (ch == '\'') quoted += "'\\''";
        else quoted += ch;
    }
    quoted += "'";
    return quoted;
}

static int run(const std::string& command) {
    std::cout << command << '\n';
    return std::system(command.c_str());
}

static void write_le32(std::ostream& output, const std::int32_t value) {
    const auto bits = static_cast<std::uint32_t>(value);
    for (unsigned shift = 0; shift < 32; shift += 8) {
        output.put(static_cast<char>((bits >> shift) & 0xffU));
    }
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: cli_roundtrip /path/to/bzip4\n";
        return 2;
    }

    const fs::path executable = fs::absolute(argv[1]);
    const fs::path root = fs::temp_directory_path() / "bzip4-cli-roundtrip-rev0001";
    std::error_code ignored;
    fs::remove_all(root, ignored);
    fs::create_directories(root);

    const fs::path input = root / "mixed corpus.bin";
    const fs::path archive = root / "mixed corpus.bin.bz3";
    const fs::path restored = root / "restored.bin";

    std::ofstream output(input, std::ios::binary);
    for (int i = 0; i < 18000; ++i) {
        output << "record,type=source,index=" << (i % 300)
               << ",payload=constexpr-auto-repeated-template-body-" << (i % 29) << '\n';
    }
    std::mt19937 generator(0xC001D00DU);
    for (int i = 0; i < 250000; ++i) {
        output.put(static_cast<char>(generator() & 0xffU));
    }
    output.close();

    const auto exe = shell_quote(executable);
    if (run(exe + " -f -b 1 -j 3 " + shell_quote(input) + " " + shell_quote(archive)) != 0) return 1;
    if (run(exe + " -t -j 2 " + shell_quote(archive)) != 0) return 1;
    if (run(exe + " -d -f -j 4 " + shell_quote(archive) + " " + shell_quote(restored)) != 0) return 1;

    std::ifstream a(input, std::ios::binary);
    std::ifstream b(restored, std::ios::binary);
    const std::vector<char> original((std::istreambuf_iterator<char>(a)), {});
    const std::vector<char> decoded((std::istreambuf_iterator<char>(b)), {});
    if (original != decoded) {
        std::cerr << "CLI output differs from input\n";
        return 1;
    }

    const fs::path malformed = root / "negative-size.bz3";
    {
        std::ofstream bad(malformed, std::ios::binary);
        bad.write("BZ3v1", 5);
        write_le32(bad, 1024 * 1024);
        write_le32(bad, -1);
        write_le32(bad, 64);
    }
    if (run(exe + " -t " + shell_quote(malformed)) == 0) {
        std::cerr << "malformed negative block length was accepted\n";
        return 1;
    }

    fs::remove_all(root, ignored);
    return 0;
}
