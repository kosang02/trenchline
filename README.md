# 참호전선 (Trench Line)

도트 그래픽 참호전 로그라이크 웹 게임. 플레이: https://trenchline.kosang0234.workers.dev

- 게임: `public/index.html` 한 파일
- 세이브 서버: Cloudflare Worker(`src/index.js`) + Workers KV
- 계정: 12자리 난수 코드. 시작 화면에서 만들고, 다른 기기에서 코드로 불러온다.

작업 규칙과 코드 지도는 [CLAUDE.md](CLAUDE.md), 진행 상황은 [NOTES.md](NOTES.md).

## 직접 배포
```
npm install
npx wrangler login
npx wrangler deploy
```
