#pragma once

#include <optional>
#include <stdexcept>
#include <string>
#include <utility>

namespace iotox {

enum class ErrorCode {
    ok = 0,
    invalid_argument,
    not_found,
    unsupported,
    unavailable,
    io_error,
    library_error,
    protocol_error,
    timeout,
    internal_error,
    resource_exhausted,
};

class Status {
  public:
    Status() = default;
    Status(ErrorCode code, std::string message) : code_(code), message_(std::move(message)) {}

    [[nodiscard]] static Status success() { return {}; }
    [[nodiscard]] bool ok() const noexcept { return code_ == ErrorCode::ok; }
    [[nodiscard]] explicit operator bool() const noexcept { return ok(); }
    [[nodiscard]] ErrorCode code() const noexcept { return code_; }
    [[nodiscard]] const std::string &message() const noexcept { return message_; }

  private:
    ErrorCode code_{ErrorCode::ok};
    std::string message_;
};

template <typename T>
class Result {
  public:
    Result(T result_value) : value_(std::move(result_value)), status_(Status::success()) {}
    Result(Status error_status) : status_(std::move(error_status)) {
        if (status_.ok()) {
            throw std::invalid_argument("successful Result<T> requires a value");
        }
    }

    [[nodiscard]] bool ok() const noexcept { return value_.has_value(); }
    [[nodiscard]] explicit operator bool() const noexcept { return ok(); }
    [[nodiscard]] const Status &status() const noexcept { return status_; }

    [[nodiscard]] T &value() & {
        if (!value_) {
            throw std::logic_error("Result<T> has no value: " + status_.message());
        }
        return *value_;
    }

    [[nodiscard]] const T &value() const & {
        if (!value_) {
            throw std::logic_error("Result<T> has no value: " + status_.message());
        }
        return *value_;
    }

    [[nodiscard]] T &&value() && {
        if (!value_) {
            throw std::logic_error("Result<T> has no value: " + status_.message());
        }
        return std::move(*value_);
    }

  private:
    std::optional<T> value_;
    Status status_;
};

}  // namespace iotox
