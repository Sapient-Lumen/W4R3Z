export const TEST_FACILITY_SCHEMA_VERSION = 2;
const DEFAULT_TASK_SIZE_TIMEOUTS = Object.freeze({
  tiny: 2500,
  small: 5000,
  medium: 15000,
  large: 60000,
  enormous: 300000
});
const ALLOWED_SIZES = new Set(Object.keys(DEFAULT_TASK_SIZE_TIMEOUTS));
const ALLOWED_ISOLATION = new Set(['shared-process', 'fresh-process', 'exclusive-process', 'browser-context', 'browser-process', 'manual']);
const ALLOWED_FLAKE = new Set(['none', 'suspected', 'quarantined']);
export function stableHash32(value) {
  const text = String(value);
  let hash = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}
export function parseShard(value) {
  if (!value || value === 'all') return { index: 1, total: 1 };
  const match = String(value).match(/^(\d+)\/(\d+)$/);
  if (!match) throw new Error(`Bad shard spec ${value}; expected x/y`);
  const index = Number(match[1]);
  const total = Number(match[2]);
  if (!Number.isInteger(index) || !Number.isInteger(total) || total < 1 || index < 1 || index > total) throw new Error(`Invalid shard spec ${value}`);
  return { index, total };
}
export function normalizePath(value) {
  return String(value || '').replace(/\\+/g, '/').replace(/^\.\//, '');
}
export function parseChangedList(value) {
  if (!value) return [];
  if (Array.isArray(value)) return value.flatMap((entry) => parseChangedList(entry));
  return String(value).split(/[\n,]/).map((x) => normalizePath(x.trim())).filter(Boolean);
}
export function normalizeChangedFiles(value) {
  return parseChangedList(value);
}
export function globToRegExp(glob) {
  const normalized = normalizePath(glob);
  let out = '^';
  for (let i = 0; i < normalized.length; i += 1) {
    const ch = normalized[i];
    const next = normalized[i + 1];
    if (ch === '*' && next === '*') {
      const after = normalized[i + 2];
      if (after === '/') { out += '(?:.*/)?'; i += 2; }
      else { out += '.*'; i += 1; }
    } else if (ch === '*') out += '[^/]*';
    else if (ch === '?') out += '[^/]';
    else if ('\\^$+?.()|{}[]'.includes(ch)) out += `\\${ch}`;
    else out += ch;
  }
  out += '$';
  return new RegExp(out);
}
export function matchesGlob(file, glob) {
  return globToRegExp(glob).test(normalizePath(file));
}
export function matchesAnyGlob(file, patterns = []) {
  return patterns.some((pattern) => matchesGlob(file, pattern));
}
export function taskMatchesChanged(task, changedFiles = []) {
  const files = parseChangedList(changedFiles);
  if (!files.length) return true;
  if (task.alwaysRun) return true;
  const inputs = Array.isArray(task.inputs) ? task.inputs : [];
  return files.some((file) => matchesAnyGlob(file, inputs));
}
export function selectImpactRules(impactMap, changedFiles = []) {
  const files = parseChangedList(changedFiles);
  const rules = Array.isArray(impactMap?.rules) ? impactMap.rules : [];
  return rules.filter((rule) => files.some((file) => matchesAnyGlob(file, rule.globs || [])));
}
export function impactedTaskIds(impactMap, changedFiles = []) {
  const ids = new Set();
  for (const rule of selectImpactRules(impactMap, changedFiles)) for (const id of rule.taskIds || []) ids.add(id);
  return [...ids].sort();
}
export function explainImpact(impactMap, changedFiles = []) {
  const files = parseChangedList(changedFiles);
  const rules = selectImpactRules(impactMap, files);
  return {
    changedFiles: files,
    matchedRuleCount: rules.length,
    matchedRules: rules.map((rule) => ({
      id: rule.id,
      reason: rule.reason || '',
      taskIds: (rule.taskIds || []).slice().sort(),
      tags: (rule.tags || []).slice().sort(),
      matchingFiles: files.filter((file) => matchesAnyGlob(file, rule.globs || []))
    })),
    taskIds: impactedTaskIds(impactMap, files)
  };
}
export function selectTasks(manifest, options = {}) {
  const tier = options.tier || 'release';
  const tag = options.tag || null;
  const lane = options.lane || null;
  const explicitIds = new Set((options.ids || []).filter(Boolean));
  const changedTaskIds = new Set(options.changedTaskIds || []);
  const hasImpactIds = changedTaskIds.size > 0;
  const changedFiles = hasImpactIds ? [] : parseChangedList(options.changedFiles || options.changed || []);
  const shard = parseShard(options.shard || 'all');
  const includeQuarantined = Boolean(options.includeQuarantined);
  let selected = (Array.isArray(manifest.tasks) ? manifest.tasks.slice() : []).filter((task) => {
    if (explicitIds.size > 0 && !explicitIds.has(task.id)) return false;
    if (hasImpactIds && !changedTaskIds.has(task.id) && !task.alwaysRun) return false;
    if (tier !== 'all' && !(task.tiers || []).includes(tier)) return false;
    if (tag && !(task.tags || []).includes(tag)) return false;
    if (lane && task.lane !== lane) return false;
    if (!includeQuarantined && (task.flakiness || 'none') === 'quarantined') return false;
    if (changedFiles.length > 0 && !taskMatchesChanged(task, changedFiles)) return false;
    return true;
  });
  selected.sort((a, b) => String(a.id).localeCompare(String(b.id)));
  if (shard.total > 1) selected = selectWeightedShard(selected, shard.index, shard.total);
  return selected;
}
export function selectWeightedShard(tasks, index, total) {
  const bins = Array.from({ length: total }, (_, i) => ({ index: i + 1, weight: 0, tasks: [] }));
  const sorted = tasks.slice().sort((a, b) => ((b.estimatedMs || 1) - (a.estimatedMs || 1)) || (stableHash32(a.id) - stableHash32(b.id)));
  for (const task of sorted) {
    bins.sort((a, b) => (a.weight - b.weight) || (a.index - b.index));
    bins[0].tasks.push(task);
    bins[0].weight += task.estimatedMs || 1;
  }
  const chosen = bins.find((bin) => bin.index === index);
  return (chosen?.tasks || []).sort((a, b) => String(a.id).localeCompare(String(b.id)));
}
export function groupBy(items, fn) {
  const out = {};
  for (const item of items || []) {
    const key = fn(item);
    if (!out[key]) out[key] = [];
    out[key].push(item);
  }
  return out;
}
export function groupTasksByLane(tasks) {
  return Object.fromEntries(Object.entries(groupBy(tasks, (task) => task.lane || 'unspecified')).map(([lane, rows]) => [lane, rows.map((task) => task.id)]));
}
export function estimatePlan(tasks) {
  const estimatedMs = tasks.reduce((sum, task) => sum + (task.estimatedMs || 0), 0);
  const timeoutMs = tasks.reduce((sum, task) => sum + (task.timeoutMs || 0), 0);
  const lanes = {}; const tags = {}; const sizes = {}; const areas = {};
  for (const task of tasks) {
    lanes[task.lane || 'unspecified'] = (lanes[task.lane || 'unspecified'] || 0) + 1;
    sizes[task.size || 'unspecified'] = (sizes[task.size || 'unspecified'] || 0) + 1;
    for (const tag of task.tags || []) tags[tag] = (tags[tag] || 0) + 1;
    for (const area of task.areas || []) areas[area] = (areas[area] || 0) + 1;
  }
  return { taskCount: tasks.length, estimatedMs, timeoutMs, lanes, tags, sizes, areas };
}
export function estimateParallelPlan(tasks, jobs = 1) {
  const n = Math.max(1, Number(jobs) || 1);
  const workers = Array.from({ length: n }, (_, i) => ({ index: i + 1, timeMs: 0, tasks: [] }));
  const serialGroups = new Map();
  for (const task of tasks.slice().sort((a, b) => (b.estimatedMs || 1) - (a.estimatedMs || 1))) {
    workers.sort((a, b) => (a.timeMs - b.timeMs) || (a.index - b.index));
    let chosen = workers[0];
    if (task.parallelGroup) {
      const groupReady = serialGroups.get(task.parallelGroup) || 0;
      chosen = workers.slice().sort((a, b) => (Math.max(a.timeMs, groupReady) - Math.max(b.timeMs, groupReady)) || (a.index - b.index))[0];
      chosen.timeMs = Math.max(chosen.timeMs, groupReady);
      serialGroups.set(task.parallelGroup, chosen.timeMs + (task.estimatedMs || 1));
    }
    chosen.tasks.push(task.id);
    chosen.timeMs += task.estimatedMs || 1;
  }
  return { jobs: n, estimatedWallMs: Math.max(0, ...workers.map((w) => w.timeMs)), workers };
}
export function summarizeManifest(manifest) {
  const tasks = manifest.tasks || [];
  return { revision: manifest.revision, taskCount: tasks.length, plan: estimatePlan(tasks), lanes: groupTasksByLane(tasks) };
}
export function slowestTasks(results = [], count = 10) {
  return results.slice().sort((a, b) => (b.durationMs || 0) - (a.durationMs || 0) || String(a.id).localeCompare(String(b.id))).slice(0, count);
}
export function summarizeResults(tasks, results) {
  const byTask = new Map((tasks || []).map((task) => [task.id, task]));
  const rows = (results || []).map((result) => {
    const task = byTask.get(result.id) || {};
    const estimatedMs = task.estimatedMs || 0;
    const ratio = estimatedMs > 0 ? Number(((result.durationMs || 0) / estimatedMs).toFixed(3)) : null;
    return { id: result.id, status: result.status, lane: task.lane || 'unknown', size: task.size || 'unknown', areas: task.areas || [], estimatedMs, durationMs: result.durationMs || 0, estimateRatio: ratio, timedOut: Boolean(result.timedOut) };
  }).sort((a, b) => b.durationMs - a.durationMs || String(a.id).localeCompare(String(b.id)));
  const lanes = {}; const areas = {};
  for (const row of rows) {
    lanes[row.lane] ||= { count: 0, durationMs: 0, failed: 0 };
    lanes[row.lane].count += 1; lanes[row.lane].durationMs += row.durationMs;
    if (row.status !== 'passed') lanes[row.lane].failed += 1;
    for (const area of row.areas) {
      areas[area] ||= { count: 0, durationMs: 0, failed: 0 };
      areas[area].count += 1; areas[area].durationMs += row.durationMs;
      if (row.status !== 'passed') areas[area].failed += 1;
    }
  }
  return { taskCount: rows.length, slowest: rows.slice(0, 10), lanes, areas, estimateMisses: rows.filter((row) => row.estimateRatio != null && row.estimateRatio > 2).slice(0, 10) };
}
export function appendTimingHistory(existingHistory, report, { limit = 30 } = {}) {
  const history = existingHistory && typeof existingHistory === 'object' ? { ...existingHistory } : {};
  history.schema = 1; history.project = 'BrowserRT'; history.revision = report.revision; history.updatedAt = report.generatedAt;
  history.runs = Array.isArray(history.runs) ? history.runs.slice() : [];
  history.runs.push({ generatedAt: report.generatedAt, revision: report.revision, status: report.status, tier: report.options?.tier || null, taskCount: report.plan?.taskCount || report.tasks?.length || 0, durationMs: report.durationMs, effectiveJobs: report.options?.effectiveJobs || null, slowest: report.timingSummary?.slowest?.slice(0, 5) || [] });
  history.runs = history.runs.slice(-limit);
  return history;
}
export function validateManifest(manifest, { currentRevision } = {}) {
  const errors = [];
  if (!manifest || typeof manifest !== 'object') errors.push('manifest must be an object');
  if (manifest.schema !== TEST_FACILITY_SCHEMA_VERSION) errors.push('bad schema version');
  if (currentRevision && manifest.revision !== currentRevision) errors.push(`manifest revision ${manifest.revision} != ${currentRevision}`);
  if (!Array.isArray(manifest.tasks) || manifest.tasks.length === 0) errors.push('manifest.tasks must be a non-empty array');
  const ids = new Set();
  for (const task of manifest.tasks || []) {
    if (!task.id || typeof task.id !== 'string') errors.push('task missing string id');
    if (ids.has(task.id)) errors.push(`duplicate task id ${task.id}`);
    ids.add(task.id);
    if (!Array.isArray(task.command) || task.command.length === 0) errors.push(`${task.id} missing command array`);
    if (!Array.isArray(task.tiers) || task.tiers.length === 0) errors.push(`${task.id} missing tiers`);
    if (!Array.isArray(task.tags) || task.tags.length === 0) errors.push(`${task.id} missing tags`);
    if (!Array.isArray(task.areas) || task.areas.length === 0) errors.push(`${task.id} missing areas`);
    if (!task.lane) errors.push(`${task.id} missing lane`);
    if (!ALLOWED_SIZES.has(task.size)) errors.push(`${task.id} missing/invalid size`);
    if (!ALLOWED_ISOLATION.has(task.isolation)) errors.push(`${task.id} missing/invalid isolation`);
    if (!ALLOWED_FLAKE.has(task.flakiness || 'none')) errors.push(`${task.id} invalid flakiness`);
    if (!Number.isFinite(task.risk) || task.risk < 1 || task.risk > 5) errors.push(`${task.id} risk must be 1..5`);
    if (!Number.isFinite(task.estimatedMs) || task.estimatedMs < 1) errors.push(`${task.id} missing positive estimatedMs`);
    if (!Number.isFinite(task.timeoutMs) || task.timeoutMs < task.estimatedMs) errors.push(`${task.id} timeoutMs must be >= estimatedMs`);
    if (task.size && task.timeoutMs > DEFAULT_TASK_SIZE_TIMEOUTS[task.size] && !task.timeoutOverrideReason) errors.push(`${task.id} timeout exceeds size default without timeoutOverrideReason`);
    if (!Array.isArray(task.inputs) || task.inputs.length === 0) errors.push(`${task.id} missing input globs`);
    if (task.alwaysRun !== undefined && typeof task.alwaysRun !== 'boolean') errors.push(`${task.id} alwaysRun must be boolean when present`);
  }
  return errors;
}
export function validateImpactMap(impactMap, manifest, { currentRevision } = {}) {
  const errors = [];
  if (!impactMap || typeof impactMap !== 'object') errors.push('impact map must be an object');
  if (impactMap.schema !== 1) errors.push('impact map schema must be 1');
  if (currentRevision && impactMap.revision !== currentRevision) errors.push(`impact map revision ${impactMap.revision} != ${currentRevision}`);
  if (!Array.isArray(impactMap.rules) || impactMap.rules.length === 0) errors.push('impact map rules must be non-empty');
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id)); const ids = new Set();
  for (const rule of impactMap.rules || []) {
    if (!rule.id) errors.push('impact rule missing id');
    if (ids.has(rule.id)) errors.push(`duplicate impact rule id ${rule.id}`);
    ids.add(rule.id);
    if (!Array.isArray(rule.globs) || rule.globs.length === 0) errors.push(`${rule.id} missing globs`);
    if (!Array.isArray(rule.taskIds) || rule.taskIds.length === 0) errors.push(`${rule.id} missing taskIds`);
    for (const id of rule.taskIds || []) if (!taskIds.has(id)) errors.push(`${rule.id} references unknown task ${id}`);
  }
  return errors;
}
export function validateSurfaceInventory(surfaceInventory, manifest, { currentRevision } = {}) {
  const errors = [];
  if (!surfaceInventory || typeof surfaceInventory !== 'object') errors.push('surface inventory must be an object');
  if (surfaceInventory.schema !== 1) errors.push('surface inventory schema must be 1');
  if (currentRevision && surfaceInventory.revision !== currentRevision) errors.push(`surface inventory revision ${surfaceInventory.revision} != ${currentRevision}`);
  if (!Array.isArray(surfaceInventory.surfaces) || surfaceInventory.surfaces.length === 0) errors.push('surface inventory surfaces must be non-empty');
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id)); const ids = new Set();
  for (const surface of surfaceInventory.surfaces || []) {
    if (!surface.id) errors.push('surface missing id');
    if (ids.has(surface.id)) errors.push(`duplicate surface id ${surface.id}`);
    ids.add(surface.id);
    if (!surface.phase) errors.push(`${surface.id} missing phase`);
    if (!Array.isArray(surface.requiredEvidence) || surface.requiredEvidence.length === 0) errors.push(`${surface.id} missing requiredEvidence`);
    if (!Array.isArray(surface.currentTaskIds)) errors.push(`${surface.id} missing currentTaskIds`);
    for (const id of surface.currentTaskIds || []) if (!taskIds.has(id)) errors.push(`${surface.id} references unknown current task ${id}`);
  }
  return errors;
}
export function validateQuarantine(quarantine, manifest, { currentRevision } = {}) {
  const errors = [];
  if (!quarantine || typeof quarantine !== 'object') errors.push('quarantine must be an object');
  if (quarantine.schema !== 1) errors.push('quarantine schema must be 1');
  if (currentRevision && quarantine.revision !== currentRevision) errors.push(`quarantine revision ${quarantine.revision} != ${currentRevision}`);
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  if (!Array.isArray(quarantine.entries)) errors.push('quarantine.entries must be an array');
  for (const entry of quarantine.entries || []) {
    if (!taskIds.has(entry.taskId)) errors.push(`quarantine references unknown task ${entry.taskId}`);
    if (!entry.reason) errors.push(`quarantine entry ${entry.taskId} missing reason`);
    if (!entry.expiresAfterRevision) errors.push(`quarantine entry ${entry.taskId} missing expiresAfterRevision`);
  }
  return errors;
}
export function validateInventory(inventory) {
  const errors = [];
  if (!inventory || typeof inventory !== 'object') errors.push('inventory must be an object');
  if (!Array.isArray(inventory.families) || inventory.families.length === 0) errors.push('inventory.families must be non-empty');
  const ids = new Set();
  for (const family of inventory.families || []) {
    if (!family.id) errors.push('inventory family missing id');
    if (!Array.isArray(family.slices) || family.slices.length === 0) errors.push(`${family.id || 'family'} missing slices`);
    for (const slice of family.slices || []) {
      if (!slice.id) errors.push(`${family.id} slice missing id`);
      if (ids.has(slice.id)) errors.push(`duplicate inventory slice id ${slice.id}`);
      ids.add(slice.id);
      for (const field of ['status', 'cost', 'lane']) if (!slice[field]) errors.push(`${slice.id} missing ${field}`);
    }
  }
  return errors;
}
