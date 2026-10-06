#include "bzip4/release_audit.hpp"

#include <iostream>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: bzip4_release_audit RELEASE_ROOT\n";
        return 64;
    }
    try {
        const bzip4::AuditReport report = bzip4::audit_release_tree(argv[1]);
        std::cout << bzip4::audit_report_json(report, true);
        return report.ok() ? 0 : 2;
    } catch (const std::exception& exception) {
        std::cerr << "audit failed: " << exception.what() << '\n';
        return 1;
    }
}
