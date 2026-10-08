#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

JsonDict = dict[str, Any]

GAP_STATUSES = {'candidate_document', 'candidate_frame', 'related_frame_url', 'missing_target'}
EXPERIMENT_BY_ACTIVE_ID = {
    'manifest_all_frames': 'manifest_all_frames',
    'manifest_match_about_blank': 'manifest_match_about_blank',
    'manifest_match_origin_as_fallback': 'manifest_match_origin_as_fallback',
}
EXPERIMENT_BY_POLICY = {
    (False, False, False): 'current_runtime_priming',
    (True, False, False): 'manifest_all_frames',
    (True, True, False): 'manifest_match_about_blank',
    (True, False, True): 'manifest_match_origin_as_fallback',
    (True, True, True): 'manifest_match_origin_as_fallback',
}
RELATED_URL_PREFIXES = ('about:', 'data:', 'blob:', 'filesystem:')
UUIDISH = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)
LONG_HEXISH = re.compile(r'^[0-9a-f]{12,}$', re.IGNORECASE)
LONG_MIXED_ID = re.compile(r'^(?=.*\d)[A-Za-z0-9_-]{12,}$')


def compact_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    trimmed = value.strip()
    return trimmed or None


def load_json(path: Path) -> JsonDict:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'{path} is not a JSON object')
    return data


def as_dict(value: Any) -> JsonDict:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def extract_payload(document: JsonDict) -> JsonDict:
    message = as_dict(document.get('message'))
    payload = message.get('payload')
    if isinstance(payload, dict):
        return payload
    payload = document.get('payload')
    if isinstance(payload, dict):
        return payload
    return document


def infer_experiment_id(policy: JsonDict) -> str | None:
    active = as_dict(policy.get('activeExperiment'))
    active_id = compact_string(active.get('id'))
    if active_id in EXPERIMENT_BY_ACTIVE_ID:
        return EXPERIMENT_BY_ACTIVE_ID[active_id]
    key = (
        policy.get('allFrames') is True,
        policy.get('matchAboutBlank') is True,
        policy.get('matchOriginAsFallback') is True,
    )
    return EXPERIMENT_BY_POLICY.get(key)


def related_frame_scheme(url: Any) -> str | None:
    normalized = compact_string(url)
    if not normalized:
        return None
    lowered = normalized.lower()
    for prefix in RELATED_URL_PREFIXES:
        if lowered.startswith(prefix):
            return prefix[:-1]
    return None


def frame_signature(frame: JsonDict) -> str:
    status = compact_string(frame.get('status')) or 'unknown'
    url = compact_string(frame.get('url'))
    scheme = related_frame_scheme(url)
    if scheme:
        return f'{status}:{scheme}'
    frame_type = compact_string(frame.get('frameType')) or 'unknown'
    return f'{status}:{frame_type}'


def normalize_path_segment(segment: str) -> str:
    trimmed = segment.strip()
    if not trimmed:
        return ''
    lowered = trimmed.lower()
    if lowered.isdigit():
        return ':n'
    if UUIDISH.match(lowered) or LONG_HEXISH.match(lowered) or LONG_MIXED_ID.match(trimmed):
        return ':id'
    return lowered


def normalize_path_shape(path: str) -> str:
    segments = [normalize_path_segment(part) for part in path.split('/') if part.strip()]
    if not segments:
        return '/'
    limited = segments[:3]
    if len(segments) > 3:
        limited.append('…')
    return '/' + '/'.join(limited)


