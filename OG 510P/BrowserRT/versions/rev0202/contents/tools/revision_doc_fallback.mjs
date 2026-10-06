import { readFile } from 'node:fs/promises';
import { REVISION } from '../src/browserrt.mjs';

export function revisionDocCandidates(path, revision = REVISION) {
  const currentSuffix = `-${revision}.md`;
  if (!String(path).startsWith('docs/') || !String(path).endsWith(currentSuffix)) return [];
  const base = String(path).slice(0, -currentSuffix.length);
  const currentNumber = Number(revision.slice(3));
  const candidates = [];
  for (let n = currentNumber - 1; n >= 1; n -= 1) candidates.push(`${base}-rev${String(n).padStart(4, '0')}.md`);
  return candidates;
}

export async function resolveRevisionDocPath(path, options = {}) {
  const revision = options.revision || REVISION;
  try {
    await readFile(path, 'utf8');
    return { path, fallback: false };
  } catch (originalError) {
    for (const candidate of revisionDocCandidates(path, revision)) {
      try {
        await readFile(candidate, 'utf8');
        return { path: candidate, requestedPath: path, fallback: true };
      } catch {}
    }
    throw originalError;
  }
}

export async function readTextWithRevisionFallback(path, options = {}) {
  try {
    return await readFile(path, 'utf8');
  } catch (originalError) {
    for (const candidate of revisionDocCandidates(path, options.revision || REVISION)) {
      try {
        return await readFile(candidate, 'utf8');
      } catch {}
    }
    throw originalError;
  }
}
