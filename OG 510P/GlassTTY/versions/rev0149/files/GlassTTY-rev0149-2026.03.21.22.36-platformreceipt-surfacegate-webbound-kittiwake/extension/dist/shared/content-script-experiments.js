const EXPERIMENT_PREFIX = 'glasstty-exp-';
function compactString(value) {
    if (typeof value !== 'string')
        return undefined;
    const trimmed = value.trim();
    return trimmed || undefined;
}
function uniqueStrings(values) {
    const out = [];
    const seen = new Set();
    for (const value of values) {
        const normalized = compactString(value);
        if (!normalized || seen.has(normalized))
            continue;
        seen.add(normalized);
        out.push(normalized);
    }
    return out;
}
function scriptLabel(id) {
    if (id === 'manifest_all_frames')
        return 'Dynamic matching child-frame experiment';
    if (id === 'manifest_match_about_blank')
        return 'Dynamic about:blank descendant experiment';
    return 'Dynamic related-frame fallback experiment';
}
function experimentNotes(id) {
    if (id === 'manifest_all_frames') {
        return [
            'Registers a non-persistent dynamic content script so matching child frames can receive the existing GlassTTY content runtime declaratively.',
            'Already-loaded documents may still need a reload or fresh navigation before the dynamic registration becomes observable in probes.',
        ];
    }
    if (id === 'manifest_match_about_blank') {
        return [
            'Registers a non-persistent dynamic content script with allFrames plus matchAboutBlank for about:blank descendant experiments.',
            'Chrome documents match_about_blank as the focused declarative lever for about:blank descendants; a reload or fresh navigation is still recommended for proof capture.',
        ];
    }
    return [
        'Registers a non-persistent dynamic content script with allFrames plus matchOriginAsFallback for about:/data:/blob:/filesystem: descendant experiments.',
        'Chrome requires * paths when match_origin_as_fallback is enabled, so GlassTTY widens any narrower match-pattern paths in the experiment registration.',
        'A reload or fresh navigation is still recommended before comparing probe coverage against the experiment-plan prediction.',
    ];
}
function normalizeMatchPatternForOriginFallback(match) {
    const trimmed = compactString(match);
    if (!trimmed)
        return { match, widened: false, valid: false };
    if (trimmed === '<all_urls>')
        return { match: trimmed, widened: false, valid: true };
    const parsed = /^(\*|http|https|file|ftp):\/\/([^/]*)(\/.*)$/.exec(trimmed);
    if (!parsed)
        return { match: trimmed, widened: false, valid: false };
    const [, scheme, host, path] = parsed;
    if (path === '/*')
        return { match: trimmed, widened: false, valid: true };
    return { match: `${scheme}://${host}/*`, widened: true, valid: true };
}
function parseRule(source, script) {
    return {
        ...(compactString(script.id) ? { id: compactString(script.id) } : {}),
        source,
        matches: uniqueStrings(Array.isArray(script.matches) ? script.matches : []),
        js: uniqueStrings(Array.isArray(script.js) ? script.js : []),
        css: uniqueStrings(Array.isArray(script.css) ? script.css : []),
        ...(compactString(script.run_at ?? script.runAt) ? { runAt: compactString(script.run_at ?? script.runAt) } : {}),
        allFrames: script.all_frames === true || script.allFrames === true,
        matchAboutBlank: script.match_about_blank === true || script.matchAboutBlank === true,
        matchOriginAsFallback: script.match_origin_as_fallback === true || script.matchOriginAsFallback === true,
        ...(compactString(script.world) ? { world: compactString(script.world) } : {}),
        ...((typeof script.persistAcrossSessions === 'boolean') ? { persistAcrossSessions: script.persistAcrossSessions } : {}),
    };
}
export function experimentRegistrationId(experimentId, index) {
    return `${EXPERIMENT_PREFIX}${experimentId}-${index + 1}`;
}
export function glassTTYExperimentIdFromScriptId(id) {
    const normalized = compactString(id);
    if (!normalized || !normalized.startsWith(EXPERIMENT_PREFIX))
        return undefined;
    const body = normalized.slice(EXPERIMENT_PREFIX.length);
    if (body.startsWith('manifest_all_frames-'))
        return 'manifest_all_frames';
    if (body.startsWith('manifest_match_about_blank-'))
        return 'manifest_match_about_blank';
    if (body.startsWith('manifest_match_origin_as_fallback-'))
        return 'manifest_match_origin_as_fallback';
    return undefined;
}
export function staticContentScriptRulesFromManifest(manifest = {}) {
    const scripts = Array.isArray(manifest.content_scripts)
        ? manifest.content_scripts
        : [];
    return scripts.map((script) => parseRule('static', script));
}
export function dynamicContentScriptRulesFromRegisteredScripts(scripts = []) {
    return scripts
        .filter((script) => glassTTYExperimentIdFromScriptId(compactString(script.id)) !== undefined)
        .map((script) => parseRule('dynamic', script));
}
export function buildContentScriptExperimentRegistration(rules = [], experimentId) {
    const experimentRules = rules.filter((rule) => rule.source === 'static' && (rule.js.length || rule.css.length));
    const invalidMatchPatterns = [];
    let widenedMatchPatterns = false;
    const registeredScripts = experimentRules.map((rule, index) => {
        const normalizedMatches = experimentId === 'manifest_match_origin_as_fallback'
            ? rule.matches.map((match) => {
                const normalized = normalizeMatchPatternForOriginFallback(match);
                if (!normalized.valid)
                    invalidMatchPatterns.push(match);
                widenedMatchPatterns ||= normalized.widened;
                return normalized.match;
            })
            : [...rule.matches];
        return {
            id: experimentRegistrationId(experimentId, index),
            matches: uniqueStrings(normalizedMatches),
            ...(rule.js.length ? { js: [...rule.js] } : {}),
            ...(rule.css.length ? { css: [...rule.css] } : {}),
            ...(rule.runAt ? { runAt: rule.runAt } : {}),
            ...(rule.world ? { world: rule.world } : {}),
            ...(experimentId === 'manifest_all_frames' || experimentId === 'manifest_match_about_blank' || experimentId === 'manifest_match_origin_as_fallback' ? { allFrames: true } : {}),
            ...(experimentId === 'manifest_match_about_blank' ? { matchAboutBlank: true } : {}),
            ...(experimentId === 'manifest_match_origin_as_fallback' ? { matchOriginAsFallback: true } : {}),
            persistAcrossSessions: false,
        };
    });
    return {
        experimentId,
        label: scriptLabel(experimentId),
        scriptIds: registeredScripts.map((script) => script.id),
        widenedMatchPatterns,
        invalidMatchPatterns: uniqueStrings(invalidMatchPatterns),
        requiresNavigation: true,
        notes: experimentNotes(experimentId),
        registeredScripts,
    };
}
export function summarizeContentScriptPolicy(staticRules = [], dynamicRules = []) {
    const allRules = [...staticRules, ...dynamicRules];
    const experimentIds = uniqueStrings(dynamicRules.map((rule) => glassTTYExperimentIdFromScriptId(rule.id))).filter((value) => (value === 'manifest_all_frames' || value === 'manifest_match_about_blank' || value === 'manifest_match_origin_as_fallback'));
    let activeExperiment;
    if (experimentIds.length === 1) {
        const experimentId = experimentIds[0];
        const registration = buildContentScriptExperimentRegistration(staticRules, experimentId);
        activeExperiment = {
            id: experimentId,
            label: scriptLabel(experimentId),
            registeredScriptCount: dynamicRules.length,
            scriptIds: uniqueStrings(dynamicRules.map((rule) => rule.id)),
            matches: uniqueStrings(dynamicRules.flatMap((rule) => rule.matches)),
            allFrames: dynamicRules.some((rule) => rule.allFrames),
            matchAboutBlank: dynamicRules.some((rule) => rule.matchAboutBlank),
            matchOriginAsFallback: dynamicRules.some((rule) => rule.matchOriginAsFallback),
            runAt: uniqueStrings(dynamicRules.map((rule) => rule.runAt)),
            persistAcrossSessions: dynamicRules.every((rule) => rule.persistAcrossSessions !== false),
            widenedMatchPatterns: registration.widenedMatchPatterns,
            requiresNavigation: registration.requiresNavigation,
            notes: registration.notes,
        };
    }
    return {
        staticContentScriptCount: staticRules.length,
        dynamicContentScriptCount: dynamicRules.length,
        matches: uniqueStrings(allRules.flatMap((rule) => rule.matches)),
        allFrames: allRules.some((rule) => rule.allFrames),
        matchAboutBlank: allRules.some((rule) => rule.matchAboutBlank),
        matchOriginAsFallback: allRules.some((rule) => rule.matchOriginAsFallback),
        runAt: uniqueStrings(allRules.map((rule) => rule.runAt)),
        ...(activeExperiment ? { activeExperiment } : {}),
    };
}