def stable_gap_signature(frame: JsonDict) -> str:
    status = compact_string(frame.get('status')) or 'unknown'
    frame_type = compact_string(frame.get('frameType')) or 'unknown'
    url = compact_string(frame.get('url'))
    scheme = related_frame_scheme(url)
    if scheme:
        return f'{status}|{frame_type}|related:{scheme}'
    if url:
        parsed = urlparse(url)
        host = (parsed.hostname or parsed.netloc or '').lower() or 'unknown-host'
        scheme_name = (parsed.scheme or 'unknown').lower()
        path_shape = normalize_path_shape(parsed.path)
        return f'{status}|{frame_type}|{scheme_name}://{host}{path_shape}'
    document_id = compact_string(frame.get('documentId'))
    if document_id:
        return f'{status}|{frame_type}|doc-present'
    return f'{status}|{frame_type}|targetless'


def coarse_gap_signature(frame: JsonDict) -> str:
    status = compact_string(frame.get('status')) or 'unknown'
    url = compact_string(frame.get('url'))
    scheme = related_frame_scheme(url)
    if scheme:
        return f'{status}|related:{scheme}'
    if url:
        parsed = urlparse(url)
        host = (parsed.hostname or parsed.netloc or '').lower() or 'unknown-host'
        scheme_name = (parsed.scheme or 'unknown').lower()
        return f'{status}|{scheme_name}://{host}'
    frame_type = compact_string(frame.get('frameType')) or 'unknown'
    return f'{status}|{frame_type}'


def counter_to_dict(counter: Counter[str]) -> JsonDict:
    return dict(sorted((key, value) for key, value in counter.items() if value > 0))


def counter_intersection(left: Counter[str], right: Counter[str]) -> Counter[str]:
    out: Counter[str] = Counter()
    for key in set(left) & set(right):
        count = min(left[key], right[key])
        if count > 0:
            out[key] = count
    return out


def counter_difference(left: Counter[str], right: Counter[str]) -> Counter[str]:
    out: Counter[str] = Counter()
    for key, value in left.items():
        remaining = value - right.get(key, 0)
        if remaining > 0:
            out[key] = remaining
    return out


def counter_summary(counter: Counter[str], *, limit: int = 4) -> str:
    if not counter:
        return 'none'
    items = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    preview = ', '.join(f'{key}×{value}' for key, value in items[:limit])
    if len(items) > limit:
        preview += f', +{len(items) - limit} more'
    return preview


def gap_frames_from_audit(audit: JsonDict) -> list[JsonDict]:
    frames = []
    for frame in as_list(audit.get('frames')):
        if not isinstance(frame, dict):
            continue
        if frame.get('status') in GAP_STATUSES:
            frames.append(frame)
    return frames


def status_counts(frames: list[JsonDict]) -> JsonDict:
    return dict(sorted(Counter(compact_string(frame.get('status')) or 'unknown' for frame in frames).items()))


def signature_counts(frames: list[JsonDict]) -> JsonDict:
    return dict(sorted(Counter(frame_signature(frame) for frame in frames).items()))


def stable_signature_counts(frames: list[JsonDict]) -> JsonDict:
    return counter_to_dict(Counter(stable_gap_signature(frame) for frame in frames))


def coarse_signature_counts(frames: list[JsonDict]) -> JsonDict:
    return counter_to_dict(Counter(coarse_gap_signature(frame) for frame in frames))


