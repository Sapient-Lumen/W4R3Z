#include "iotox/rollback_witness_service.hpp"

#include "iotox/security/random.hpp"
#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <linux/fs.h>
#include <netdb.h>
#include <netinet/in.h>
#include <poll.h>
#include <span>
#include <string>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/file.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::rollback_witness {
namespace {

constexpr std::array<std::uint8_t, 8U> kRequestMagic = {
    'I', 'O', 'T', 'X', 'W', 'R', 'Q', '1'};
constexpr std::array<std::uint8_t, 8U> kResponseMagic = {
    'I', 'O', 'T', 'X', 'W', 'R', 'S', '1'};
constexpr std::array<std::uint8_t, 8U> kStoreMagic = {
    'I', 'O', 'T', 'X', 'W', 'S', 'T', '1'};
constexpr std::array<std::uint8_t, 8U> kEnrollmentMagic = {
    'I', 'O', 'T', 'X', 'W', 'E', 'N', '1'};
constexpr std::array<std::uint8_t, 8U> kCheckpointMagic = {
    'I', 'O', 'T', 'X', 'W', 'C', 'P', '1'};
constexpr std::uint8_t kOperationQuery = 1U;
constexpr std::uint8_t kOperationCompareExchange = 2U;
constexpr std::uint8_t kResponseOk = 0U;
constexpr std::uint8_t kResponseConflict = 1U;
constexpr std::uint8_t kResponseNotFound = 2U;
constexpr std::uint8_t kResponseInvalid = 3U;
constexpr std::uint8_t kResponseInternal = 4U;
constexpr std::size_t kSelectorBytes = 64U;
constexpr std::size_t kStoreBytes =
    kStoreMagic.size() + kWireRecordBytes + security::kSignatureBytes;

void put_u64(std::span<std::uint8_t, 8U> output, std::uint64_t value) {
    for (std::size_t index = 0U; index < output.size(); ++index) {
        output[index] = static_cast<std::uint8_t>(
            value >> ((output.size() - 1U - index) * 8U));
    }
}

std::uint64_t get_u64(std::span<const std::uint8_t, 8U> input) {
    std::uint64_t value = 0U;
    for (const std::uint8_t byte : input) {
        value = (value << 8U) | byte;
    }
    return value;
}

bool all_zero(std::span<const std::uint8_t> bytes) {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

Status encode_record(const Record &record,
                     std::span<std::uint8_t, kWireRecordBytes> output) {
    const Status valid = validate(record);
    if (!valid.ok()) return valid;
    std::fill(output.begin(), output.end(), 0U);
    constexpr std::array<std::uint8_t, 8U> magic = {
        'I', 'O', 'T', 'X', 'W', 'R', '1', '\0'};
    std::copy(magic.begin(), magic.end(), output.begin());
    output[8U] = 1U;
    output[9U] = static_cast<std::uint8_t>(record.lane);
    output[10U] = record.pending ? 1U : 0U;
    std::copy(record.domain.begin(), record.domain.end(), output.begin() + 16U);
    std::copy(record.device.begin(), record.device.end(), output.begin() + 32U);
    put_u64(output.subspan<64U, 8U>(), record.witness_epoch);
    put_u64(output.subspan<72U, 8U>(), record.committed.position);
    std::copy(record.committed.digest.begin(), record.committed.digest.end(),
              output.begin() + 80U);
    if (record.pending) {
        put_u64(output.subspan<112U, 8U>(), record.pending->position);
        std::copy(record.pending->digest.begin(), record.pending->digest.end(),
                  output.begin() + 120U);
        std::copy(record.nonce->begin(), record.nonce->end(),
                  output.begin() + 152U);
    }
    return Status::success();
}

Result<Record> decode_record(
    std::span<const std::uint8_t, kWireRecordBytes> input) {
    constexpr std::array<std::uint8_t, 8U> magic = {
        'I', 'O', 'T', 'X', 'W', 'R', '1', '\0'};
    if (!std::equal(magic.begin(), magic.end(), input.begin()) ||
        input[8U] != 1U || (input[10U] & ~1U) != 0U ||
        !all_zero(input.subspan(11U, 5U))) {
        return Status{ErrorCode::protocol_error,
                      "witness service record header is invalid"};
    }
    Record record;
    record.lane = static_cast<Lane>(input[9U]);
    std::copy_n(input.begin() + 16U, record.domain.size(), record.domain.begin());
    std::copy_n(input.begin() + 32U, record.device.size(), record.device.begin());
    record.witness_epoch = get_u64(input.subspan<64U, 8U>());
    record.committed.position = get_u64(input.subspan<72U, 8U>());
    std::copy_n(input.begin() + 80U, record.committed.digest.size(),
                record.committed.digest.begin());
    if (input[10U] != 0U) {
        Head pending;
        pending.position = get_u64(input.subspan<112U, 8U>());
        std::copy_n(input.begin() + 120U, pending.digest.size(),
                    pending.digest.begin());
        TransactionNonce nonce{};
        std::copy_n(input.begin() + 152U, nonce.size(), nonce.begin());
        record.pending = pending;
        record.nonce = nonce;
    } else if (!all_zero(input.subspan(112U))) {
        return Status{ErrorCode::protocol_error,
                      "witness service committed record has non-zero pending bytes"};
    }
    const Status valid = validate(record);
    if (!valid.ok()) return valid;
    return record;
}

Status encode_selector(const Record &record,
                       std::span<std::uint8_t, kSelectorBytes> output) {
    const Status valid = validate(record);
    if (!valid.ok()) return valid;
    std::fill(output.begin(), output.end(), 0U);
    std::copy(record.domain.begin(), record.domain.end(), output.begin());
    std::copy(record.device.begin(), record.device.end(), output.begin() + 16U);
    put_u64(output.subspan<48U, 8U>(), record.witness_epoch);
    output[56U] = static_cast<std::uint8_t>(record.lane);
    return Status::success();
}

Result<Record> decode_selector(
    std::span<const std::uint8_t, kSelectorBytes> input) {
    if (!all_zero(input.subspan(57U, 7U))) {
        return Status{ErrorCode::protocol_error,
                      "witness service selector reserved bytes are non-zero"};
    }
    Record selector;
    std::copy_n(input.begin(), selector.domain.size(), selector.domain.begin());
    std::copy_n(input.begin() + 16U, selector.device.size(), selector.device.begin());
    selector.witness_epoch = get_u64(input.subspan<48U, 8U>());
    selector.lane = static_cast<Lane>(input[56U]);
    const Status valid = validate(selector);
    if (!valid.ok()) return valid;
    return selector;
}

bool same_selector(const Record &left, const Record &right) {
    return left.domain == right.domain && left.device == right.device &&
        left.witness_epoch == right.witness_epoch && left.lane == right.lane;
}

bool selector_less(const Record &left, const Record &right) {
    if (left.domain != right.domain) return left.domain < right.domain;
    if (left.device != right.device) return left.device < right.device;
    if (left.witness_epoch != right.witness_epoch) {
        return left.witness_epoch < right.witness_epoch;
    }
    return static_cast<std::uint8_t>(left.lane) <
        static_cast<std::uint8_t>(right.lane);
}

Status require_descendant(const Record &current, const Record &floor) {
    if (!same_selector(current, floor)) {
        return Status{ErrorCode::protocol_error,
                      "witness checkpoint selector is absent from the service store"};
    }
    if (floor.pending) {
        if (current == floor) return Status::success();
        const Head &required = *floor.pending;
        if (current.committed.position < required.position ||
            (current.committed.position == required.position &&
             current.committed.digest != required.digest)) {
            return Status{ErrorCode::protocol_error,
                          "witness service record is behind or forked from its pending checkpoint floor"};
        }
        return Status::success();
    }
    if (current.committed.position < floor.committed.position ||
        (current.committed.position == floor.committed.position &&
         current.committed.digest != floor.committed.digest)) {
        return Status{ErrorCode::protocol_error,
                      "witness service record is behind or forked from its checkpoint floor"};
    }
    return Status::success();
}

Status socket_status(std::string operation, int error = errno) {
    return Status{ErrorCode::unavailable,
                  std::move(operation) + ": " + std::strerror(error)};
}

Status wait_descriptor(int descriptor, short events,
                       std::chrono::milliseconds timeout) {
    struct pollfd item { descriptor, events, 0 };
    int result = -1;
    do {
        result = ::poll(&item, 1U, static_cast<int>(timeout.count()));
    } while (result < 0 && errno == EINTR);
    if (result == 0) {
        return Status{ErrorCode::timeout, "witness service socket timed out"};
    }
    if (result < 0) return socket_status("unable to poll witness service socket");
    if ((item.revents & events) == 0) {
        return Status{ErrorCode::unavailable,
                      "witness service socket closed or failed"};
    }
    return Status::success();
}

Status send_all(int descriptor, std::span<const std::uint8_t> bytes,
                std::chrono::milliseconds timeout) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const Status ready = wait_descriptor(descriptor, POLLOUT, timeout);
        if (!ready.ok()) return ready;
        const ssize_t count = ::send(
            descriptor, bytes.data() + offset, bytes.size() - offset,
            MSG_NOSIGNAL);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) return socket_status("unable to send witness service record");
        offset += static_cast<std::size_t>(count);
    }
    return Status::success();
}

