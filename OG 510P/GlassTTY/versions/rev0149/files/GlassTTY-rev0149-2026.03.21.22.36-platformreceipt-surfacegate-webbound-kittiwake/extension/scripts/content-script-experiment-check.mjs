import assert from 'node:assert/strict';
import {
  buildContentScriptExperimentRegistration,
  dynamicContentScriptRulesFromRegisteredScripts,
  staticContentScriptRulesFromManifest,
  summarizeContentScriptPolicy,
} from '../dist/shared/content-script-experiments.js';

const manifest = {
  content_scripts: [
    {
      matches: ['https://claude.ai/chat/*', 'http://127.0.0.1:8765/*'],
      js: ['dist/content/main.js'],
      run_at: 'document_idle',
    },
  ],
};

const staticRules = staticContentScriptRulesFromManifest(manifest);
assert.equal(staticRules.length, 1);
assert.equal(staticRules[0].allFrames, false);

const aboutPlan = buildContentScriptExperimentRegistration(staticRules, 'manifest_match_about_blank');
assert.equal(aboutPlan.registeredScripts[0].allFrames, true);
assert.equal(aboutPlan.registeredScripts[0].matchAboutBlank, true);
assert.equal(aboutPlan.registeredScripts[0].persistAcrossSessions, false);
assert.equal(aboutPlan.widenedMatchPatterns, false);

const fallbackPlan = buildContentScriptExperimentRegistration(staticRules, 'manifest_match_origin_as_fallback');
assert.equal(fallbackPlan.registeredScripts[0].matchOriginAsFallback, true);
assert.equal(fallbackPlan.registeredScripts[0].matches[0], 'https://claude.ai/*');
assert.equal(fallbackPlan.registeredScripts[0].matches[1], 'http://127.0.0.1:8765/*');
assert.equal(fallbackPlan.widenedMatchPatterns, true);
assert.equal(fallbackPlan.invalidMatchPatterns.length, 0);

const dynamicRules = dynamicContentScriptRulesFromRegisteredScripts(fallbackPlan.registeredScripts);
const policy = summarizeContentScriptPolicy(staticRules, dynamicRules);
assert.equal(policy.staticContentScriptCount, 1);
assert.equal(policy.dynamicContentScriptCount, 1);
assert.equal(policy.allFrames, true);
assert.equal(policy.matchOriginAsFallback, true);
assert.equal(policy.activeExperiment?.id, 'manifest_match_origin_as_fallback');
assert.equal(policy.activeExperiment?.registeredScriptCount, 1);
assert.equal(policy.activeExperiment?.widenedMatchPatterns, true);

process.stdout.write(`${JSON.stringify({ ok: true, aboutPlan, fallbackPlan, policy }, null, 2)}\n`);