def extract_probe_evidence(path: Path) -> JsonDict:
    document = load_json(path)
    payload = extract_payload(document)
    manifest = as_dict(payload.get('manifest'))
    receiver_audit = as_dict(payload.get('receiverAudit'))
    coverage_audit = as_dict(receiver_audit.get('coverageAudit'))
    if not coverage_audit:
        metadata = as_dict(payload.get('metadata'))
        coverage_audit = as_dict(metadata.get('receiver_coverage_audit'))
        manifest = {
            'contentScriptPolicy': metadata.get('receiver_coverage_manifest_policy')
        } if metadata.get('receiver_coverage_manifest_policy') else manifest
    experiment_plan = as_dict(coverage_audit.get('experimentPlan'))
    if not experiment_plan:
        metadata = as_dict(payload.get('metadata'))
        experiment_plan = as_dict(metadata.get('receiver_coverage_experiment_plan'))
    policy_hints = as_dict(coverage_audit.get('policyHints'))
    counts = as_dict(coverage_audit.get('counts'))
    gap_frames = gap_frames_from_audit(coverage_audit)
    content_script_policy = as_dict(manifest.get('contentScriptPolicy'))
    inferred_experiment_id = infer_experiment_id(content_script_policy)
    baseline_gap_count = counts.get('gapCount') if isinstance(counts.get('gapCount'), int) else len(gap_frames)
    return {
        'path': str(path),
        'payload_kind': 'probe' if receiver_audit else 'fixture',
        'manifest': manifest,
        'contentScriptPolicy': content_script_policy,
        'receiverAudit': receiver_audit,
        'coverageAudit': coverage_audit,
        'policyHints': policy_hints,
        'experimentPlan': experiment_plan,
        'gapFrames': gap_frames,
        'gapFrameIds': [frame['frameId'] for frame in gap_frames if isinstance(frame.get('frameId'), int)],
        'gapFrameCount': baseline_gap_count,
        'gapStatusCounts': status_counts(gap_frames),
        'gapSignatureCounts': signature_counts(gap_frames),
        'gapStableSignatureCounts': stable_signature_counts(gap_frames),
        'gapCoarseSignatureCounts': coarse_signature_counts(gap_frames),
        'inferredExperimentId': inferred_experiment_id,
    }


def experiment_lookup(plan: JsonDict) -> dict[str, JsonDict]:
    out: dict[str, JsonDict] = {}
    for experiment in as_list(plan.get('experiments')):
        if not isinstance(experiment, dict):
            continue
        experiment_id = compact_string(experiment.get('id'))
        if experiment_id:
            out[experiment_id] = experiment
    return out


def manifest_policy_from_experiment(experiment: JsonDict | None, fallback: JsonDict) -> JsonDict:
    if isinstance(experiment, dict):
        policy = as_dict(experiment.get('manifestPolicy'))
        if policy:
            return policy
    return fallback


def experiment_addresses_frame(frame: JsonDict, manifest_policy: JsonDict) -> bool:
    status = compact_string(frame.get('status'))
    if status in {'candidate_document', 'candidate_frame'}:
        return True
    if status != 'related_frame_url':
        return False
    if manifest_policy.get('allFrames') is not True:
        return False
    scheme = related_frame_scheme(frame.get('url'))
    if manifest_policy.get('matchOriginAsFallback') is True:
        return scheme in {'about', 'data', 'blob', 'filesystem'}
    if manifest_policy.get('matchAboutBlank') is True:
        return scheme == 'about'
    return False


def gap_counters_for_policy(frames: list[JsonDict], policy: JsonDict) -> tuple[Counter[str], Counter[str], Counter[str], Counter[str]]:
    addressed_stable: Counter[str] = Counter()
    remaining_stable: Counter[str] = Counter()
    addressed_coarse: Counter[str] = Counter()
    remaining_coarse: Counter[str] = Counter()
    for frame in frames:
        target_stable = addressed_stable if experiment_addresses_frame(frame, policy) else remaining_stable
        target_coarse = addressed_coarse if experiment_addresses_frame(frame, policy) else remaining_coarse
        target_stable[stable_gap_signature(frame)] += 1
        target_coarse[coarse_gap_signature(frame)] += 1
    return addressed_stable, remaining_stable, addressed_coarse, remaining_coarse