Status receive_all(int descriptor, std::span<std::uint8_t> bytes,
                   std::chrono::milliseconds timeout) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const Status ready = wait_descriptor(descriptor, POLLIN, timeout);
        if (!ready.ok()) return ready;
        const ssize_t count =
            ::recv(descriptor, bytes.data() + offset, bytes.size() - offset, 0);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            return Status{ErrorCode::unavailable,
                          "witness service closed before its fixed record completed"};
        }
        offset += static_cast<std::size_t>(count);
    }
    return Status::success();
}

Result<int> connect_service(const ServiceEndpoint &endpoint) {
    struct addrinfo hints {};
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;
    struct addrinfo *addresses = nullptr;
    const int resolved = ::getaddrinfo(endpoint.host.c_str(),
                                       endpoint.service.c_str(), &hints,
                                       &addresses);
    if (resolved != 0) {
        return Status{ErrorCode::unavailable,
                      "unable to resolve witness service: " +
                          std::string{::gai_strerror(resolved)}};
    }
    int connected = -1;
    int final_error = ECONNREFUSED;
    for (struct addrinfo *address = addresses; address != nullptr;
         address = address->ai_next) {
        const int descriptor = ::socket(
            address->ai_family,
            address->ai_socktype | SOCK_CLOEXEC | SOCK_NONBLOCK,
            address->ai_protocol);
        if (descriptor < 0) {
            final_error = errno;
            continue;
        }
        if (::connect(descriptor, address->ai_addr, address->ai_addrlen) == 0) {
            connected = descriptor;
            break;
        }
        if (errno == EINPROGRESS) {
            const Status ready = wait_descriptor(
                descriptor, POLLOUT, endpoint.timeout);
            int socket_error = 0;
            socklen_t size = sizeof(socket_error);
            if (ready.ok() &&
                ::getsockopt(descriptor, SOL_SOCKET, SO_ERROR, &socket_error,
                             &size) == 0 &&
                socket_error == 0) {
                connected = descriptor;
                break;
            }
            final_error = socket_error != 0 ? socket_error : ETIMEDOUT;
        } else {
            final_error = errno;
        }
        (void)::close(descriptor);
    }
    ::freeaddrinfo(addresses);
    if (connected < 0) {
        return socket_status("unable to connect to witness service", final_error);
    }
    return connected;
}

