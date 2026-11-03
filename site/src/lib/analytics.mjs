// Custom events contain categories and public paths, never free-form queries.
const events = {
  faq_search: ['result_count', 'query_length', 'query_intent'],
  faq_search_empty: ['query_length', 'query_intent'],
  faq_search_result_click: ['result_position', 'destination_path', 'query_intent'],
  faq_feedback_click: ['feedback_type', 'article_path'],
};
const intents = new Set(['error_code', 'adhesion', 'stringing', 'extrusion', 'warping', 'supports', 'other']);
export function trackUsage(name, values, target = globalThis.window) {
  if (!events[name] || typeof target?.gtag !== 'function') return;
  const params = {};
  for (const key of events[name]) {
    const value = values[key];
    if (key === 'query_intent' && intents.has(value)) params[key] = value;
    if (key === 'feedback_type' && ['case', 'correction'].includes(value)) params[key] = value;
    if (key.endsWith('_path') && typeof value === 'string' && /^\/(?:[a-z0-9-]+\/)*$/.test(value)) params[key] = value;
    if (['result_count', 'query_length', 'result_position'].includes(key) && Number.isSafeInteger(value) && value >= 0) params[key] = Math.min(value, 10000);
  }
  target.gtag('event', name, params);
}
