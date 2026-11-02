// Test the generated Pagefind API directly, without a browser or network.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { dirname, resolve, relative } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

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
  for (const query of ['прилипание', 'влажный филамент', 'влажного филамента', 'поддержки', 'поддержка', 'поддержками', '103', '1243', 'TPU', 'CANVAS']) {
    const response = await pagefind.search(query);
    assert.ok(response.results.length > 0, `No results for ${query}`);
    const hits = await Promise.all(response.results.slice(0, 3).map(result => result.data()));
    for (const hit of hits) {
      assert.ok(hit.url.startsWith(`${base}/`), `Wrong project base: ${hit.url}`);
      assert.ok(!hit.url.includes('/sources/'), 'Evidence registry appeared in search');
    }
    if (query === 'влажный филамент') {
      assert.ok(hits.some(hit => hit.url.includes('drying-and-storage')), 'Drying guide missing from first results');
    }
    console.log(`${query}: ${response.results.length} results; first: ${hits[0].meta.title}`);
  }
} finally {
  await pagefind.destroy();
}
