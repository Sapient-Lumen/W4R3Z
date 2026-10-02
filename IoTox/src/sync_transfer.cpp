#include "iotox/sync_transfer.hpp"

#include <algorithm>
#include <limits>
#include <utility>

namespace iotox::sync {

SyncTransferCoordinator::SyncTransferCoordinator(
    SyncObjectScheduler &scheduler, Config config)
    : scheduler_(&scheduler), config_(std::move(config)) {}

SyncTransferCoordinator::~SyncTransferCoordinator() noexcept {
  try {
    (void)close();
  } catch (...) {
  }
}

Status SyncTransferCoordinator::validate_config() const {
  const Status policy = validate_namespace_policy(config_.policy);
  if (!policy.ok()) return policy;
  const bool any_persistence = config_.attempt_store != nullptr ||
                               config_.identity != nullptr ||
                               config_.sodium != nullptr;
  const bool complete_persistence = config_.attempt_store != nullptr &&
                                    config_.identity != nullptr &&
                                    config_.sodium != nullptr;
  if (scheduler_ == nullptr || config_.maximum_bindings == 0U ||
      config_.maximum_bindings > 65536U ||
      config_.maximum_events_per_service == 0U ||
      config_.maximum_events_per_service > config_.maximum_bindings ||
      config_.copy_chunk_bytes == 0U ||
      config_.copy_chunk_bytes > 1024U * 1024U ||
      !config_.seams.receive_to_path || !config_.seams.cancel_transfer ||
      !config_.seams.retire_transfer ||
      !config_.seams.install.hash_file ||
      (any_persistence && !complete_persistence)) {
    return Status{ErrorCode::invalid_argument,
                  "sync transfer coordinator configuration is invalid"};
  }
  return Status::success();
}

DurableSyncAttempt SyncTransferCoordinator::durable_attempt(
    const SyncTransferBindingSnapshot &binding) const {
  return DurableSyncAttempt{binding.attempt_id, binding.object,
                            binding.route_key, binding.worker_id};
}

Result<TransferAttemptSnapshot>
SyncTransferCoordinator::active_attempt(std::uint64_t attempt_id) const {
  const SyncSchedulerSnapshot state = scheduler_->snapshot();
  const auto found = std::find_if(
      state.attempts.begin(), state.attempts.end(),
      [attempt_id](const TransferAttemptSnapshot &attempt) {
        return attempt.attempt_id == attempt_id;
      });
  if (found == state.attempts.end()) {
    return Status{ErrorCode::not_found,
                  "sync transfer attempt is not retained"};
  }
  if (found->state != TransferAttemptState::active ||
      !found->route_capacity_reserved ||
      !found->staging_bytes_reserved) {
    return Status{ErrorCode::unavailable,
                  "sync transfer attempt is not active and reserved"};
  }
  return *found;
}

Result<SyncTransferBindingSnapshot>
SyncTransferCoordinator::accept_offer(std::uint64_t attempt_id,
                                      std::uint32_t file_number) {
  const Status valid = validate_config();
  if (!valid.ok()) return valid;
  if (closed_) {
    return Status{ErrorCode::unavailable,
                  "sync transfer coordinator is closed"};
  }
  auto attempt = active_attempt(attempt_id);
  if (!attempt) return attempt.status();
  const auto same_attempt = std::find_if(
      bindings_.begin(), bindings_.end(),
      [attempt_id](const BindingState &state) {
        return state.binding.attempt_id == attempt_id;
      });
  if (same_attempt != bindings_.end()) {
    return same_attempt->binding.file_number == file_number
               ? Result<SyncTransferBindingSnapshot>(same_attempt->binding)
               : Result<SyncTransferBindingSnapshot>(Status{
                     ErrorCode::protocol_error,
                     "sync attempt is already bound to another file number"});
  }
  const auto same_file = std::find_if(
      bindings_.begin(), bindings_.end(),
      [&attempt, file_number](const BindingState &state) {
        return state.binding.route_key == attempt.value().route_key &&
               state.binding.worker_id == attempt.value().worker_id &&
               state.binding.file_number == file_number;
      });
  if (same_file != bindings_.end()) {
    return Status{ErrorCode::protocol_error,
                  "worker file number is already bound to another attempt"};
  }
  const auto retained = std::find_if(
      retained_partials_.begin(), retained_partials_.end(),
      [&attempt](const RetainedPartialState &state) {
        return state.binding.object == attempt.value().object;
      });
  const bool resume_retained =
      retained != retained_partials_.end() &&
      static_cast<bool>(config_.seams.receive_to_path_from_offset);
  if (!resume_retained &&
      bindings_.size() + retained_partials_.size() >=
          config_.maximum_bindings) {
    return Status{ErrorCode::resource_exhausted,
                  "sync transfer binding bound is exhausted"};
  }

  auto transaction = SyncNamespaceTransaction::acquire(config_.policy);
  if (!transaction) return transaction.status();
  const bool retained_partial_receive =
      static_cast<bool>(config_.seams.receive_to_path_from_offset);
  std::filesystem::path staging_path;
  std::uint64_t resume_offset = 0U;
  bool restart_resumed = false;
  std::optional<std::size_t> consumed_retained_index;
  if (resume_retained) {
    const std::size_t retained_index = static_cast<std::size_t>(
        retained - retained_partials_.begin());
    if (config_.attempt_store != nullptr) {
      auto finished = config_.attempt_store->finish(
          config_.policy, durable_attempt(retained->binding),
          *config_.identity, *config_.sodium, transaction.value());
      if (!finished) return finished.status();
    }
    auto partial = handoff_sync_attempt_partial(
        config_.policy, retained->binding.attempt_id, attempt_id,
        attempt.value().object, transaction.value());
    if (!partial) return partial.status();
    if (partial.value().bytes != retained->bytes) {
      return Status{ErrorCode::protocol_error,
                    "sync retained prefix size changed before handoff"};
    }
    staging_path = partial.value().path;
    resume_offset = partial.value().bytes;
    consumed_retained_index = retained_index;
  } else if (retained_partial_receive) {
    std::optional<DurableSyncAttempt> restart_partial;
    if (config_.attempt_store != nullptr) {
      auto durable_retained = config_.attempt_store->retained_attempt(
          config_.policy, attempt.value().object,
          config_.identity->public_key(), *config_.sodium,
          transaction.value());
      if (!durable_retained) return durable_retained.status();
      restart_partial = durable_retained.value();
    }
    if (restart_partial) {
      auto partial = inspect_sync_attempt_partial(
          config_.policy, restart_partial->attempt_id,
          restart_partial->object, transaction.value());
      if (!partial || partial.value().bytes == 0U) {
        const Status discarded = discard_sync_attempt_staging(
            config_.policy, restart_partial->attempt_id,
            transaction.value());
        if (!discarded.ok()) return discarded;
        auto finished = config_.attempt_store->finish(
            config_.policy, *restart_partial, *config_.identity,
            *config_.sodium, transaction.value());
        if (!finished) return finished.status();
        if (!finished.value()) {
          return Status{ErrorCode::protocol_error,
                        "restart-retained sync attempt disappeared during fencing"};
        }
      } else {
        auto finished = config_.attempt_store->finish(
            config_.policy, *restart_partial, *config_.identity,
            *config_.sodium, transaction.value());
        if (!finished) return finished.status();
        if (!finished.value()) {
          return Status{ErrorCode::protocol_error,
                        "restart-retained sync attempt disappeared during handoff"};
        }
        auto handed = handoff_sync_attempt_partial(
            config_.policy, restart_partial->attempt_id, attempt_id,
            attempt.value().object, transaction.value());
        if (!handed) {
          const Status prior_discarded = discard_sync_attempt_staging(
              config_.policy, restart_partial->attempt_id,
              transaction.value());
          const Status next_discarded = discard_sync_attempt_staging(
              config_.policy, attempt_id, transaction.value());
          if (!prior_discarded.ok()) return prior_discarded;
          return next_discarded.ok() ? handed.status() : next_discarded;
        }
        staging_path = handed.value().path;
        resume_offset = handed.value().bytes;
        restart_resumed = true;
      }
    }
    if (!restart_resumed) {
      auto partial = create_sync_attempt_partial(
          config_.policy, attempt_id, attempt.value().object,
          transaction.value());
      if (!partial) return partial.status();
      staging_path = partial.value().path;
    }
  } else {
    auto staging = prepare_sync_attempt_staging(
        config_.policy, attempt_id, attempt.value().object,
        transaction.value());
    if (!staging) return staging.status();
    staging_path = staging.value();
  }

  SyncTransferBindingSnapshot binding;
  binding.attempt_id = attempt_id;
  binding.object = attempt.value().object;
  binding.route_key = attempt.value().route_key;
  binding.worker_id = attempt.value().worker_id;
  binding.file_number = file_number;
  binding.staging_path = staging_path;
  binding.resume_offset = resume_offset;
  bindings_.push_back(BindingState{binding, std::nullopt});
  if (config_.attempt_store != nullptr) {
    auto begun = config_.attempt_store->begin(
        config_.policy, durable_attempt(binding), *config_.identity,
        *config_.sodium, transaction.value());
    if (!begun) {
      if (retained_partial_receive) {
        const Status discarded = discard_sync_attempt_staging(
            config_.policy, attempt_id, transaction.value());
        if (!discarded.ok()) return discarded;
      }
      if (consumed_retained_index) {
        retained_partials_.erase(
            retained_partials_.begin() +
            static_cast<std::ptrdiff_t>(*consumed_retained_index));
      }
      bindings_.pop_back();
      return begun.status();
    }
  }
  if (consumed_retained_index) {
    retained_partials_.erase(
        retained_partials_.begin() +
        static_cast<std::ptrdiff_t>(*consumed_retained_index));
  }
  SyncTransferBindingSnapshot response = binding;
  response.admitted = true;
  auto accepted = retained_partial_receive
      ? config_.seams.receive_to_path_from_offset(
            binding.route_key, binding.worker_id, file_number,
            binding.staging_path, binding.resume_offset)
      : config_.seams.receive_to_path(
            binding.route_key, binding.worker_id, file_number,
            binding.staging_path);
  if (!accepted) {
    const Status failure = accepted.status();
    const Status discarded = discard_sync_attempt_staging(
        config_.policy, attempt_id, transaction.value());
    if (!discarded.ok()) return discarded;
    if (config_.attempt_store != nullptr) {
      auto finished = config_.attempt_store->finish(
          config_.policy, durable_attempt(binding), *config_.identity,
          *config_.sodium, transaction.value());
      if (!finished) return finished.status();
    }
    // A full Agent receive ledger is an admission deferral, not an
    // immutable-object failure. Undo only provisional staging/journal state
    // and retain the exact scheduler attempt for the same FileId/file number.
    if (failure.code() == ErrorCode::resource_exhausted) {
      bindings_.pop_back();
      if (deferred_offers_ != std::numeric_limits<std::uint64_t>::max())
        ++deferred_offers_;
      return failure;
    }
    const Status fenced = scheduler_->fence_attempt(attempt_id);
    if (!fenced.ok()) return fenced;
    bindings_.pop_back();
    ++failed_attempts_;
    return failure;
  }
  bindings_.back().binding.admitted = true;
  if (accepted.value().direction != FileTransferDirection::incoming ||
      accepted.value().file_number != file_number ||
      accepted.value().file_size != binding.object.bytes ||
      accepted.value().position != binding.resume_offset ||
      accepted.value().local_path != binding.staging_path) {
    const Status cancelled = config_.seams.cancel_transfer(
        binding.route_key, binding.worker_id, file_number);
    if (!cancelled.ok()) return cancelled;
    const Status discarded = discard_sync_attempt_staging(
        config_.policy, attempt_id, transaction.value());
    if (!discarded.ok()) return discarded;
    if (config_.attempt_store != nullptr) {
      auto finished = config_.attempt_store->finish(
          config_.policy, durable_attempt(binding), *config_.identity,
          *config_.sodium, transaction.value());
      if (!finished) return finished.status();
    }
    const Status fenced = scheduler_->fence_attempt(attempt_id);
    if (!fenced.ok()) return fenced;
    bindings_.pop_back();
    ++failed_attempts_;
    return Status{ErrorCode::protocol_error,
                  "worker accepted record conflicts with immutable object attempt"};
  }
  if (binding.resume_offset != 0U) {
    if (resumed_attempts_ != std::numeric_limits<std::uint64_t>::max())
      ++resumed_attempts_;
    resumed_bytes_ = binding.resume_offset >
            std::numeric_limits<std::uint64_t>::max() - resumed_bytes_
        ? std::numeric_limits<std::uint64_t>::max()
        : resumed_bytes_ + binding.resume_offset;
    if (restart_resumed) {
      if (restart_resumed_attempts_ !=
          std::numeric_limits<std::uint64_t>::max()) {
        ++restart_resumed_attempts_;
      }
      restart_resumed_bytes_ = binding.resume_offset >
              std::numeric_limits<std::uint64_t>::max() -
                  restart_resumed_bytes_
          ? std::numeric_limits<std::uint64_t>::max()
          : restart_resumed_bytes_ + binding.resume_offset;
    }
  }
  ++accepted_offers_;
  return response;
}

Status SyncTransferCoordinator::fail_binding(std::size_t index,
                                             bool cancel_transport) {
  if (index >= bindings_.size()) {
    return Status{ErrorCode::internal_error,
                  "sync transfer binding index is invalid"};
  }
  const SyncTransferBindingSnapshot binding = bindings_[index].binding;
  Status cancellation = Status::success();
  if (binding.admitted) {
    cancellation = cancel_transport
        ? config_.seams.cancel_transfer(
              binding.route_key, binding.worker_id, binding.file_number)
        : config_.seams.retire_transfer(
              binding.route_key, binding.worker_id, binding.file_number);
    // Either seam removes local transfer state. Never repeat that effect, and
    // do not let its status prevent local staging/journal cleanup and fencing.
    bindings_[index].binding.admitted = false;
  }
  auto transaction = SyncNamespaceTransaction::acquire(config_.policy);
  if (!transaction) return transaction.status();
  const Status discarded = discard_sync_attempt_staging(
      config_.policy, binding.attempt_id, transaction.value());
  if (!discarded.ok()) return discarded;
  if (config_.attempt_store != nullptr) {
    auto finished = config_.attempt_store->finish(
        config_.policy, durable_attempt(binding), *config_.identity,
        *config_.sodium, transaction.value());
    if (!finished) return finished.status();
  }
  const Status fenced = scheduler_->fence_attempt(binding.attempt_id);
  if (!fenced.ok()) return fenced;
  bindings_.erase(bindings_.begin() + static_cast<std::ptrdiff_t>(index));
  ++failed_attempts_;
  return cancellation;
}

Status SyncTransferCoordinator::retain_binding(std::size_t index,
                                               bool cancel_transport) {
  if (index >= bindings_.size()) {
    return Status{ErrorCode::internal_error,
                  "sync transfer binding index is invalid"};
  }
  if (!config_.seams.receive_to_path_from_offset ||
      retained_partials_.size() >= config_.maximum_bindings) {
    return fail_binding(index, cancel_transport);
  }
  const SyncTransferBindingSnapshot binding = bindings_[index].binding;
  if (std::any_of(
          retained_partials_.begin(), retained_partials_.end(),
          [&binding](const RetainedPartialState &state) {
            return state.binding.object == binding.object;
          })) {
    return Status{ErrorCode::protocol_error,
                  "sync object already owns a retained partial"};
  }
  Status cancellation = Status::success();
  if (binding.admitted) {
    cancellation = cancel_transport
        ? config_.seams.cancel_transfer(
              binding.route_key, binding.worker_id, binding.file_number)
        : config_.seams.retire_transfer(
              binding.route_key, binding.worker_id, binding.file_number);
    bindings_[index].binding.admitted = false;
  }
  auto partial = [&]() -> Result<SyncAttemptPartial> {
    auto transaction = SyncNamespaceTransaction::acquire(config_.policy);
    if (!transaction) return transaction.status();
    return inspect_sync_attempt_partial(
        config_.policy, binding.attempt_id, binding.object,
        transaction.value());
  }();
  if (!partial) {
    if (retention_fallbacks_ != std::numeric_limits<std::uint64_t>::max())
      ++retention_fallbacks_;
    const Status discarded = fail_binding(index, false);
    return discarded.ok() ? cancellation : discarded;
  }
  if (partial.value().bytes == 0U) {
    return fail_binding(index, false);
  }
  const Status fenced = scheduler_->fence_attempt(binding.attempt_id);
  if (!fenced.ok()) return fenced;
  retained_partials_.push_back(
      RetainedPartialState{binding, partial.value().bytes});
  if (retained_attempts_ != std::numeric_limits<std::uint64_t>::max())
    ++retained_attempts_;
  retained_bytes_ = partial.value().bytes >
          std::numeric_limits<std::uint64_t>::max() - retained_bytes_
      ? std::numeric_limits<std::uint64_t>::max()
      : retained_bytes_ + partial.value().bytes;
  bindings_.erase(bindings_.begin() + static_cast<std::ptrdiff_t>(index));
  ++failed_attempts_;
  return cancellation;
}

Status SyncTransferCoordinator::discard_retained_partial(
    std::size_t index) {
  if (index >= retained_partials_.size()) {
    return Status{ErrorCode::internal_error,
                  "sync retained partial index is invalid"};
  }
  const SyncTransferBindingSnapshot binding =
      retained_partials_[index].binding;
  auto transaction = SyncNamespaceTransaction::acquire(config_.policy);
  if (!transaction) return transaction.status();
  const Status discarded = discard_sync_attempt_staging(
      config_.policy, binding.attempt_id, transaction.value());
  if (!discarded.ok()) return discarded;
  if (config_.attempt_store != nullptr) {
    auto finished = config_.attempt_store->finish(
        config_.policy, durable_attempt(binding), *config_.identity,
        *config_.sodium, transaction.value());
    if (!finished) return finished.status();
  }
  retained_partials_.erase(
      retained_partials_.begin() + static_cast<std::ptrdiff_t>(index));
  return Status::success();
}

Status SyncTransferCoordinator::apply_pending(std::size_t index) {
  if (index >= bindings_.size() || !bindings_[index].terminal) {
    return Status{ErrorCode::internal_error,
                  "sync transfer has no retained terminal event"};
  }
  const SyncTransferBindingSnapshot binding = bindings_[index].binding;
  const routes::WorkerTransferTerminalEvent &event =
      *bindings_[index].terminal;
  auto live_attempt = active_attempt(binding.attempt_id);
  if (!live_attempt) {
    const Status stale = live_attempt.status();
    const Status cleaned = fail_binding(index, false);
    return cleaned.ok() ? stale : cleaned;
  }
  if (event.outcome != routes::WorkerTransferOutcome::completed ||
      event.failure != ErrorCode::ok ||
      event.transfer.direction != FileTransferDirection::incoming ||
      event.transfer.file_size != binding.object.bytes ||
      event.transfer.local_path != binding.staging_path) {
    return fail_binding(index, false);
  }

  Status object_commit = Status::success();
  {
    auto transaction = SyncNamespaceTransaction::acquire(config_.policy);
    if (!transaction) {
      object_commit = transaction.status();
    } else {
      const Status existing = verify_sync_object(
          config_.policy, binding.object, transaction.value(),
          config_.seams.install);
      if (existing.ok()) {
        object_commit = discard_sync_attempt_staging(
            config_.policy, binding.attempt_id, transaction.value());
      } else if (existing.code() == ErrorCode::not_found) {
        auto committed = commit_sync_attempt_staging(
            config_.policy, binding.attempt_id, binding.object,
            transaction.value(), config_.seams.install,
            config_.copy_chunk_bytes);
        if (!committed) object_commit = committed.status();
      } else {
        object_commit = existing;
      }
      if (object_commit.ok() && config_.attempt_store != nullptr) {
        auto finished = config_.attempt_store->finish(
            config_.policy, durable_attempt(binding), *config_.identity,
            *config_.sodium, transaction.value());
        if (!finished) object_commit = finished.status();
      }
    }
  }
  if (!object_commit.ok()) {
    if (object_commit.code() == ErrorCode::protocol_error ||
        object_commit.code() == ErrorCode::not_found) {
      const Status cleaned = fail_binding(index, false);
      if (!cleaned.ok()) return cleaned;
    }
    return object_commit;
  }
  const Status verified = scheduler_->complete(
      binding.attempt_id, binding.object.identity, binding.object.bytes);
  if (!verified.ok()) {
    const Status failure = verified;
    const Status cleaned = fail_binding(index, false);
    return cleaned.ok() ? failure : cleaned;
  }
  const Status finalized = scheduler_->commit(binding.attempt_id);
  if (!finalized.ok()) {
    const Status failure = finalized;
    const Status cleaned = fail_binding(index, false);
    return cleaned.ok() ? failure : cleaned;
  }
  bindings_.erase(bindings_.begin() + static_cast<std::ptrdiff_t>(index));
  ++committed_objects_;
  return Status::success();
}

Status SyncTransferCoordinator::service() {
  const Status valid = validate_config();
  if (!valid.ok()) return valid;
  if (!config_.seams.take_terminal_events) {
    return Status{ErrorCode::invalid_argument,
                  "sync transfer service has no terminal-event drain"};
  }
  Status first = Status::success();
  std::size_t index = 0U;
  while (index < bindings_.size()) {
    if (!bindings_[index].terminal) {
      ++index;
      continue;
    }
    const std::size_t before = bindings_.size();
    const Status applied = apply_pending(index);
    if (!applied.ok() && first.ok()) first = applied;
    if (bindings_.size() == before) ++index;
  }
  auto events = config_.seams.take_terminal_events(
      config_.maximum_events_per_service);
  if (!events) return first.ok() ? events.status() : first;
  for (auto &event : events.value()) {
    const Status applied = handle_terminal(std::move(event));
    if (!applied.ok() && first.ok()) first = applied;
  }
  return first;
}

Status SyncTransferCoordinator::handle_terminal(
    routes::WorkerTransferTerminalEvent event) {
  const Status valid = validate_config();
  if (!valid.ok()) return valid;
  if (closed_) {
    return Status{ErrorCode::unavailable,
                  "sync transfer coordinator is closed"};
  }
  const auto found = std::find_if(
      bindings_.begin(), bindings_.end(),
      [&event](const BindingState &state) {
        return state.binding.route_key == event.route_key &&
               state.binding.worker_id == event.worker_id &&
               state.binding.file_number == event.transfer.file_number;
      });
  if (found == bindings_.end()) {
    ++stale_terminal_events_;
    return Status::success();
  }
  const std::size_t index =
      static_cast<std::size_t>(found - bindings_.begin());
  if (found->terminal) {
    if (*found->terminal != event) {
      return Status{ErrorCode::protocol_error,
                    "sync transfer received conflicting terminal truth"};
    }
  } else {
    found->terminal.emplace(std::move(event));
  }
  return apply_pending(index);
}

Result<std::size_t> SyncTransferCoordinator::fence_route(
    const routes::ToxPublicKey &route_key, std::uint64_t worker_id,
    bool cancel_transport, bool retain_incomplete_partials) {
  const Status valid = validate_config();
  if (!valid.ok()) return valid;
  if (closed_) {
    return Status{ErrorCode::unavailable,
                  "sync transfer coordinator is closed"};
  }
  std::size_t fenced = 0U;
  for (std::size_t index = bindings_.size(); index > 0U; --index) {
    const BindingState &state = bindings_[index - 1U];
    if (state.binding.route_key != route_key ||
        state.binding.worker_id != worker_id) {
      continue;
    }
    const Status closed = retain_incomplete_partials
        ? retain_binding(index - 1U, cancel_transport)
        : fail_binding(index - 1U, cancel_transport);
    if (!closed.ok()) return closed;
    ++fenced;
  }
  auto remaining = scheduler_->fence_route(route_key, worker_id);
  if (!remaining) return remaining.status();
  if (remaining.value() >
      std::numeric_limits<std::size_t>::max() - fenced) {
    return Status{ErrorCode::resource_exhausted,
                  "sync route fence count overflow"};
  }
  return fenced + remaining.value();
}

Status SyncTransferCoordinator::close() {
  if (closed_) return Status::success();
  Status first = Status::success();
  for (std::size_t index = bindings_.size(); index > 0U; --index) {
    const bool cancel_transport = !bindings_[index - 1U].terminal.has_value();
    const Status failed = fail_binding(index - 1U, cancel_transport);
    if (!failed.ok() && first.ok()) first = failed;
  }
  for (std::size_t index = retained_partials_.size(); index > 0U; --index) {
    const Status discarded = discard_retained_partial(index - 1U);
    if (!discarded.ok() && first.ok()) first = discarded;
  }
  closed_ = bindings_.empty() && retained_partials_.empty();
  if (!closed_ && first.ok()) {
    first = Status{ErrorCode::unavailable,
                   "sync transfer coordinator retained unfinished work"};
  }
  return first;
}

SyncTransferCoordinatorSnapshot SyncTransferCoordinator::snapshot() const {
  SyncTransferCoordinatorSnapshot result;
  result.bindings.reserve(bindings_.size());
  for (const BindingState &state : bindings_) {
    result.bindings.push_back(state.binding);
  }
  result.accepted_offers = accepted_offers_;
  result.deferred_offers = deferred_offers_;
  result.committed_objects = committed_objects_;
  result.failed_attempts = failed_attempts_;
  result.stale_terminal_events = stale_terminal_events_;
  result.retained_partials = retained_partials_.size();
  result.retained_attempts = retained_attempts_;
  result.retained_bytes = retained_bytes_;
  result.retention_fallbacks = retention_fallbacks_;
  result.resumed_attempts = resumed_attempts_;
  result.resumed_bytes = resumed_bytes_;
  result.restart_resumed_attempts = restart_resumed_attempts_;
  result.restart_resumed_bytes = restart_resumed_bytes_;
  result.closed = closed_;
  return result;
}

} // namespace iotox::sync
