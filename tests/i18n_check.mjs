// 번역 표 검사: node tests/i18n_check.mjs
// - 코드/화면에 쓰였는데 표(I18N_EN)에 없는 문장  → 표에 추가해야 함
// - 표에 있는데 아무 데도 안 쓰는 문장          → 원문이 바뀐 것. 새 원문으로 키를 바꾼다
// - 자리표시({0}...)나 태그 수가 원문과 다른 번역 → 고쳐야 함
// - 아직 비어 있는 번역 수
import fs from 'fs';
const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
const si=html.indexOf('<script>')+8, src=html.slice(si,html.lastIndexOf('</script>'));
const a=src.indexOf('const I18N_EN={'), b=src.indexOf('\n};',a);
const table=Function('return '+src.slice(a+'const I18N_EN='.length,b+3))();
const code=src.slice(b+3), used=new Set();
for(const m of code.matchAll(/_t\((['"])((?:\\.|(?!\1).)*)\1/g)) used.add(Function('return '+m[1]+m[2]+m[1])());
const HAN=/[가-힣]/, head=html.slice(0,si);
for(const m of head.matchAll(/>([^<>]*)</g)){const k=m[1].trim();if(HAN.test(k))used.add(k)}
for(const m of head.matchAll(/(?:placeholder|aria-label|title)="([^"]*)"/g))if(HAN.test(m[1]))used.add(m[1]);
const missing=[...used].filter(k=>!(k in table)), unused=Object.keys(table).filter(k=>!used.has(k));
const sig=s=>[(s.match(/\{\d+\}/g)||[]).sort().join(),(s.match(/<\/?[a-z]+/g)||[]).sort().join()].join('|');
const bad=Object.entries(table).filter(([k,v])=>v&&sig(k)!==sig(v));
const empty=Object.values(table).filter(v=>!v).length;
const show=(t,l)=>{console.log(`\n[${t}] ${l.length}`);l.forEach(x=>console.log('  '+x))};
show('표에 없음',missing);show('안 쓰임',unused);show('자리표시/태그 불일치',bad.map(([k,v])=>k+'  →  '+v));
console.log(`\n번역 ${Object.keys(table).length-empty}/${Object.keys(table).length} 완료`);
process.exit(missing.length||bad.length?1:0);