Result<ServiceResponseBytes> transact(
    const ServiceEndpoint &endpoint, const ServiceRequestBytes &request) {
    auto connected = connect_service(endpoint);
    if (!connected) return connected.status();
    const int descriptor = connected.value();
    const Status sent = send_all(descriptor, request, endpoint.timeout);
    ServiceResponseBytes response{};
    Status received = sent.ok()
        ? receive_all(descriptor, response, endpoint.timeout)
        : sent;
    const int close_result = ::close(descriptor);
    if (!received.ok()) return received;
    if (close_result != 0) {
        return socket_status("unable to close witness service socket");
    }
    return response;
}

Result<ServiceResponseBytes> make_response(
    std::uint8_t status, std::span<const std::uint8_t, 32U> nonce,
    const Record *record, const security::DeviceIdentity &identity) {
    ServiceResponseBytes response{};
    std::copy(kResponseMagic.begin(), kResponseMagic.end(), response.begin());
    response[8U] = status;
    std::copy(nonce.begin(), nonce.end(), response.begin() + 16U);
    if (record != nullptr) {
        const Status encoded = encode_record(
            *record,
            std::span<std::uint8_t, kWireRecordBytes>{
                response.data() + 48U, kWireRecordBytes});
        if (!encoded.ok()) return encoded;
    }
    auto signature = identity.sign(
        std::span<const std::uint8_t>{response}.first<232U>());
    if (!signature) return signature.status();
    std::copy(signature.value().begin(), signature.value().end(),
              response.begin() + 232U);
    return response;
}

Status sync_parent(const std::filesystem::path &path) {
    const int descriptor = ::open(path.c_str(),
                                  O_RDONLY | O_DIRECTORY | O_CLOEXEC |
                                      O_NOFOLLOW);
    if (descriptor < 0) {
        return Status{ErrorCode::io_error,
                      "unable to open witness service directory: " +
                          std::string{std::strerror(errno)}};
    }
    const int sync_result = ::fsync(descriptor);
    const int sync_error = errno;
    const int close_result = ::close(descriptor);
    if (sync_result != 0) {
        return Status{ErrorCode::io_error,
                      "unable to sync witness service directory: " +
                          std::string{std::strerror(sync_error)}};
    }
    if (close_result != 0) {
        return Status{ErrorCode::io_error,
                      "unable to close witness service directory"};
    }
    return Status::success();
}

}  // namespace

Result<EnrollmentBytes> create_enrollment(
    const Record &committed,
    const security::DeviceIdentity &device_identity) {
    const Status valid = validate(committed);
    if (!valid.ok() || committed.pending ||
        committed.device != device_identity.public_key()) {
        return Status{ErrorCode::invalid_argument,
                      "witness enrollment must bind one committed head to its device signer"};
    }
    EnrollmentBytes enrollment{};
    std::copy(kEnrollmentMagic.begin(), kEnrollmentMagic.end(),
              enrollment.begin());
    enrollment[8U] = static_cast<std::uint8_t>(committed.lane);
    std::copy(committed.domain.begin(), committed.domain.end(),
              enrollment.begin() + 16U);
    std::copy(committed.device.begin(), committed.device.end(),
              enrollment.begin() + 32U);
    put_u64(std::span<std::uint8_t, 8U>{enrollment.data() + 64U, 8U},
            committed.witness_epoch);
    put_u64(std::span<std::uint8_t, 8U>{enrollment.data() + 72U, 8U},
            committed.committed.position);
    std::copy(committed.committed.digest.begin(),
              committed.committed.digest.end(), enrollment.begin() + 80U);
    auto signature = device_identity.sign(
        std::span<const std::uint8_t>{enrollment}.first<112U>());
    if (!signature) return signature.status();
    std::copy(signature.value().begin(), signature.value().end(),
              enrollment.begin() + 112U);
    return enrollment;
}

