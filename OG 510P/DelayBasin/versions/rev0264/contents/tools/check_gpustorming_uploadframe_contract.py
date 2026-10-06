import pathlib

from gpustorming_contract_lib import late_search_standard_family_contract_kwargs, run_standard_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_standard_family_contract(
    ROOT,
    "gpustorming-uploadframe",
    **late_search_standard_family_contract_kwargs("uploadframe"),
    quarantine_id="QWS-0192",
    quarantine_text="upload court / attachment-authority board / file-eligibility controller",
    changelog_text="upload-neutralized / attachment-detached / public-web-replayed guard",
    archive_index_text="upload-neutralized, attachment-detached, or public-web-replayed control",
)
