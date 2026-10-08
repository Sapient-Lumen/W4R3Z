from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sidepanel_has_local_recovery_vault_controls_and_storage_guard() -> None:
    source = (ROOT / 'extension' / 'src' / 'sidepanel' / 'main.ts').read_text(encoding='utf-8')
    html = (ROOT / 'extension' / 'sidepanel' / 'index.html').read_text(encoding='utf-8')
    chrome_types = (ROOT / 'extension' / 'src' / 'types' / 'chrome.d.ts').read_text(encoding='utf-8')

    assert 'proof-recovery-vault-status' in html
    assert 'proof-save-vault' in html
    assert 'proof-restore-vault' in html
    assert 'proof-download-vault' in html
    assert 'proof-clear-vault' in html
    assert 'Save recovery vault' in html
    assert 'Restore recovery vault' in html
    assert 'Download recovery JSON' in html
    assert 'Clear recovery vault' in html

    assert "PROOF_RECOVERY_VAULT_KEY = 'glasstty.chatgpt.firstProof.recoveryVault.v1'" in source
    assert 'ProofRecoveryVaultRecord' in source
    assert 'chrome.storage.local.set({ [PROOF_RECOVERY_VAULT_KEY]: record })' in source
    assert 'chrome.storage.local.remove(PROOF_RECOVERY_VAULT_KEY)' in source
    assert 'saveProofRecoveryVault(\'auto\')' in source
    assert "renderProofCapture({ persist: false })" in source
    assert 'Restore recovery vault or Download recovery JSON' in source
    assert 'Full proof document could not be persisted in chrome.storage.local' in source
    assert 'visible_tab_screenshot_data_url' in source
    assert "save_recovery_vault: 'proof-save-vault'" in source
    assert "download_recovery_json: 'proof-download-vault'" in source
    assert "storage_backend: 'chrome.storage.local'" in source
    assert "function remove(keys: string | string[]): Promise<void>;" in chrome_types
