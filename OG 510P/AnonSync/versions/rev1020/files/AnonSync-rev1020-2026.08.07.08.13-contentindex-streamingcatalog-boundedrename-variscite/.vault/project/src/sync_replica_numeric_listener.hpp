#pragma once

#if !defined(_WIN32)

#include "sync_replica_file_tls_server.hpp"
#include "sync_replica_stream_connector.hpp"

#include <memory>
#include <string>

namespace anonsync {

// Owns one exact numeric nonblocking+CLOEXEC listening socket and the
// process/thread-bound capability required by the TLS accepted-session owner.
// Construction performs numeric-address validation, socket policy, bind,
// listen, and capability observation as one fail-closed operation. The owner
// must be constructed and used on the same thread; it never resolves names.
class SyncReplicaNumericListener final {
public:
    explicit SyncReplicaNumericListener(
        SyncReplicaNumericStreamEndpoint endpoint,
        std::string label = "sync replica numeric listener");
    ~SyncReplicaNumericListener() noexcept;

    SyncReplicaNumericListener(const SyncReplicaNumericListener&) = delete;
    SyncReplicaNumericListener& operator=(
        const SyncReplicaNumericListener&) = delete;
    SyncReplicaNumericListener(SyncReplicaNumericListener&&) = delete;
    SyncReplicaNumericListener& operator=(
        SyncReplicaNumericListener&&) = delete;

    [[nodiscard]] const SyncReplicaNumericStreamEndpoint& endpoint()
        const noexcept {
        return endpoint_;
    }
    [[nodiscard]] int descriptor() const noexcept { return descriptor_; }
    [[nodiscard]] SyncReplicaFileTlsServerListener& listener_or_throw();

private:
    void close_noexcept() noexcept;

    SyncReplicaNumericStreamEndpoint endpoint_;
    std::string label_;
    int descriptor_ = -1;
    std::unique_ptr<SyncReplicaFileTlsServerListener> listener_;
};

}  // namespace anonsync

#endif
