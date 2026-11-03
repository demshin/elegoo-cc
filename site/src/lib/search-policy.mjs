// Keep the visible query intact; normalize only the term sent to Pagefind.
export function searchQuery(value) {
  const text = value.toLocaleLowerCase('ru').replaceAll('ё', 'е').trim().replace(/\s+/g, ' ')
    .replace(/канвас/g, 'canvas').replace(/кентавр/g, 'centauri')
    .replace(/(?<![\p{L}\p{N}])сс([12])(?![\p{L}\p{N}])/gu, 'cc$1');
  const code = text.match(/(?:ошибка\s*)?\b(103|502|703|1243)\b/);
  if (code) return { term: code[1], intent: 'error_code' };
  const rules = [
    [/не (?:липнет|прилипает)|не держится на (?:столе|пластине)|плохая адгезия/, 'прилипание', 'adhesion'],
    [/сопли|паутин(?:а|ка|ки|ку)/, 'паутина', 'stringing'],
    [/не (?:тянет пластик|подает)|щелкает экструдер/, 'пропуски подачи', 'extrusion'],
    [/(?:отрывает|загибает|поднимает) углы/, 'отрыв углов', 'warping'],
    [/поддержки не (?:снимаются|отделяются)|прилипли поддержки/, 'поддержки', 'supports'],
  ];
  for (const [pattern, replacement, intent] of rules) {
    if (pattern.test(text)) return { term: text.replace(pattern, replacement), intent };
  }
  return { term: text, intent: 'other' };
}
