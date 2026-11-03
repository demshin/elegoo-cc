import test from 'node:test';
import assert from 'node:assert/strict';
import { searchQuery } from '../site/src/lib/search-policy.mjs';
import { trackUsage } from '../site/src/lib/analytics.mjs';

test('symptom normalization preserves model and material qualifiers', () => {
  assert.deepEqual(searchQuery('  PETG не липнет CC2  '), { term: 'petg прилипание cc2', intent: 'adhesion' });
  assert.deepEqual(searchQuery('ошибка103'), { term: '103', intent: 'error_code' });
  assert.equal(searchQuery('КАНВАС').term, 'canvas');
  assert.equal(searchQuery('СС1 СС2').term, 'cc1 cc2');
  assert.equal(searchQuery('СС2 не подаёт').term, 'cc2 пропуски подачи');
  assert.equal(searchQuery('PLA 210°C').term, 'pla 210°c');
  assert.equal(searchQuery('не подаёт').intent, 'extrusion');
  assert.equal(searchQuery('').term, '');
});

test('analytics works without a configured tag and never forwards arbitrary input', () => {
  assert.doesNotThrow(() => trackUsage('faq_search', {}, {}));
  const calls = [];
  const target = { gtag: (...args) => calls.push(args) };
  trackUsage('unknown_event', {}, target);
  trackUsage('faq_search', { query_intent: 'adhesion', query_length: 9, result_count: 2, search_term: 'PRIVATE QUERY', email: 'PRIVATE EMAIL' }, target);
  trackUsage('faq_search_result_click', { query_intent: 'PRIVATE QUERY', result_position: -2, destination_path: '/faq/article/?token=PRIVATE' }, target);
  trackUsage('faq_feedback_click', { feedback_type: 'case', article_path: '/elegoo-cc/faq/first-layer-adhesion/' }, target);
  assert.deepEqual(calls, [
    ['event', 'faq_search', { result_count: 2, query_length: 9, query_intent: 'adhesion' }],
    ['event', 'faq_search_result_click', {}],
    ['event', 'faq_feedback_click', { feedback_type: 'case', article_path: '/elegoo-cc/faq/first-layer-adhesion/' }],
  ]);
  assert.ok(!JSON.stringify(calls).includes('PRIVATE'));
});

test('zero-result and result-click events keep only safe categories and paths', () => {
  const calls = [];
  const target = { gtag: (...args) => calls.push(args) };
  trackUsage('faq_search_empty', { query_intent: 'other', query_length: 10001, result_count: 0 }, target);
  trackUsage('faq_search_result_click', { query_intent: 'error_code', result_position: 1, destination_path: '/faq/centauri/heating-error-103/' }, target);
  assert.deepEqual(calls[0], ['event', 'faq_search_empty', { query_length: 10000, query_intent: 'other' }]);
  assert.equal(calls[1][2].destination_path, '/faq/centauri/heating-error-103/');
});
