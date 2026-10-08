#pragma once

#include "mtgsim/types.hpp"

#include <string_view>
#include <vector>

namespace mtgsim {

struct RuleModuleDescriptor {
    std::string_view id;
    std::string_view name;
    std::string_view rule_range;
    std::string_view component;
    bool executable = false;
    std::vector<std::string_view> dependencies;
};

[[nodiscard]] const std::vector<RuleModuleDescriptor>& builtin_rule_modules();
[[nodiscard]] const RuleModuleDescriptor* find_rule_module(std::string_view id) noexcept;
[[nodiscard]] bool rule_module_graph_is_acyclic();
[[nodiscard]] std::vector<std::string_view> executable_rule_module_ids();

} // namespace mtgsim
