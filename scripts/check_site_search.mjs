// Test the generated Pagefind API directly, without a browser or network.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { dirname, resolve, relative } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { searchQuery } from '../site/src/lib/search-policy.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dist = resolve(process.argv[2] || resolve(root, 'site/dist'));
const base = (process.env.SITE_BASE || '').replace(/\/$/, '');
const origin = 'https://local-search.invalid';
globalThis.fetch = async input => {
  const url = new URL(typeof input === 'string' ? input : input.url || input.href);
  assert.equal(url.origin, origin, 'Search attempted an unexpected network request');
  assert.ok(url.pathname.startsWith(`${base}/pagefind/`), url.href);
  const path = resolve(dist, `.${decodeURIComponent(url.pathname.slice(base.length))}`);
  assert.ok(!relative(dist, path).startsWith('..'), 'Search path left the build directory');
  return new Response(await readFile(path));
};
const pagefind = await import(pathToFileURL(resolve(dist, 'pagefind/pagefind.js')));
await pagefind.options({ basePath: `${origin}${base}/pagefind/`, baseUrl: `${base}/` });
try {
  const queries = [
    ['прилипание', 'first-layer-adhesion'], ['влажный филамент', 'drying-and-storage'],
    ['влажного филамента', 'drying-and-storage'], ['поддержки', 'support-removal'],
    ['поддержка', 'support-removal'], ['поддержками', 'support-removal'],
    ['103', 'heating-error-103'], ['1243', 'cc2-extrusion-1243'], ['TPU', 'tpu-feed-path'], ['CANVAS'],
    ['не липнет', 'first-layer-adhesion'], ['не прилипает', 'first-layer-adhesion'],
    ['сопли', 'drying-and-storage'], ['паутинка', 'drying-and-storage'],
    ['не тянет пластик', 'feed-resistance'], ['щелкает экструдер', 'feed-resistance'], ['отрывает углы', 'warping-and-brim'],
    ['поддержки не снимаются', 'support-removal'], ['ошибка103', 'heating-error-103'],
    ['канвас'], ['кентавр'],
  ];
  for (const [query, expected] of queries) {
    const normalized = searchQuery(query);
    const response = await pagefind.search(normalized.term);
    assert.ok(response.results.length > 0, `No results for ${query}`);
    const hits = await Promise.all(response.results.slice(0, 3).map(result => result.data()));
    for (const hit of hits) {
      assert.ok(hit.url.startsWith(`${base}/`), `Wrong project base: ${hit.url}`);
      assert.ok(!hit.url.includes('/sources/'), 'Evidence registry appeared in search');
    }
    if (expected) assert.ok(hits.some(hit => hit.url.includes(expected)), `${expected} missing from first three results for ${query}`);
    if (normalized.intent === 'adhesion') assert.ok(hits[0].url.includes('first-layer-adhesion'), `First-layer guide must lead the results for ${query}`);
    console.log(`${query}: ${response.results.length} results; first: ${hits[0].meta.title}`);
  }
  assert.equal((await pagefind.search('qzxqzxqzxqzxqzx')).results.length, 0);
} finally {
  await pagefind.destroy();
}
