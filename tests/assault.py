"""참호 돌파 측정: 적 소총수 D명이 참호를 지키고, 아군이 같은 CP(BUDGET)의 병과 X로 전진해 들어간다.
결과: 참호를 비운 비율, 남은 아군 CP. 실행: BUDGET=105 D=5 N=10 UNITS=rifle,assault,flame python3 tests/assault.py
혼성: UNITS="rifle:12,rifle:9+flame:1" MG=1 (적 참호에 기관총 1)"""
import http.server, threading, functools, os, json
from playwright.sync_api import sync_playwright
root = os.path.join(os.path.dirname(__file__), '..', 'public')
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8793), functools.partial(http.server.SimpleHTTPRequestHandler, directory=root))
srv.RequestHandlerClass.log_message = lambda *a: None
threading.Thread(target=srv.serve_forever, daemon=True).start()
PATCH=json.loads(os.environ.get('PATCH','{}'));BUDGET=int(os.environ.get('BUDGET','105'));D=int(os.environ.get('D','5'));N=int(os.environ.get('N','10'));MG=int(os.environ.get('MG','0'))
JS="""({x,budget,d,n,patch,mg})=>{const T=window.__TL;for(const k in patch)Object.assign(T.U[k],patch[k]);const res=[];
 for(let r=0;r<n;r++){T.RUN=T.mkRun();T.startBattle({id:'a'+r,f:0,i:0,n:1,type:'battle',next:[],seed:21+r});const S=T.S;
  S.units.length=0;S.terrain.feats=[];S.nextFlare=1e9;S.ai.t=1e9;S.ai.supT=1e9;S.pts={1:0,'-1':0};S.payT={1:-1e9,'-1':-1e9};
  const tr=S.trench[2];
  for(let i=0;i<d;i++){T.spawn(-1,'rifle',true);const u=S.units[S.units.length-1];u.x=tr.x;u.y=tr.y0+3+(tr.y1-tr.y0-6)*i/Math.max(1,d-1)}
  if(mg){T.spawn(-1,'mg',true);const u=S.units[S.units.length-1];u.x=tr.x;u.y=(tr.y0+tr.y1)/2;u.setupT=9}
  const comp=x.includes(':')?x.split('+').map(p=>{const [k,n]=p.split(':');return [k,+n]}):[[x,Math.max(1,Math.round(budget/S.ST[1][x].cost))]];
  let c=0,cost=0;for(const [k,n] of comp)for(let i=0;i<n;i++){T.spawn(1,k,true);const u=S.units[S.units.length-1];u.x=tr.x-70-(c%3)*5;u.y=tr.y0+3+(tr.y1-tr.y0-6)*((c*7)%11)/10;c++;cost+=S.ST[1][k].cost}
  T.setStance('advance');S.stance[-1]='hold';
  while(S.t<90){T.step(1/30);if(!S.units.some(u=>u.side===-1)||!S.units.some(u=>u.side===1))break}
  const left=S.units.filter(u=>u.side===1).reduce((p,u)=>p+S.ST[1][u.type].cost*u.hp/u.max,0);
  res.push({cleared:!S.units.some(u=>u.side===-1),left:left/cost,c,cost,t:S.t})}
 return res}"""
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();pg.goto('http://127.0.0.1:8793/')
    for x in os.environ.get('UNITS','rifle,assault,flame').split(','):
        r=pg.evaluate(JS,{'x':x,'budget':BUDGET,'d':D,'n':N,'patch':PATCH,'mg':MG})
        print(f"참호 소총수 {D}{'+기관총' if MG else ''} vs {x:18s} {r[0]['c']:2d}명 {r[0]['cost']}CP | 돌파 {sum(i['cleared'] for i in r):2d}/{len(r)}  남은 CP {sum(i['left'] for i in r)/len(r):4.0%}  {sum(i['t'] for i in r)/len(r):3.0f}초")
    b.close()
srv.shutdown()