Result<Record> verify_enrollment(
    std::span<const std::uint8_t, kEnrollmentBytes> enrollment,
    const security::Sodium &sodium) {
    if (!std::equal(kEnrollmentMagic.begin(), kEnrollmentMagic.end(),
                    enrollment.begin()) ||
        !all_zero(enrollment.subspan(9U, 7U))) {
        return Status{ErrorCode::protocol_error,
                      "witness enrollment header is invalid"};
    }
    Record record;
    record.lane = static_cast<Lane>(enrollment[8U]);
    std::copy_n(enrollment.begin() + 16U, record.domain.size(),
                record.domain.begin());
    std::copy_n(enrollment.begin() + 32U, record.device.size(),
                record.device.begin());
    record.witness_epoch = get_u64(
        std::span<const std::uint8_t, 8U>{enrollment.data() + 64U, 8U});
    record.committed.position = get_u64(
        std::span<const std::uint8_t, 8U>{enrollment.data() + 72U, 8U});
    std::copy_n(enrollment.begin() + 80U, record.committed.digest.size(),
                record.committed.digest.begin());
    const Status valid = validate(record);
    if (!valid.ok()) return valid;
    security::Signature signature{};
    std::copy_n(enrollment.begin() + 112U, signature.size(),
                signature.begin());
    const Status verified = sodium.verify_detached(
        signature, enrollment.first<112U>(), record.device);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "witness enrollment device signature is invalid"};
    }
    return record;
}

Result<ServiceCheckpoint> verify_service_checkpoint(
    std::span<const std::uint8_t> checkpoint,
    const security::SigningPublicKey &expected_service_key,
    const security::Sodium &sodium) {
    const std::size_t minimum = kServiceCheckpointHeaderBytes +
        kServiceCheckpointSignatureBytes;
    if (checkpoint.size() < minimum ||
        !std::equal(kCheckpointMagic.begin(), kCheckpointMagic.end(),
                    checkpoint.begin()) ||
        checkpoint[8U] != 1U || !all_zero(checkpoint.subspan(9U, 7U)) ||
        !all_zero(checkpoint.subspan(56U, 8U))) {
        return Status{ErrorCode::protocol_error,
                      "witness service checkpoint header is invalid"};
    }
    security::SigningPublicKey service_key{};
    std::copy_n(checkpoint.begin() + 16U, service_key.size(),
                service_key.begin());
    if (all_zero(expected_service_key) || service_key != expected_service_key) {
        return Status{ErrorCode::protocol_error,
                      "witness service checkpoint signer does not match the pinned key"};
    }
    const std::uint64_t count = get_u64(
        std::span<const std::uint8_t, 8U>{checkpoint.data() + 48U, 8U});
    if (count == 0U || count > kMaximumServiceCheckpointRecords) {
        return Status{ErrorCode::protocol_error,
                      "witness service checkpoint record count is invalid"};
    }
    const std::size_t expected_size = kServiceCheckpointHeaderBytes +
        static_cast<std::size_t>(count) * kWireRecordBytes +
        kServiceCheckpointSignatureBytes;
    if (checkpoint.size() != expected_size) {
        return Status{ErrorCode::protocol_error,
                      "witness service checkpoint length is invalid"};
    }
    security::Signature signature{};
    std::copy_n(checkpoint.end() -
                    static_cast<std::ptrdiff_t>(signature.size()),
                signature.size(), signature.begin());
    const Status signed_ok = sodium.verify_detached(
        signature, checkpoint.first(checkpoint.size() - signature.size()),
        service_key);
    if (!signed_ok.ok()) {
        return Status{ErrorCode::protocol_error,
                      "witness service checkpoint signature is invalid"};
    }
    ServiceCheckpoint decoded;
    decoded.service_key = service_key;
    decoded.records.reserve(static_cast<std::size_t>(count));
    std::size_t offset = kServiceCheckpointHeaderBytes;
    for (std::uint64_t index = 0U; index < count; ++index) {
        auto record = decode_record(
            std::span<const std::uint8_t, kWireRecordBytes>{
                checkpoint.data() + offset, kWireRecordBytes});
        if (!record) return record.status();
        if (!decoded.records.empty() &&
            !selector_less(decoded.records.back(), record.value())) {
            return Status{ErrorCode::protocol_error,
                          "witness service checkpoint selectors are not unique and sorted"};
        }
        decoded.records.push_back(std::move(record).value());
        offset += kWireRecordBytes;
    }
    return decoded;
}

RemoteBackend::RemoteBackend(RemoteBackendConfig config,
                             const security::DeviceIdentity &device_identity,
                             const security::Sodium &sodium)
    : config_(std::move(config)), device_identity_(&device_identity),
      sodium_(&sodium) {}

Result<std::shared_ptr<RemoteBackend>> RemoteBackend::create(
    RemoteBackendConfig config,
    const security::DeviceIdentity &device_identity,
    const security::Sodium &sodium) {
    Record selector;
    selector.domain = config.domain;
    selector.device = device_identity.public_key();
    selector.witness_epoch = config.witness_epoch;
    selector.lane = config.lane;
    const Status valid = validate(selector);
    if (!valid.ok() || config.endpoint.host.empty() ||
        config.endpoint.service.empty() || config.endpoint.timeout.count() <= 0 ||
        all_zero(config.service_key)) {
        return Status{ErrorCode::invalid_argument,
                      "remote witness service configuration is incomplete"};
    }
    return std::shared_ptr<RemoteBackend>{new RemoteBackend(
        std::move(config), device_identity, sodium)};
}