def compare_shape_counters(
    candidate_stable: Counter[str],
    predicted_remaining_stable: Counter[str],
    predicted_addressed_stable: Counter[str],
    candidate_coarse: Counter[str],
    predicted_remaining_coarse: Counter[str],
) -> JsonDict:
    unexpected_stable = counter_difference(candidate_stable, predicted_remaining_stable)
    missing_predicted_stable = counter_difference(predicted_remaining_stable, candidate_stable)
    residual_addressed_stable = counter_intersection(candidate_stable, predicted_addressed_stable)
    expected_match_stable = counter_intersection(candidate_stable, predicted_remaining_stable)

    unexpected_coarse = counter_difference(candidate_coarse, predicted_remaining_coarse)
    missing_predicted_coarse = counter_difference(predicted_remaining_coarse, candidate_coarse)

    if residual_addressed_stable and unexpected_stable:
        stable_status = 'mixed_divergence'
    elif residual_addressed_stable:
        stable_status = 'residual_addressed_gaps'
    elif unexpected_stable and sum(candidate_stable.values()) == sum(predicted_remaining_stable.values()):
        stable_status = 'matched_counts_but_shapes_differ'
    elif unexpected_stable:
        stable_status = 'unexpected_new_gaps'
    elif missing_predicted_stable:
        stable_status = 'improved_more_than_predicted_shapes'
    else:
        stable_status = 'matched_predicted_shapes'

    coarse_status = 'matched_predicted_shapes'
    if unexpected_coarse and missing_predicted_coarse:
        coarse_status = 'mixed_divergence'
    elif unexpected_coarse and sum(candidate_coarse.values()) == sum(predicted_remaining_coarse.values()):
        coarse_status = 'matched_counts_but_shapes_differ'
    elif unexpected_coarse:
        coarse_status = 'unexpected_new_gaps'
    elif missing_predicted_coarse:
        coarse_status = 'improved_more_than_predicted_shapes'

    return {
        'stableSignatureStatus': stable_status,
        'coarseSignatureStatus': coarse_status,
        'predictedRemainingStableSignatures': counter_to_dict(predicted_remaining_stable),
        'candidateStableSignatures': counter_to_dict(candidate_stable),
        'expectedMatchedStableSignatures': counter_to_dict(expected_match_stable),
        'unexpectedCandidateStableSignatures': counter_to_dict(unexpected_stable),
        'missingPredictedStableSignatures': counter_to_dict(missing_predicted_stable),
        'residualAddressedStableSignatures': counter_to_dict(residual_addressed_stable),
        'predictedRemainingCoarseSignatures': counter_to_dict(predicted_remaining_coarse),
        'candidateCoarseSignatures': counter_to_dict(candidate_coarse),
        'unexpectedCandidateCoarseSignatures': counter_to_dict(unexpected_coarse),
        'missingPredictedCoarseSignatures': counter_to_dict(missing_predicted_coarse),
    }


