#pragma once

#include "anonsync_json_value.hpp"

#include <string>

namespace anonsync {

// Parses one complete UTF-8 JSON document. Duplicate object keys, malformed
// Unicode, non-finite numbers, trailing content, and nesting beyond the owned
// depth ceiling are rejected.
[[nodiscard]] Json parse_json_text(const std::string& text);

}  // namespace anonsync
