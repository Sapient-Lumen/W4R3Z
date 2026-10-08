#include <iostream>
#include <locale>
#include <sstream>
#include <string>

class GroupedNumberPunctuation final : public std::numpunct<char> {
protected:
    char do_thousands_sep() const override { return '_'; }
    std::string do_grouping() const override { return "\3"; }
};

std::string parent_signing_input(long long prepared_sequence) {
    std::ostringstream in;
    in << "anonsync-effect-transition-intent-v2-ledger-instance\n"
       << "intent\nsubject\n2026-07-19T00:00:00Z\nsqlite-wal\n"
       << std::string(64, 'a') << "\nGENESIS\nGENESIS\n"
       << std::string(64, 'b') << "\n"
       << prepared_sequence << "\n"
       << std::string(64, 'c') << "\napplied\n"
       << std::string(64, 'd') << "\nrelay applied\n";
    return in.str();
}

std::string parent_json(long long prepared_sequence) {
    std::ostringstream out;
    out << "{\"prepared_sequence\":" << prepared_sequence << "}\n";
    return out.str();
}

int main() {
    constexpr long long sequence = 7000;
    const std::locale previous = std::locale::global(std::locale::classic());
    const std::string classic_signing = parent_signing_input(sequence);
    const std::string classic_json = parent_json(sequence);
    std::locale::global(std::locale(std::locale::classic(),
                                   new GroupedNumberPunctuation));
    const std::string grouped_signing = parent_signing_input(sequence);
    const std::string grouped_json = parent_json(sequence);
    std::locale::global(previous);

    std::cout << "classic_json=" << classic_json;
    std::cout << "grouped_json=" << grouped_json;
    std::cout << "signing_inputs_equal="
              << (classic_signing == grouped_signing ? "true" : "false")
              << "\n";
    const auto grouped_number = grouped_signing.find("7_000\n");
    std::cout << "grouped_signing_contains_7_000="
              << (grouped_number == std::string::npos ? "false" : "true")
              << "\n";
}
