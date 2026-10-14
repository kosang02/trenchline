"""스모크 테스트: 정적 서버로 게임을 띄워 전투 한 판을 ×4로 돌리고 페이지 오류가 없는지 본다.
실행: python3 tests/smoke.py   (playwright + chromium 필요)"""
import http.server, threading, functools, sys, os
from playwright.sync_api import sync_playwright
root = os.path.join(os.path.dirname(__file__), '..', 'public')
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8799), functools.partial(http.server.SimpleHTTPRequestHandler, directory=root))
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1200, 'height': 900})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:8799/'); pg.fill('#seedIn', 'SMOKE1'); pg.click('#bNew'); pg.click('.node.reach'); pg.click('#ovGo')
    for i in range(12): pg.keyboard.press(str(i % 4 + 1)); pg.wait_for_timeout(250)
    for _ in range(3): pg.keyboard.press('Tab')
    pg.wait_for_timeout(8000); pg.locator('.stage').screenshot(path='/tmp/trenchline-smoke.png'); b.close()
srv.shutdown()
print('page errors:', errs or 'none'); sys.exit(1 if errs else 0)
