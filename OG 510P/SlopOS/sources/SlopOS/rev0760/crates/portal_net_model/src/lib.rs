#![forbid(unsafe_code)]
//! Minimal executable model seed for the `portal.net.request` proof slice.
//!
//! The crate is intentionally tiny: it gives the archive a buildable transition
//! relation for exact replay, changed replay rejection, domain conflict denial,
//! accepted-only durability, prefix rollback, and receipt-chain verification. It
//! does not model DNS,
//! transport profiles, TLS, proxy policy, authorization languages, or real
//! cryptographic hashing.

use std::collections::BTreeMap;

#[derive(Clone, Debug, Eq, PartialEq, Ord, PartialOrd)]
pub struct RequestId(String);

#[derive(Clone, Debug, Eq, PartialEq, Ord, PartialOrd)]
pub struct DomainId(String);

#[derive(Clone, Debug, Eq, PartialEq, Ord, PartialOrd)]
pub struct Subject(String);

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct NetRequest {
    pub req_id: RequestId,
    pub subject: Subject,
    pub domain: DomainId,
    pub operation: Operation,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Operation {
    Connect,
    ListenLocal,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Admission {
    Allow,
    Deny(&'static str),
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Outcome {
    Accepted {
        lease_id: String,
        commit_index: u64,
    },
    Replayed {
        lease_id: String,
        original_commit_index: u64,
    },
    Denied(&'static str),
    Rejected(&'static str),
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Lease {
    pub lease_id: String,
    pub req_id: RequestId,
    pub subject: Subject,
    pub domain: DomainId,
    pub operation: Operation,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct CommitRecord {
    pub commit_index: u64,
    pub order_token: String,
    pub request_fingerprint: u64,
    pub lease: Lease,
    pub post_state_fingerprint: u64,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ReceiptV0 {
    pub req_id: String,
    pub subject: String,
    pub domain: String,
    pub operation: Operation,
    pub lease_id: String,
    pub commit_index: u64,
    pub order_token: String,
    pub request_fingerprint: u64,
    pub post_state_fingerprint: u64,
}

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct ModelState {
    accepted: Vec<CommitRecord>,
    requests: BTreeMap<RequestId, (u64, u64)>,
    leases_by_domain: BTreeMap<DomainId, String>,
}

impl RequestId {
    pub fn new(s: impl Into<String>) -> Result<Self, &'static str> {
        let s = s.into();
        validate_atom(&s, "req_id")?;
        Ok(Self(s))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl DomainId {
    pub fn new(s: impl Into<String>) -> Result<Self, &'static str> {
        let s = s.into();
        validate_domain(&s)?;
        Ok(Self(s))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl Subject {
    pub fn new(s: impl Into<String>) -> Result<Self, &'static str> {
        let s = s.into();
        validate_atom(&s, "subject")?;
        Ok(Self(s))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl NetRequest {
    pub fn new(
        req_id: &str,
        subject: &str,
        domain: &str,
        operation: Operation,
    ) -> Result<Self, &'static str> {
        Ok(Self {
            req_id: RequestId::new(req_id)?,
            subject: Subject::new(subject)?,
            domain: DomainId::new(domain)?,
            operation,
        })
    }

    fn fingerprint(&self) -> u64 {
        fn op_str(op: &Operation) -> &'static str {
            match op {
                Operation::Connect => "connect",
                Operation::ListenLocal => "listen-local",
            }
        }
        stable_fingerprint(&[
            self.req_id.as_str(),
            self.subject.as_str(),
            self.domain.as_str(),
            op_str(&self.operation),
        ])
    }
}

impl ModelState {
    pub fn accepted(&self) -> &[CommitRecord] {
        &self.accepted
    }

    pub fn live_leases(&self) -> &BTreeMap<DomainId, String> {
        &self.leases_by_domain
    }

    pub fn receipts(&self) -> Vec<ReceiptV0> {
        self.accepted.iter().map(ReceiptV0::from_commit_record).collect()
    }

    /// Check the model's internal conservation invariants.
    ///
    /// This is intentionally executable rather than proof-complete. It gives
    /// scenario tests and future bounded model-checker harnesses one stable
    /// fail-closed predicate for the current state representation.
    pub fn validate_invariants(&self) -> Result<(), &'static str> {
        if self.accepted.len() != self.requests.len() {
            return Err("request-index-cardinality-mismatch");
        }
        if self.accepted.len() != self.leases_by_domain.len() {
            return Err("lease-index-cardinality-mismatch");
        }

        let mut reconstructed_requests: BTreeMap<RequestId, (u64, u64)> = BTreeMap::new();
        let mut reconstructed_leases: BTreeMap<DomainId, String> = BTreeMap::new();

        for (idx, rec) in self.accepted.iter().enumerate() {
            let expected_index = idx as u64;
            if rec.commit_index != expected_index {
                return Err("non-contiguous-commit-index");
            }
            if rec.order_token != format!("order:{expected_index}") {
                return Err("order-token-mismatch");
            }
            if rec.lease.lease_id != format!("lease:{}", rec.lease.req_id.as_str()) {
                return Err("lease-id-mismatch");
            }
            if reconstructed_requests
                .insert(
                    rec.lease.req_id.clone(),
                    (rec.request_fingerprint, rec.commit_index),
                )
                .is_some()
            {
                return Err("duplicate-request-id-in-accepted-history");
            }
            if reconstructed_leases
                .insert(rec.lease.domain.clone(), rec.lease.lease_id.clone())
                .is_some()
            {
                return Err("duplicate-domain-in-accepted-history");
            }
            if fingerprint_domains(&reconstructed_leases) != rec.post_state_fingerprint {
                return Err("post-state-fingerprint-mismatch");
            }
        }

        if reconstructed_requests != self.requests {
            return Err("request-index-mismatch");
        }
        if reconstructed_leases != self.leases_by_domain {
            return Err("lease-index-mismatch");
        }
        Ok(())
    }

    pub fn apply(&mut self, request: NetRequest, admission: Admission) -> Outcome {
        let request_fingerprint = request.fingerprint();

        if let Some((seen_fp, original_commit_index)) = self.requests.get(&request.req_id).copied()
        {
            if seen_fp == request_fingerprint {
                let lease_id = format!("lease:{}", request.req_id.as_str());
                return Outcome::Replayed {
                    lease_id,
                    original_commit_index,
                };
            }
            return Outcome::Rejected("changed-replay-for-req-id");
        }

        if let Admission::Deny(reason) = admission {
            return Outcome::Denied(reason);
        }

        if self.leases_by_domain.contains_key(&request.domain) {
            return Outcome::Denied("domain-conflict");
        }

        let commit_index = self.accepted.len() as u64;
        let lease_id = format!("lease:{}", request.req_id.as_str());
        let lease = Lease {
            lease_id: lease_id.clone(),
            req_id: request.req_id.clone(),
            subject: request.subject.clone(),
            domain: request.domain.clone(),
            operation: request.operation.clone(),
        };
        self.leases_by_domain
            .insert(request.domain.clone(), lease_id.clone());
        self.requests
            .insert(request.req_id.clone(), (request_fingerprint, commit_index));

        let post_state_fingerprint = self.state_fingerprint();
        let record = CommitRecord {
            commit_index,
            order_token: format!("order:{commit_index}"),
            request_fingerprint,
            lease,
            post_state_fingerprint,
        };
        self.accepted.push(record);
        Outcome::Accepted {
            lease_id,
            commit_index,
        }
    }

    pub fn replay_prefix(records: &[CommitRecord]) -> Result<Self, &'static str> {
        let mut out = ModelState::default();
        for expected_index in 0..records.len() {
            let rec = &records[expected_index];
            if rec.commit_index != expected_index as u64 {
                return Err("non-contiguous-commit-index");
            }
            if out.leases_by_domain.contains_key(&rec.lease.domain) {
                return Err("prefix-domain-conflict");
            }
            out.leases_by_domain
                .insert(rec.lease.domain.clone(), rec.lease.lease_id.clone());
            out.requests.insert(
                rec.lease.req_id.clone(),
                (rec.request_fingerprint, rec.commit_index),
            );
            let post = out.state_fingerprint();
            if post != rec.post_state_fingerprint {
                return Err("prefix-post-state-fingerprint-mismatch");
            }
            out.accepted.push(rec.clone());
        }
        out.validate_invariants()?;
        Ok(out)
    }

    pub fn state_fingerprint(&self) -> u64 {
        fingerprint_domains(&self.leases_by_domain)
    }
}

impl ReceiptV0 {
    pub fn from_commit_record(record: &CommitRecord) -> Self {
        Self {
            req_id: record.lease.req_id.as_str().to_owned(),
            subject: record.lease.subject.as_str().to_owned(),
            domain: record.lease.domain.as_str().to_owned(),
            operation: record.lease.operation.clone(),
            lease_id: record.lease.lease_id.clone(),
            commit_index: record.commit_index,
            order_token: record.order_token.clone(),
            request_fingerprint: record.request_fingerprint,
            post_state_fingerprint: record.post_state_fingerprint,
        }
    }

    pub fn request(&self) -> Result<NetRequest, &'static str> {
        NetRequest::new(
            &self.req_id,
            &self.subject,
            &self.domain,
            self.operation.clone(),
        )
    }
}

pub fn verify_receipt_chain(receipts: &[ReceiptV0]) -> Result<(), &'static str> {
    replay_receipts(receipts).map(|_| ())
}

fn request_from_receipt(receipt: &ReceiptV0) -> Result<NetRequest, &'static str> {
    Ok(NetRequest {
        req_id: RequestId::new(&receipt.req_id).map_err(|_| "receipt-invalid-request-id-shape")?,
        subject: Subject::new(&receipt.subject).map_err(|_| "receipt-invalid-subject-shape")?,
        domain: DomainId::new(&receipt.domain).map_err(|_| "receipt-invalid-domain-shape")?,
        operation: receipt.operation.clone(),
    })
}

pub fn replay_receipts(receipts: &[ReceiptV0]) -> Result<ModelState, &'static str> {
    let mut out = ModelState::default();

    for (idx, receipt) in receipts.iter().enumerate() {
        let expected_index = idx as u64;
        if receipt.commit_index != expected_index {
            return Err("receipt-non-contiguous-commit-index");
        }
        if receipt.order_token != format!("order:{expected_index}") {
            return Err("receipt-order-token-mismatch");
        }

        let request = request_from_receipt(receipt)?;
        if receipt.lease_id != format!("lease:{}", request.req_id.as_str()) {
            return Err("receipt-lease-id-mismatch");
        }
        if request.fingerprint() != receipt.request_fingerprint {
            return Err("receipt-request-fingerprint-mismatch");
        }
        if out.requests.contains_key(&request.req_id) {
            return Err("receipt-duplicate-request-id");
        }
        if out.leases_by_domain.contains_key(&request.domain) {
            return Err("receipt-duplicate-domain");
        }

        let lease = Lease {
            lease_id: receipt.lease_id.clone(),
            req_id: request.req_id.clone(),
            subject: request.subject.clone(),
            domain: request.domain.clone(),
            operation: request.operation.clone(),
        };
        out.leases_by_domain
            .insert(request.domain.clone(), receipt.lease_id.clone());
        out.requests
            .insert(request.req_id.clone(), (receipt.request_fingerprint, receipt.commit_index));
        let post = out.state_fingerprint();
        if post != receipt.post_state_fingerprint {
            return Err("receipt-post-state-fingerprint-mismatch");
        }
        out.accepted.push(CommitRecord {
            commit_index: receipt.commit_index,
            order_token: receipt.order_token.clone(),
            request_fingerprint: receipt.request_fingerprint,
            lease,
            post_state_fingerprint: receipt.post_state_fingerprint,
        });
    }

    out.validate_invariants()?;
    Ok(out)
}

fn fingerprint_domains(leases_by_domain: &BTreeMap<DomainId, String>) -> u64 {
    let mut parts = Vec::new();
    for (domain, lease_id) in leases_by_domain {
        parts.push(domain.as_str());
        parts.push(lease_id.as_str());
    }
    stable_fingerprint(&parts)
}

fn validate_atom(s: &str, _field: &'static str) -> Result<(), &'static str> {
    if s.is_empty() || s.len() > 64 {
        return Err("invalid-atom-length");
    }
    if !s
        .bytes()
        .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_' || b == b':' || b == b'.')
    {
        return Err("invalid-atom-character");
    }
    Ok(())
}

fn validate_domain(s: &str) -> Result<(), &'static str> {
    if s.is_empty() || s.len() > 253 || s.starts_with('.') || s.ends_with('.') || s.contains("..") {
        return Err("invalid-domain-shape");
    }
    for label in s.split('.') {
        if label.is_empty() || label.len() > 63 {
            return Err("invalid-domain-label-length");
        }
        if label.starts_with('-') || label.ends_with('-') {
            return Err("invalid-domain-label-edge");
        }
        if !label
            .bytes()
            .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-')
        {
            return Err("invalid-domain-label-character");
        }
    }
    Ok(())
}

fn stable_fingerprint(parts: &[&str]) -> u64 {
    // FNV-1a 64-bit for deterministic model fingerprints. This is deliberately
    // not a cryptographic digest and must not be used as evidence bytes.
    let mut h: u64 = 0xcbf29ce484222325;
    for part in parts {
        for b in part.as_bytes() {
            h ^= u64::from(*b);
            h = h.wrapping_mul(0x100000001b3);
        }
        h ^= 0xff;
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}

#[cfg(test)]
mod tests {
    use super::*;

    fn req(id: &str, domain: &str) -> NetRequest {
        NetRequest::new(id, "svc:portal.net", domain, Operation::Connect).unwrap()
    }

    #[test]
    fn exact_replay_does_not_commit_twice() {
        let mut s = ModelState::default();
        let r = req("r1", "alpha.example");
        assert_eq!(
            s.apply(r.clone(), Admission::Allow),
            Outcome::Accepted {
                lease_id: "lease:r1".into(),
                commit_index: 0
            }
        );
        assert_eq!(
            s.apply(r, Admission::Allow),
            Outcome::Replayed {
                lease_id: "lease:r1".into(),
                original_commit_index: 0
            }
        );
        assert_eq!(s.accepted().len(), 1);
    }

    #[test]
    fn changed_replay_fails_closed() {
        let mut s = ModelState::default();
        assert!(matches!(
            s.apply(req("r1", "alpha.example"), Admission::Allow),
            Outcome::Accepted { .. }
        ));
        assert_eq!(
            s.apply(req("r1", "beta.example"), Admission::Allow),
            Outcome::Rejected("changed-replay-for-req-id")
        );
        assert_eq!(s.accepted().len(), 1);
    }

    #[test]
    fn same_domain_conflict_denies_without_commit() {
        let mut s = ModelState::default();
        assert!(matches!(
            s.apply(req("r1", "alpha.example"), Admission::Allow),
            Outcome::Accepted { .. }
        ));
        assert_eq!(
            s.apply(req("r2", "alpha.example"), Admission::Allow),
            Outcome::Denied("domain-conflict")
        );
        assert_eq!(s.accepted().len(), 1);
    }

    #[test]
    fn explicit_deny_does_not_commit() {
        let mut s = ModelState::default();
        assert_eq!(
            s.apply(req("r1", "alpha.example"), Admission::Deny("policy-deny")),
            Outcome::Denied("policy-deny")
        );
        assert!(s.accepted().is_empty());
        assert!(s.live_leases().is_empty());
    }

    #[test]
    fn replay_prefix_recovers_state() {
        let mut s = ModelState::default();
        assert!(matches!(
            s.apply(req("r1", "alpha.example"), Admission::Allow),
            Outcome::Accepted { .. }
        ));
        assert!(matches!(
            s.apply(req("r2", "beta.example"), Admission::Allow),
            Outcome::Accepted { .. }
        ));
        let prefix = ModelState::replay_prefix(&s.accepted()[..1]).unwrap();
        assert_eq!(prefix.accepted().len(), 1);
        assert_eq!(prefix.live_leases().len(), 1);
        assert!(
            prefix
                .live_leases()
                .contains_key(&DomainId::new("alpha.example").unwrap())
        );
        assert!(
            !prefix
                .live_leases()
                .contains_key(&DomainId::new("beta.example").unwrap())
        );
    }

    #[test]
    fn validation_is_canonical_and_closed() {
        assert!(
            NetRequest::new("r1", "svc:portal.net", "Upper.example", Operation::Connect).is_err()
        );
        assert!(
            NetRequest::new("r 1", "svc:portal.net", "alpha.example", Operation::Connect).is_err()
        );
        assert!(
            NetRequest::new("r1", "svc:portal.net", "alpha..example", Operation::Connect).is_err()
        );
    }

    #[test]
    fn accepted_states_satisfy_internal_invariants() {
        let mut s = ModelState::default();
        assert_eq!(s.validate_invariants(), Ok(()));
        assert!(matches!(
            s.apply(req("r1", "alpha.example"), Admission::Allow),
            Outcome::Accepted { .. }
        ));
        assert_eq!(s.validate_invariants(), Ok(()));
        assert_eq!(
            s.apply(req("r2", "alpha.example"), Admission::Allow),
            Outcome::Denied("domain-conflict")
        );
        assert_eq!(s.validate_invariants(), Ok(()));
        assert_eq!(
            s.apply(req("r1", "beta.example"), Admission::Allow),
            Outcome::Rejected("changed-replay-for-req-id")
        );
        assert_eq!(s.validate_invariants(), Ok(()));
    }

    #[test]
    fn accepted_history_exports_verifiable_receipts() {
        let mut s = ModelState::default();
        assert!(matches!(
            s.apply(req("r1", "alpha.example"), Admission::Allow),
            Outcome::Accepted { .. }
        ));
        assert!(matches!(
            s.apply(req("r2", "beta.example"), Admission::Allow),
            Outcome::Accepted { .. }
        ));
        let receipts = s.receipts();
        assert_eq!(verify_receipt_chain(&receipts), Ok(()));
        assert_eq!(replay_receipts(&receipts).unwrap(), s);

        let mut tampered = receipts.clone();
        tampered[0].lease_id = "lease:other".into();
        assert_eq!(
            verify_receipt_chain(&tampered),
            Err("receipt-lease-id-mismatch")
        );
    }

}
