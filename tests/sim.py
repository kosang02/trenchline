"""자동 전투 시뮬레이션. 실시간이 아니라 step()을 직접 돌려 빠르게 승패를 낸다.
python3 tests/sim.py [정책 이름 ...]  — 정책은 아래 POLICIES 참고."""
import http.server, threading, functools, os, sys, json
from playwright.sync_api import sync_playwright
root = os.path.join(os.path.dirname(__file__), '..', 'public')
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8798), functools.partial(http.server.SimpleHTTPRequestHandler, directory=root))
srv.RequestHandlerClass.log_message = lambda *a: None
threading.Thread(target=srv.serve_forever, daemon=True).start()
POLICIES = {
  # 아군 행동: 매 0.25초 판단. pick(T) → 뽑을 병과 or null, stance
  'rifle_rush': "T=>({pick:'rifle',stance:'advance'})",
  'rifle_hold': "T=>({pick:'rifle',stance:T.S.t<90?'hold':'advance'})",
  'smart': "T=>{const S=T.S,e=S.units.filter(u=>u.side===-1),m=S.units.filter(u=>u.side===1),c=k=>m.filter(u=>u.type===k).length,et=e.filter(u=>u.type==='tank').length;let k='rifle';if(et>c('at'))k='at';else if(c('mg')<Math.floor(m.length/5)+1)k='mg';else if(S.t>40&&c('mortar')<1+Math.floor(m.length/10))k='mortar';else if(c('assault')<Math.floor(m.length/6))k='assault';return {pick:k,stance:m.length<12&&S.t<100?'hold':'advance'}}",
  'smart2': "T=>{const S=T.S,e=S.units.filter(u=>u.side===-1),m=S.units.filter(u=>u.side===1),c=k=>m.filter(u=>u.type===k).length,et=e.filter(u=>u.type==='tank').length,v=a=>a.reduce((p,u)=>p+S.ST[u.side][u.type].cost,0);let k='rifle';if(et>c('at'))k='at';else if(c('mg')<Math.min(4,1+Math.floor(m.length/6)))k='mg';else if(S.t>40&&c('sniper')<1+Math.floor(m.length/12))k='sniper';else if(S.t>60&&c('mortar')<1)k='mortar';else if(c('assault')<Math.floor(m.length/5))k='assault';return {pick:k,stance:v(m)>v(e)*1.4+40?'advance':'hold'}}",
  'mixed': "T=>{const o=['rifle','rifle','mg','assault','rifle','at','mortar'];T.i=(T.i||0);const k=o[T.i%o.length];return {pick:k,stance:T.S.t<70?'hold':'advance',adv:true}}",
}
JS = """async ({pol,floor,n,type,patch,runx,cards})=>{const T=window.__TL,P=eval(%s),out=[];
 for(const k in (patch||{}))Object.assign(T.U[k],patch[k]);
 for(let k=0;k<n;k++){T.RUN=T.mkRun(runx);const node={id:'sim'+k,f:floor,i:0,n:1,type,next:[],seed:1000+k};
  T.startBattle(node);const S=T.S;S.paused=true;S.started=true;S.noLS=true;S.noEvents=true;const ctx={S,i:0};let acc=0;
  while(!S.over&&S.t<600){T.step(1/30);acc+=1/30;if(acc>=.25){acc=0;const a=P(ctx);T.setStance(a.stance);
     if(cards)for(const k of (T.RUN.loadout||[])){if((k!=='bar'&&k!=='howitzer')||!T.supReady(1,k))continue;const e=S.units.filter(u=>u.side===-1);let bx=null,by=0,bv=0;
       for(const u of e){let v=0;for(const w of e)if(Math.hypot(w.x-u.x,w.y-u.y)<(k==='bar'?26:16))v+=k==='bar'?1:S.ST[-1][w.type].cost;if(v>bv){bv=v;bx=u.x;by=u.y}}
       if(bx!=null&&(k==='bar'?bv>=3:bv>=60)){T.callSupport(1,k,bx,by);break}}
     const d=S.ST[1][a.pick];if(S.pts[1]>=d.cost&&!(S.cd[1][a.pick]>0)){T.spawn(1,a.pick);if(a.adv)ctx.i++}}}
  out.push({win:S.hq[-1]<=0,t:Math.round(S.t),hq:Math.round(S.hq[1]),k:S.kills,l:S.lost})}
 return out}"""
PATCH = json.loads(os.environ.get('PATCH','{}'))
RUNX = json.loads(os.environ.get('RUNX','{}'))  # 예: '{"perks":{"income":2},"relics":["coin"]}'
FLOORS = [(int(a),b) for a,b in (x.split(':') for x in os.environ['SIMF'].split(','))] if os.environ.get('SIMF') else [(0,'battle'),(4,'battle')] if os.environ.get('QUICK') else [(0,'battle'),(4,'battle'),(6,'elite'),(9,'boss')]
# 3막 작전: RUNX='{"floors":24}' SIMF='7:boss,15:boss,23:boss'. CARDS=1이면 출전 카드 중 포격·야포를 뭉친 적에게 쓴다(RUNX에 loadout 필요)
N = int(os.environ.get('N','6'))
pols = sys.argv[1:] or list(POLICIES)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:8798/')
    for pol in pols:
        for floor, typ in FLOORS:
            r = pg.evaluate(JS % POLICIES[pol], {'pol':pol,'floor':floor,'n':N,'type':typ,'patch':PATCH,'runx':RUNX,'cards':bool(os.environ.get('CARDS'))})
            w = sum(x['win'] for x in r); tt = sum(x['t'] for x in r)/len(r); hq = sum(x['hq'] for x in r)/len(r)
            print(f"{pol:11s} {floor+1:2d}층 {typ:6s} 승 {w}/{len(r)}  평균 {tt:5.0f}초  잔여 사령부 {hq:4.0f}")
    print('errors', errs[:3]); b.close()
srv.shutdown()
