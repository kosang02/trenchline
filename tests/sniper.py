"""저격수 압박 측정: 아군이 참호에서 사수(소총 6 + 기관총 1)하고, 적은 소총 4 + 저격수 K명이 사거리 밖에서 사수.
보급 정지, 아군은 2초마다 소총수 1명 증원(보급 속도와 같음), 90초 동안 아군이 잃은 CP와 적이 잃은 CP. PATCH로 U 수치 덮어쓰기.
실행: K=3 N=8 python3 tests/sniper.py"""
import http.server, threading, functools, os, json
from playwright.sync_api import sync_playwright
root = os.path.join(os.path.dirname(__file__), '..', 'public')
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8796), functools.partial(http.server.SimpleHTTPRequestHandler, directory=root))
srv.RequestHandlerClass.log_message = lambda *a: None
threading.Thread(target=srv.serve_forever, daemon=True).start()
PATCH = json.loads(os.environ.get('PATCH', '{}')); N = int(os.environ.get('N', '8')); K = int(os.environ.get('K', '3'))
JS = """({n,k,patch})=>{const T=window.__TL;for(const q in patch)Object.assign(T.U[q],patch[q]);const res=[];
 for(let r=0;r<n;r++){T.RUN=T.mkRun();T.startBattle({id:'s'+r,f:0,i:0,n:1,type:'battle',next:[],seed:11+r});const S=T.S;
  S.units.length=0;S.terrain.feats=[];S.nextFlare=1e9;S.ai.t=1e9;S.ai.supT=1e9;S.pts={1:0,'-1':0};S.payT={1:-1e9,'-1':-1e9};
  const tx=S.trench[1].x,ex=S.trench[3].x+40;
  const put=(side,type,cnt,x)=>{for(let i=0;i<cnt;i++){T.spawn(side,type,true);const u=S.units[S.units.length-1];u.x=x;u.y=62+((i*29+side*13)%88)}};
  put(1,'rifle',6,tx);put(1,'mg',1,tx);put(-1,'rifle',4,S.trench[3].x);put(-1,'sniper',k,ex);
  T.setStance('hold');S.stance[-1]='hold';
  const val=s=>S.units.filter(u=>u.side===s).reduce((p,u)=>p+S.ST[s][u.type].cost*u.hp/u.max,0);
  const p0=val(1),e0=val(-1);
  let sp=0,spent=0;const DUR=+(window.DUR||90);while(S.t<DUR){T.step(1/30);if(S.t>=sp){sp+=2;T.spawn(1,'rifle',true);spent+=10}}
  res.push({pl:p0+spent-val(1),el:e0-val(-1),p0})}
 return res}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto('http://127.0.0.1:8796/')
    r = pg.evaluate(JS, {'n': N, 'k': K, 'patch': PATCH})
    pl = sum(i['pl'] for i in r)/len(r); el = sum(i['el'] for i in r)/len(r)
    print(f"저격수 {K}명, 90초: 아군 손실 {pl:5.1f}/{r[0]['p0']:.0f} CP · 적 손실 {el:5.1f} CP")
    b.close()
srv.shutdown()