Result<ServiceResponseBytes> RemoteBackend::exchange(
    std::uint8_t operation, const Record *expected, const Record *desired) {
    ServiceRequestBytes request{};
    std::copy(kRequestMagic.begin(), kRequestMagic.end(), request.begin());
    request[8U] = operation;
    std::span<std::uint8_t, 32U> request_nonce{
        request.data() + 16U, 32U};
    const Status random = security::fill_random(request_nonce);
    if (!random.ok()) return random;
    Record selector;
    selector.domain = config_.domain;
    selector.device = device_identity_->public_key();
    selector.witness_epoch = config_.witness_epoch;
    selector.lane = config_.lane;
    const Status selected = encode_selector(
        selector, std::span<std::uint8_t, kSelectorBytes>{
                      request.data() + 48U, kSelectorBytes});
    if (!selected.ok()) return selected;
    if (expected != nullptr) {
        const Status encoded = encode_record(
            *expected, std::span<std::uint8_t, kWireRecordBytes>{
                           request.data() + 112U, kWireRecordBytes});
        if (!encoded.ok()) return encoded;
    }
    if (desired != nullptr) {
        const Status encoded = encode_record(
            *desired, std::span<std::uint8_t, kWireRecordBytes>{
                          request.data() + 296U, kWireRecordBytes});
        if (!encoded.ok()) return encoded;
    }
    auto signature = device_identity_->sign(
        std::span<const std::uint8_t>{request}.first<480U>());
    if (!signature) return signature.status();
    std::copy(signature.value().begin(), signature.value().end(),
              request.begin() + 480U);

    auto response = transact(config_.endpoint, request);
    if (!response) return response.status();
    if (!std::equal(kResponseMagic.begin(), kResponseMagic.end(),
                    response.value().begin()) ||
        !all_zero(std::span<const std::uint8_t>{response.value()}.subspan(9U, 7U)) ||
        !security::constant_time_equal(
            request_nonce,
            std::span<const std::uint8_t>{response.value()}.subspan<16U, 32U>())) {
        return Status{ErrorCode::protocol_error,
                      "witness service response header or nonce is invalid"};
    }
    security::Signature response_signature{};
    std::copy_n(response.value().begin() + 232U, response_signature.size(),
                response_signature.begin());
    const Status verified = sodium_->verify_detached(
        response_signature,
        std::span<const std::uint8_t>{response.value()}.first<232U>(),
        config_.service_key);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "witness service response signature is invalid"};
    }
    return response;
}

Result<Record> RemoteBackend::query() {
    auto response = exchange(kOperationQuery, nullptr, nullptr);
    if (!response) return response.status();
    if (response.value()[8U] == kResponseNotFound) {
        return Status{ErrorCode::not_found,
                      "witness service has no enrollment for this device lane"};
    }
    if (response.value()[8U] != kResponseOk) {
        return Status{response.value()[8U] == kResponseInvalid
                          ? ErrorCode::protocol_error
                          : ErrorCode::unavailable,
                      "witness service refused query"};
    }
    auto record = decode_record(
        std::span<const std::uint8_t, kWireRecordBytes>{
            response.value().data() + 48U, kWireRecordBytes});
    if (!record || record.value().domain != config_.domain ||
        record.value().device != device_identity_->public_key() ||
        record.value().witness_epoch != config_.witness_epoch ||
        record.value().lane != config_.lane) {
        return Status{ErrorCode::protocol_error,
                      "witness service returned another lane or an invalid record"};
    }
    return record;
}

Status RemoteBackend::compare_exchange(const Record &expected,
                                       const Record &desired) {
    const Status transition = validate_transition(expected, desired);
    if (!transition.ok() || expected.domain != config_.domain ||
        expected.device != device_identity_->public_key() ||
        expected.witness_epoch != config_.witness_epoch ||
        expected.lane != config_.lane) {
        return Status{ErrorCode::invalid_argument,
                      "remote witness CAS is not the configured exact transition"};
    }
    auto response = exchange(kOperationCompareExchange, &expected, &desired);
    if (!response) return response.status();
    if (response.value()[8U] == kResponseConflict) {
        return Status{ErrorCode::protocol_error,
                      "remote witness CAS lost an exact-state race"};
    }
    if (response.value()[8U] != kResponseOk) {
        return Status{response.value()[8U] == kResponseInvalid
                          ? ErrorCode::protocol_error
                          : ErrorCode::unavailable,
                      "remote witness service refused CAS"};
    }
    auto current = decode_record(
        std::span<const std::uint8_t, kWireRecordBytes>{
            response.value().data() + 48U, kWireRecordBytes});
    if (!current || !(current.value() == desired)) {
        return Status{ErrorCode::protocol_error,
                      "remote witness CAS acknowledgement has the wrong head"};
    }
    return Status::success();
}

ServiceStore::ServiceStore(std::filesystem::path root,
                           const security::DeviceIdentity &service_identity,
                           const security::Sodium &sodium)
    : root_(std::move(root)), service_identity_(&service_identity),
      sodium_(&sodium) {}

ServiceStore::~ServiceStore() {
    if (lock_descriptor_ >= 0) (void)::close(lock_descriptor_);
}

Result<std::unique_ptr<ServiceStore>> ServiceStore::open(
    std::filesystem::path root,
    const security::DeviceIdentity &service_identity,
    const security::Sodium &sodium) {
    struct stat metadata {};
    if (root.empty() || ::lstat(root.c_str(), &metadata) != 0 ||
        !S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & 0077U) != 0U ||
        service_identity.role() != security::SigningIdentityRole::witness) {
        return Status{ErrorCode::invalid_argument,
                      "witness service requires an owner-private root and a dedicated witness identity"};
    }
    const std::filesystem::path lock_path = root / ".service.lock";
    const int lock_descriptor = ::open(
        lock_path.c_str(), O_RDWR | O_CREAT | O_CLOEXEC | O_NOFOLLOW, 0600);
    if (lock_descriptor < 0 || ::fchmod(lock_descriptor, 0600) != 0 ||
        ::flock(lock_descriptor, LOCK_EX | LOCK_NB) != 0) {
        const int error = errno;
        if (lock_descriptor >= 0) (void)::close(lock_descriptor);
        return Status{ErrorCode::unavailable,
                      "witness service store is already active or cannot be locked: " +
                          std::string{std::strerror(error)}};
    }
    auto store = std::unique_ptr<ServiceStore>{
        new ServiceStore(std::move(root), service_identity, sodium)};
    store->lock_descriptor_ = lock_descriptor;
    return store;
}