def compare_evidence(baseline: JsonDict, candidate: JsonDict, *, experiment_id: str | None = None) -> JsonDict:
    warnings: list[str] = []
    baseline_plan = baseline['experimentPlan']
    lookup = experiment_lookup(baseline_plan)
    active_experiment_id = experiment_id or compact_string(candidate.get('inferredExperimentId'))
    if not active_experiment_id:
        warnings.append('Could not infer the candidate experiment from activeExperiment or manifest-policy deltas.')
    predicted = lookup.get(active_experiment_id or '') if active_experiment_id else None
    if active_experiment_id and active_experiment_id not in lookup:
        warnings.append(f'Baseline experiment plan does not include {active_experiment_id}.')
    baseline_recommended = compact_string(baseline_plan.get('recommendedExperimentId'))
    if baseline_recommended and active_experiment_id and baseline_recommended != active_experiment_id:
        warnings.append(f'Baseline recommended {baseline_recommended}, but candidate evidence points at {active_experiment_id}.')

    baseline_gap_count = baseline['gapFrameCount']
    candidate_gap_count = candidate['gapFrameCount']
    predicted_remaining = predicted.get('remainingGapCount') if isinstance(predicted, dict) and isinstance(predicted.get('remainingGapCount'), int) else None
    predicted_reduction = baseline_gap_count - predicted_remaining if isinstance(predicted_remaining, int) else None
    observed_reduction = baseline_gap_count - candidate_gap_count

    predicted_policy = manifest_policy_from_experiment(predicted, baseline['contentScriptPolicy'])
    predicted_addressed_stable, predicted_remaining_stable, predicted_addressed_coarse, predicted_remaining_coarse = gap_counters_for_policy(
        baseline['gapFrames'],
        predicted_policy,
    )
    candidate_stable = Counter(candidate['gapStableSignatureCounts'])
    candidate_coarse = Counter(candidate['gapCoarseSignatureCounts'])
    shape_comparison = compare_shape_counters(
        candidate_stable,
        predicted_remaining_stable,
        predicted_addressed_stable,
        candidate_coarse,
        predicted_remaining_coarse,
    )

    if active_experiment_id and active_experiment_id != 'current_runtime_priming' and baseline_gap_count == candidate_gap_count:
        warnings.append('Observed gap counts did not change after the declarative experiment. Chrome documents that dynamic registration changes do not remove already-injected scripts, so confirm the tab was reloaded or renavigated before treating this as a failed experiment.')

    if active_experiment_id == 'manifest_match_origin_as_fallback':
        active = as_dict(candidate['contentScriptPolicy'].get('activeExperiment'))
        if active.get('widenedMatchPatterns') is True:
            warnings.append('match_origin_as_fallback widened one or more narrower match paths to /*, which Chrome requires for initiator-origin fallback.')

    unexpected_stable = Counter(shape_comparison['unexpectedCandidateStableSignatures'])
    missing_predicted_stable = Counter(shape_comparison['missingPredictedStableSignatures'])
    residual_addressed_stable = Counter(shape_comparison['residualAddressedStableSignatures'])

    if residual_addressed_stable:
        warnings.append(
            'Candidate evidence still contains gap shapes the chosen experiment was expected to address: '
            + counter_summary(residual_addressed_stable)
            + '.'
        )
    if unexpected_stable:
        warnings.append(
            'Candidate evidence contains unexpected remaining gap shapes beyond the baseline prediction: '
            + counter_summary(unexpected_stable)
            + '.'
        )
    if missing_predicted_stable:
        warnings.append(
            'Candidate evidence no longer shows some gap shapes that the baseline predicted would remain: '
            + counter_summary(missing_predicted_stable)
            + '. This is often good news, but it means count-only comparisons understate what changed.'
        )
    if shape_comparison['stableSignatureStatus'] == 'matched_counts_but_shapes_differ':
        warnings.append('Gap counts matched the baseline prediction, but the stable gap signatures changed. Treat this as a count-only match rather than proof that the same frame shapes remained.')

    if predicted_reduction is None:
        prediction_status = 'unverifiable'
    elif candidate_gap_count < 0:
        prediction_status = 'unverifiable'
    elif candidate_gap_count == predicted_remaining:
        prediction_status = 'matched_exactly'
    elif candidate_gap_count < predicted_remaining:
        prediction_status = 'improved_more_than_predicted'
    elif candidate_gap_count < baseline_gap_count:
        prediction_status = 'improved_less_than_predicted'
    elif candidate_gap_count == baseline_gap_count:
        prediction_status = 'no_change'
    else:
        prediction_status = 'regressed'

    return {
        'experimentId': active_experiment_id,
        'baselineRecommendedExperimentId': baseline_recommended,
        'baselineCurrentExperimentId': compact_string(baseline_plan.get('currentExperimentId')),
        'predicted': {
            'available': predicted is not None,
            'remainingGapCount': predicted_remaining,
            'addressedFrameCount': predicted.get('addressedFrameCount') if isinstance(predicted, dict) else None,
            'incrementalGapReduction': predicted.get('incrementalGapReduction') if isinstance(predicted, dict) else None,
            'remainingGapFrameIds': predicted.get('remainingGapFrameIds') if isinstance(predicted, dict) else None,
            'pathWildcardRequired': predicted.get('pathWildcardRequired') if isinstance(predicted, dict) else None,
            'notes': predicted.get('notes') if isinstance(predicted, dict) else None,
            'predictedAddressedStableSignatures': counter_to_dict(predicted_addressed_stable),
            'predictedRemainingStableSignatures': counter_to_dict(predicted_remaining_stable),
            'predictedAddressedCoarseSignatures': counter_to_dict(predicted_addressed_coarse),
            'predictedRemainingCoarseSignatures': counter_to_dict(predicted_remaining_coarse),
        },
        'observed': {
            'baselineGapFrameCount': baseline_gap_count,
            'candidateGapFrameCount': candidate_gap_count,
            'gapFrameDelta': candidate_gap_count - baseline_gap_count,
            'observedGapReduction': observed_reduction,
            'baselineGapStatusCounts': baseline['gapStatusCounts'],
            'candidateGapStatusCounts': candidate['gapStatusCounts'],
            'baselineGapSignatureCounts': baseline['gapSignatureCounts'],
            'candidateGapSignatureCounts': candidate['gapSignatureCounts'],
            'baselineGapStableSignatureCounts': baseline['gapStableSignatureCounts'],
            'candidateGapStableSignatureCounts': candidate['gapStableSignatureCounts'],
            'baselineGapCoarseSignatureCounts': baseline['gapCoarseSignatureCounts'],
            'candidateGapCoarseSignatureCounts': candidate['gapCoarseSignatureCounts'],
            'baselineGapFrameIds': baseline['gapFrameIds'],
            'candidateGapFrameIds': candidate['gapFrameIds'],
        },
        'shapeComparison': shape_comparison,
        'predictionStatus': prediction_status,
        'warnings': warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Compare saved GlassTTY probe/fixture artifacts before and after a content-script coverage experiment.')
    parser.add_argument('baseline', help='Baseline bridge.probe JSON or fixture-capture JSON before the experiment')
    parser.add_argument('candidate', help='Post-experiment bridge.probe JSON or fixture-capture JSON')
    parser.add_argument('--experiment-id', choices=['current_runtime_priming', 'manifest_all_frames', 'manifest_match_about_blank', 'manifest_match_origin_as_fallback'], default=None, help='Override the experiment ID instead of inferring it from the candidate manifest policy')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output')
    args = parser.parse_args()

    baseline = extract_probe_evidence(Path(args.baseline))
    candidate = extract_probe_evidence(Path(args.candidate))
    report = {
        'ok': True,
        'baseline': {
            'path': baseline['path'],
            'payloadKind': baseline['payload_kind'],
            'gapFrameCount': baseline['gapFrameCount'],
            'gapStatusCounts': baseline['gapStatusCounts'],
            'gapSignatureCounts': baseline['gapSignatureCounts'],
            'gapStableSignatureCounts': baseline['gapStableSignatureCounts'],
            'gapCoarseSignatureCounts': baseline['gapCoarseSignatureCounts'],
            'recommendedExperimentId': compact_string(baseline['experimentPlan'].get('recommendedExperimentId')),
            'contentScriptPolicy': baseline['contentScriptPolicy'],
        },
        'candidate': {
            'path': candidate['path'],
            'payloadKind': candidate['payload_kind'],
            'gapFrameCount': candidate['gapFrameCount'],
            'gapStatusCounts': candidate['gapStatusCounts'],
            'gapSignatureCounts': candidate['gapSignatureCounts'],
            'gapStableSignatureCounts': candidate['gapStableSignatureCounts'],
            'gapCoarseSignatureCounts': candidate['gapCoarseSignatureCounts'],
            'contentScriptPolicy': candidate['contentScriptPolicy'],
            'inferredExperimentId': candidate['inferredExperimentId'],
        },
        'comparison': compare_evidence(baseline, candidate, experiment_id=args.experiment_id),
    }
    indent = 2 if args.pretty else None
    print(json.dumps(report, ensure_ascii=False, indent=indent))


if __name__ == '__main__':
    main()
