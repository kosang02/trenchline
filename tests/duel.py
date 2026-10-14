"""병과 비용 효율 측정: 같은 CP의 소총수 vs 병과 X를 개활지에서 붙인다(적 AI 생산 정지).
결과: X 쪽 승률과 남은 CP 비율. PATCH 환경변수로 U 수치를 덮어쓸 수 있다."""
import http.server, threading, functools, os, json
from playwright.sync_api import sync_playwright
root = os.path.join(os.path.dirname(__file__), '..', 'public')
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8797), functools.partial(http.server.SimpleHTTPRequestHandler, directory=root))
srv.RequestHandlerClass.log_message = lambda *a: None
threading.Thread(target=srv.serve_forever, daemon=True).start()
PATCH = json.loads(os.environ.get('PATCH', '{}')); BUDGET = int(os.environ.get('BUDGET', '200')); N = int(os.environ.get('N', '10'))
JS = """({x,budget,n,patch})=>{const T=window.__TL;for(const k in patch)Object.assign(T.U[k],patch[k]);const res=[];
 for(let k=0;k<n;k++){T.RUN=T.mkRun();T.startBattle({id:'d'+k,f:0,i:0,n:1,type:'battle',next:[],seed:7+k});const S=T.S;
  S.units.length=0;S.terrain.feats=[];S.trench.forEach(t=>{t.x=-999});S.nextFlare=1e9;S.ai.t=1e9;S.pts={1:0,'-1':0};S.payT={1:-1e9,'-1':-1e9};
  const put=(side,type,cnt,x)=>{for(let i=0;i<cnt;i++){T.spawn(side,type,true);const u=S.units[S.units.length-1];u.x=x+side*-(i%3)*6;u.y=60+((i*37)%90)}};
  const cr=Math.round(budget/S.ST[1].rifle.cost),cx=Math.max(1,Math.round(budget/S.ST[-1][x].cost));
  put(1,'rifle',cr,250);put(-1,x,cx,400);T.setStance('advance');S.stance[-1]='advance';
  while(S.t<240){T.step(1/30);const a=S.units.filter(u=>u.side===1).length,b=S.units.filter(u=>u.side===-1).length;if(!a||!b)break}
  const left=s=>S.units.filter(u=>u.side===s).reduce((p,u)=>p+S.ST[s][u.type].cost*u.hp/u.max,0);
  res.push({xw:!S.units.some(u=>u.side===1),xl:left(-1)/(cx*S.ST[-1][x].cost),rl:left(1)/(cr*S.ST[1].rifle.cost),cr,cx})}
 return res}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto('http://127.0.0.1:8797/')
    for x in ['rifle','assault','mg','at','sniper','mortar','tank']:
        r = pg.evaluate(JS, {'x': x, 'budget': BUDGET, 'n': N, 'patch': PATCH})
        w = sum(i['xw'] for i in r); xl = sum(i['xl'] for i in r)/len(r); rl = sum(i['rl'] for i in r)/len(r)
        print(f"소총수 {r[0]['cr']:2d} vs {x:7s} {r[0]['cx']:2d} | {x} 승 {w:2d}/{len(r)}  남은 CP {x} {xl:4.0%} / 소총 {rl:4.0%}")
    b.close()
srv.shutdown()