std::filesystem::path ServiceStore::record_path(const Record &selector) const {
    return root_ /
        (security::hex(selector.domain) + "-" +
         security::hex(selector.device) + "-" +
         std::to_string(selector.witness_epoch) + "-" +
         std::to_string(static_cast<unsigned>(selector.lane)) + ".witness");
}

Result<Record> ServiceStore::load_path(const std::filesystem::path &path) const {
    const int descriptor =
        ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) {
        return Status{errno == ENOENT ? ErrorCode::not_found : ErrorCode::io_error,
                      "unable to open witness service record: " +
                          std::string{std::strerror(errno)}};
    }
    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0 || !S_ISREG(metadata.st_mode) ||
        metadata.st_uid != ::geteuid() || (metadata.st_mode & 0077U) != 0U ||
        metadata.st_nlink != 1 ||
        metadata.st_size != static_cast<off_t>(kStoreBytes)) {
        (void)::close(descriptor);
        return Status{ErrorCode::protocol_error,
                      "witness service record metadata is invalid"};
    }
    std::array<std::uint8_t, kStoreBytes> bytes{};
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(descriptor, bytes.data() + offset,
                                     bytes.size() - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            (void)::close(descriptor);
            return Status{ErrorCode::io_error,
                          "witness service record is truncated"};
        }
        offset += static_cast<std::size_t>(count);
    }
    if (::close(descriptor) != 0) {
        return Status{ErrorCode::io_error,
                      "unable to close witness service record"};
    }
    if (!std::equal(kStoreMagic.begin(), kStoreMagic.end(), bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "witness service stored record magic is invalid"};
    }
    security::Signature signature{};
    std::copy_n(bytes.begin() + 192U, signature.size(), signature.begin());
    const Status verified = sodium_->verify_detached(
        signature, std::span<const std::uint8_t>{bytes}.first<192U>(),
        service_identity_->public_key());
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "witness service stored record signature is invalid"};
    }
    auto record = decode_record(
        std::span<const std::uint8_t, kWireRecordBytes>{
            bytes.data() + 8U, kWireRecordBytes});
    if (!record || record_path(record.value()) != path) {
        return Status{ErrorCode::protocol_error,
                      "witness service stored record path or selector is invalid"};
    }
    return record;
}

Result<Record> ServiceStore::load(const Record &selector) const {
    auto record = load_path(record_path(selector));
    if (!record || !same_selector(record.value(), selector)) {
        return record ? Status{ErrorCode::protocol_error,
                               "witness service stored record selector is invalid"}
                      : record.status();
    }
    return record;
}

Result<std::vector<Record>> ServiceStore::snapshot() const {
    std::vector<Record> records;
    std::error_code error;
    std::filesystem::directory_iterator iterator{root_, error};
    if (error) {
        return Status{ErrorCode::io_error,
                      "unable to enumerate witness service store: " +
                          error.message()};
    }
    for (const auto &entry : iterator) {
        if (entry.path().extension() != ".witness") continue;
        if (records.size() == kMaximumServiceCheckpointRecords) {
            return Status{ErrorCode::resource_exhausted,
                          "witness service store exceeds checkpoint record limit"};
        }
        auto record = load_path(entry.path());
        if (!record) return record.status();
        records.push_back(std::move(record).value());
    }
    std::sort(records.begin(), records.end(), selector_less);
    for (std::size_t index = 1U; index < records.size(); ++index) {
        if (!selector_less(records[index - 1U], records[index])) {
            return Status{ErrorCode::protocol_error,
                          "witness service store contains duplicate selectors"};
        }
    }
    return records;
}

Status ServiceStore::write(const Record &record, bool no_replace) const {
    std::array<std::uint8_t, kStoreBytes> bytes{};
    std::copy(kStoreMagic.begin(), kStoreMagic.end(), bytes.begin());
    const Status encoded = encode_record(
        record, std::span<std::uint8_t, kWireRecordBytes>{
                    bytes.data() + 8U, kWireRecordBytes});
    if (!encoded.ok()) return encoded;
    auto signature = service_identity_->sign(
        std::span<const std::uint8_t>{bytes}.first<192U>());
    if (!signature) return signature.status();
    std::copy(signature.value().begin(), signature.value().end(),
              bytes.begin() + 192U);
    const std::filesystem::path path = record_path(record);
    if (!no_replace) return StateStore::write_atomic(path, bytes);

    std::array<std::uint8_t, 8U> suffix{};
    const Status random = security::fill_random(suffix);
    if (!random.ok()) return random;
    const std::filesystem::path temporary =
        root_ / (".enroll-" + security::hex(suffix));
    const Status staged = StateStore::write_atomic(temporary, bytes);
    if (!staged.ok()) return staged;
    if (::syscall(SYS_renameat2, AT_FDCWD, temporary.c_str(), AT_FDCWD,
                  path.c_str(), RENAME_NOREPLACE) != 0) {
        const int error = errno;
        (void)::unlink(temporary.c_str());
        return Status{error == EEXIST ? ErrorCode::invalid_argument
                                      : ErrorCode::io_error,
                      error == EEXIST
                          ? "witness service enrollment already exists"
                          : "unable to commit witness service enrollment: " +
                                std::string{std::strerror(error)}};
    }
    return sync_parent(root_);
}

