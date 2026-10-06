import pathlib

from gpustorming_contract_lib import run_standard_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_standard_family_contract(
    ROOT,
    "gpustorming-liveframe",
    family="liveframe",
    operator_variant="live-neutralized, camera-disconnected, or still-basis-replayed variant",
    privileges=["live-context privilege", "camera-feed privilege", "motion-scene privilege"],
    crosswalk_text="live camera feeds, interactive voice-and-video search turns, moving-scene visual search, or other embodied real-time context",
    oq_variant="live-neutralized/camera-disconnected/still-basis-replayed variant",
    prompt_variant="live-neutralized, camera-disconnected, or still-basis-replayed variant worth checking",
    runbook_variant="live-neutralized, camera-disconnected, or still-basis-replayed variant",
    quarantine_id="QWS-0191",
    quarantine_text="live court / embodied-context board / camera-eligibility controller",
    changelog_text="live-neutralized / camera-disconnected / still-basis-replayed guard",
    archive_index_text="live-neutralized, camera-disconnected, or still-basis-replayed control",
)
