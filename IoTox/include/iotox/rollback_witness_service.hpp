#pragma once

#include "iotox/rollback_witness.hpp"
#include "iotox/security/identity.hpp"

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <memory>
#include <mutex>
#include <span>
#include <string>
#include <vector>

namespace iotox::rollback_witness {

inline constexpr std::size_t kWireRecordBytes = 184U;
inline constexpr std::size_t kServiceRequestBytes = 544U;
inline constexpr std::size_t kServiceResponseBytes = 296U;
inline constexpr std::size_t kEnrollmentBytes = 176U;
inline constexpr std::size_t kServiceCheckpointHeaderBytes = 64U;
inline constexpr std::size_t kServiceCheckpointSignatureBytes =
    security::kSignatureBytes;
inline constexpr std::size_t kMaximumServiceCheckpointRecords = 4096U;

using ServiceRequestBytes = std::array<std::uint8_t, kServiceRequestBytes>;
using ServiceResponseBytes = std::array<std::uint8_t, kServiceResponseBytes>;
using EnrollmentBytes = std::array<std::uint8_t, kEnrollmentBytes>;

struct ServiceCheckpoint {
    security::SigningPublicKey service_key{};
    std::vector<Record> records;
};

[[nodiscard]] Result<EnrollmentBytes> create_enrollment(
    const Record &committed,
    const security::DeviceIdentity &device_identity);
[[nodiscard]] Result<Record> verify_enrollment(
    std::span<const std::uint8_t, kEnrollmentBytes> enrollment,
    const security::Sodium &sodium);
[[nodiscard]] Result<ServiceCheckpoint> verify_service_checkpoint(
    std::span<const std::uint8_t> checkpoint,
    const security::SigningPublicKey &expected_service_key,
    const security::Sodium &sodium);

struct ServiceEndpoint {
    std::string host;
    std::string service;
    std::chrono::milliseconds timeout{3000};
};

struct RemoteBackendConfig {
    ServiceEndpoint endpoint;
    security::SigningPublicKey service_key{};
    DomainId domain{};
    std::uint64_t witness_epoch{0U};
    Lane lane{Lane::authority};
};

// The remote-service backend provides cryptographic separation from the
// Agent. Operational independence still requires deploying the service in a
// different administration/storage failure domain; a same-host instance is
// only a protocol test.
class RemoteBackend final : public Backend {
  public:
    [[nodiscard]] static Result<std::shared_ptr<RemoteBackend>> create(
        RemoteBackendConfig config,
        const security::DeviceIdentity &device_identity,
        const security::Sodium &sodium);

    [[nodiscard]] Result<Record> query() override;
    [[nodiscard]] Status compare_exchange(const Record &expected,
                                          const Record &desired) override;
    [[nodiscard]] bool independently_controlled() const noexcept override {
        return true;
    }

  private:
    RemoteBackend(RemoteBackendConfig config,
                  const security::DeviceIdentity &device_identity,
                  const security::Sodium &sodium);
    [[nodiscard]] Result<ServiceResponseBytes> exchange(
        std::uint8_t operation, const Record *expected,
        const Record *desired);

    RemoteBackendConfig config_;
    const security::DeviceIdentity *device_identity_{nullptr};
    const security::Sodium *sodium_{nullptr};
};

// A separately deployable, single-writer durable service store. Enrollment is
// explicit and no-replace. The service key signs both storage records and
// nonce-bound replies; device signatures authorize query/CAS requests.
class ServiceStore {
  public:
    ~ServiceStore();
    [[nodiscard]] static Result<std::unique_ptr<ServiceStore>> open(
        std::filesystem::path root,
        const security::DeviceIdentity &service_identity,
        const security::Sodium &sodium);
    [[nodiscard]] Status enroll(const Record &initial);
    // A checkpoint is a service-signed, selector-complete snapshot. Retaining
    // it outside this store and requiring it at restart turns it into a
    // rollback floor; a copy beside the store is only an integrity artifact.
    [[nodiscard]] Result<std::vector<std::uint8_t>> checkpoint();
    [[nodiscard]] Status require_checkpoint(
        std::span<const std::uint8_t> checkpoint);
    [[nodiscard]] Status verify_all();
    [[nodiscard]] Result<ServiceResponseBytes> process(
        std::span<const std::uint8_t, kServiceRequestBytes> request);

  private:
    ServiceStore(std::filesystem::path root,
                 const security::DeviceIdentity &service_identity,
                 const security::Sodium &sodium);
    [[nodiscard]] std::filesystem::path record_path(const Record &selector) const;
    [[nodiscard]] Result<Record> load_path(
        const std::filesystem::path &path) const;
    [[nodiscard]] Result<Record> load(const Record &selector) const;
    [[nodiscard]] Result<std::vector<Record>> snapshot() const;
    [[nodiscard]] Status write(const Record &record, bool no_replace) const;

    std::filesystem::path root_;
    const security::DeviceIdentity *service_identity_{nullptr};
    const security::Sodium *sodium_{nullptr};
    int lock_descriptor_{-1};
    std::mutex mutex_;
};

class TcpServiceServer {
  public:
    ~TcpServiceServer();
    TcpServiceServer(const TcpServiceServer &) = delete;
    TcpServiceServer &operator=(const TcpServiceServer &) = delete;

    [[nodiscard]] static Result<std::unique_ptr<TcpServiceServer>> listen(
        ServiceEndpoint endpoint, ServiceStore &store);
    [[nodiscard]] std::uint16_t bound_port() const noexcept { return bound_port_; }
    [[nodiscard]] Status serve_one(std::chrono::milliseconds timeout);
    [[nodiscard]] Status serve_until(
        const std::function<bool()> &stop_requested);

  private:
    TcpServiceServer(int descriptor, std::uint16_t bound_port,
                     ServiceEndpoint endpoint, ServiceStore &store);

    int descriptor_{-1};
    std::uint16_t bound_port_{0U};
    ServiceEndpoint endpoint_;
    ServiceStore *store_{nullptr};
};

}  // namespace iotox::rollback_witness