Status ServiceStore::enroll(const Record &initial) {
    std::scoped_lock lock(mutex_);
    const Status valid = validate(initial);
    if (!valid.ok() || initial.pending) {
        return Status{ErrorCode::invalid_argument,
                      "witness service enrollment must be one committed record"};
    }
    return write(initial, true);
}

Result<std::vector<std::uint8_t>> ServiceStore::checkpoint() {
    std::scoped_lock lock(mutex_);
    auto records = snapshot();
    if (!records) return records.status();
    if (records.value().empty()) {
        return Status{ErrorCode::invalid_argument,
                      "witness service checkpoint requires at least one enrollment"};
    }
    std::vector<std::uint8_t> bytes(
        kServiceCheckpointHeaderBytes +
        records.value().size() * kWireRecordBytes +
        kServiceCheckpointSignatureBytes);
    std::copy(kCheckpointMagic.begin(), kCheckpointMagic.end(), bytes.begin());
    bytes[8U] = 1U;
    std::copy(service_identity_->public_key().begin(),
              service_identity_->public_key().end(), bytes.begin() + 16U);
    put_u64(std::span<std::uint8_t, 8U>{bytes.data() + 48U, 8U},
            records.value().size());
    std::size_t offset = kServiceCheckpointHeaderBytes;
    for (const Record &record : records.value()) {
        const Status encoded = encode_record(
            record, std::span<std::uint8_t, kWireRecordBytes>{
                        bytes.data() + offset, kWireRecordBytes});
        if (!encoded.ok()) return encoded;
        offset += kWireRecordBytes;
    }
    auto signature = service_identity_->sign(
        std::span<const std::uint8_t>{bytes}.first(offset));
    if (!signature) return signature.status();
    std::copy(signature.value().begin(), signature.value().end(),
              bytes.begin() + static_cast<std::ptrdiff_t>(offset));
    return bytes;
}

Status ServiceStore::require_checkpoint(
    std::span<const std::uint8_t> checkpoint_bytes) {
    std::scoped_lock lock(mutex_);
    auto checkpoint = verify_service_checkpoint(
        checkpoint_bytes, service_identity_->public_key(), *sodium_);
    if (!checkpoint) return checkpoint.status();
    auto records = snapshot();
    if (!records) return records.status();
    for (const Record &floor : checkpoint.value().records) {
        const auto current = std::lower_bound(
            records.value().begin(), records.value().end(), floor,
            selector_less);
        if (current == records.value().end() ||
            !same_selector(*current, floor)) {
            return Status{ErrorCode::protocol_error,
                          "witness service checkpoint enrollment is missing from the store"};
        }
        const Status descendant = require_descendant(*current, floor);
        if (!descendant.ok()) return descendant;
    }
    return Status::success();
}

Status ServiceStore::verify_all() {
    std::scoped_lock lock(mutex_);
    auto records = snapshot();
    return records ? Status::success() : records.status();
}

Result<ServiceResponseBytes> ServiceStore::process(
    std::span<const std::uint8_t, kServiceRequestBytes> request) {
    std::scoped_lock lock(mutex_);
    std::span<const std::uint8_t, 32U> nonce{
        request.data() + 16U, 32U};
    if (!std::equal(kRequestMagic.begin(), kRequestMagic.end(), request.begin()) ||
        !all_zero(request.subspan(9U, 7U)) || all_zero(nonce) ||
        (request[8U] != kOperationQuery &&
         request[8U] != kOperationCompareExchange)) {
        return make_response(kResponseInvalid, nonce, nullptr,
                             *service_identity_);
    }
    auto selector = decode_selector(
        std::span<const std::uint8_t, kSelectorBytes>{
            request.data() + 48U, kSelectorBytes});
    if (!selector) {
        return make_response(kResponseInvalid, nonce, nullptr,
                             *service_identity_);
    }
    security::Signature request_signature{};
    std::copy_n(request.begin() + 480U, request_signature.size(),
                request_signature.begin());
    const Status authenticated = sodium_->verify_detached(
        request_signature, request.first<480U>(), selector.value().device);
    if (!authenticated.ok()) {
        return make_response(kResponseInvalid, nonce, nullptr,
                             *service_identity_);
    }
    auto current = load(selector.value());
    if (!current && current.status().code() == ErrorCode::not_found) {
        return make_response(kResponseNotFound, nonce, nullptr,
                             *service_identity_);
    }
    if (!current) {
        return make_response(kResponseInternal, nonce, nullptr,
                             *service_identity_);
    }
    if (request[8U] == kOperationQuery) {
        if (!all_zero(request.subspan(112U, 368U))) {
            return make_response(kResponseInvalid, nonce, nullptr,
                                 *service_identity_);
        }
        return make_response(kResponseOk, nonce, &current.value(),
                             *service_identity_);
    }
    auto expected = decode_record(
        std::span<const std::uint8_t, kWireRecordBytes>{
            request.data() + 112U, kWireRecordBytes});
    auto desired = decode_record(
        std::span<const std::uint8_t, kWireRecordBytes>{
            request.data() + 296U, kWireRecordBytes});
    if (!expected || !desired ||
        !same_selector(selector.value(), expected.value()) ||
        !same_selector(selector.value(), desired.value()) ||
        !validate_transition(expected.value(), desired.value()).ok()) {
        return make_response(kResponseInvalid, nonce, nullptr,
                             *service_identity_);
    }
    if (!(current.value() == expected.value())) {
        return make_response(kResponseConflict, nonce, &current.value(),
                             *service_identity_);
    }
    const Status written = write(desired.value(), false);
    if (!written.ok()) {
        return make_response(kResponseInternal, nonce, nullptr,
                             *service_identity_);
    }
    return make_response(kResponseOk, nonce, &desired.value(),
                         *service_identity_);
}

TcpServiceServer::TcpServiceServer(int descriptor, std::uint16_t bound_port,
                                   ServiceEndpoint endpoint,
                                   ServiceStore &store)
    : descriptor_(descriptor), bound_port_(bound_port),
      endpoint_(std::move(endpoint)), store_(&store) {}

TcpServiceServer::~TcpServiceServer() {
    if (descriptor_ >= 0) (void)::close(descriptor_);
}

Result<std::unique_ptr<TcpServiceServer>> TcpServiceServer::listen(
    ServiceEndpoint endpoint, ServiceStore &store) {
    if (endpoint.service.empty() || endpoint.timeout.count() <= 0) {
        return Status{ErrorCode::invalid_argument,
                      "witness service listener endpoint is incomplete"};
    }
    struct addrinfo hints {};
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;
    hints.ai_flags = AI_PASSIVE;
    struct addrinfo *addresses = nullptr;
    const char *host = endpoint.host.empty() ? nullptr : endpoint.host.c_str();
    const int resolved = ::getaddrinfo(host, endpoint.service.c_str(), &hints,
                                       &addresses);
    if (resolved != 0) {
        return Status{ErrorCode::invalid_argument,
                      "unable to resolve witness listener: " +
                          std::string{::gai_strerror(resolved)}};
    }
    int listener = -1;
    std::uint16_t port = 0U;
    int final_error = EADDRNOTAVAIL;
    for (struct addrinfo *address = addresses; address != nullptr;
         address = address->ai_next) {
        const int candidate = ::socket(
            address->ai_family,
            address->ai_socktype | SOCK_CLOEXEC | SOCK_NONBLOCK,
            address->ai_protocol);
        if (candidate < 0) {
            final_error = errno;
            continue;
        }
        const int enabled = 1;
        (void)::setsockopt(candidate, SOL_SOCKET, SO_REUSEADDR, &enabled,
                           sizeof(enabled));
        if (::bind(candidate, address->ai_addr, address->ai_addrlen) == 0 &&
            ::listen(candidate, 16) == 0) {
            struct sockaddr_storage bound {};
            socklen_t bound_size = sizeof(bound);
            if (::getsockname(candidate,
                              reinterpret_cast<struct sockaddr *>(&bound),
                              &bound_size) == 0) {
                if (bound.ss_family == AF_INET) {
                    port = ntohs(reinterpret_cast<struct sockaddr_in *>(&bound)
                                     ->sin_port);
                } else if (bound.ss_family == AF_INET6) {
                    port = ntohs(reinterpret_cast<struct sockaddr_in6 *>(&bound)
                                     ->sin6_port);
                }
            }
            listener = candidate;
            break;
        }
        final_error = errno;
        (void)::close(candidate);
    }
    ::freeaddrinfo(addresses);
    if (listener < 0) {
        return socket_status("unable to bind witness service listener",
                             final_error);
    }
    return std::unique_ptr<TcpServiceServer>{new TcpServiceServer(
        listener, port, std::move(endpoint), store)};
}

Status TcpServiceServer::serve_one(std::chrono::milliseconds timeout) {
    const Status ready = wait_descriptor(descriptor_, POLLIN, timeout);
    if (!ready.ok()) return ready;
    const int client = ::accept4(descriptor_, nullptr, nullptr,
                                 SOCK_CLOEXEC | SOCK_NONBLOCK);
    if (client < 0) return socket_status("unable to accept witness client");
    ServiceRequestBytes request{};
    Status status = receive_all(client, request, endpoint_.timeout);
    if (!status.ok()) {
        // An accepted socket is untrusted input. A port probe, truncated
        // request, timeout, reset, or early close must consume only this
        // bounded connection and can never stop the witness service.
        (void)::close(client);
        return Status::success();
    }
    auto response = store_->process(request);
    if (!response) {
        (void)::close(client);
        return response.status();
    }
    // A peer may disappear after committing a valid request. The signed CAS
    // protocol resolves that ambiguity by query; reply delivery is not a
    // service-liveness condition.
    (void)send_all(client, response.value(), endpoint_.timeout);
    (void)::close(client);
    return Status::success();
}

Status TcpServiceServer::serve_until(
    const std::function<bool()> &stop_requested) {
    while (!stop_requested()) {
        const Status served = serve_one(std::chrono::milliseconds{100});
        if (!served.ok() && served.code() != ErrorCode::timeout) return served;
    }
    return Status::success();
}

}  // namespace iotox::rollback_witness
