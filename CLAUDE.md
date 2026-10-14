# 참호전선 (Trench Line) — 작업 규칙

도트 그래픽 참호 줄다리기 RTS + 로그라이크. 사용자: 고상혁(kosang02). 이 문서는 이 저장소에서 일하는 모든 Claude 세션이 따른다.

## 역할
- **팀장 (Opus 세션)**: 모든 코드 작업(시스템, 구조, 기능, 버그, 스프라이트), 배포, 다른 세션 작업 검토와 최종 결정.
- **팀원 (Sonnet 세션)**: 기획과 밸런스 설계, 세계관·문구, 측정 결과 분석. 결과물은 `docs/`의 문서와 `NOTES.md`로 낸다.
  - 팀원은 `public/index.html`의 **데이터 값과 문구만** 직접 고칠 수 있다(`U`·`PERKS`·`RELICS`·`SUP`·`EVENTS`·`ORIGINS`·`RANKS`의 숫자와 텍스트). 함수나 로직은 고치지 않는다.
  - 로직이 필요한 제안은 `NOTES.md`의 "팀장 확인 필요"에 적는다.

## 작업 순서 (충돌 방지)
1. 시작 전 반드시 `git checkout dev && git pull`.
2. 한 번에 한 세션만 `public/index.html`을 고친다. 사용자가 누구 차례인지 정한다.
3. 작고 의미 있는 단위로 커밋하고 바로 `git push`. 커밋 메시지는 한국어로, 무엇을 왜 바꿨는지.
4. 푸시 전 검사: `node --check`로 스크립트 문법 확인(아래 명령), 가능하면 `python3 tests/smoke.py`.
5. 끝나면 `NOTES.md`의 변경 기록에 한 줄 남긴다.

문법 검사:
```
sed -n '/<script>/,/<\/script>/p' public/index.html | sed '1d;$d' > /tmp/g.js && node --check /tmp/g.js
```

## 배포 (테스트 서버 → 실제 서버)
- **모든 작업은 `dev` 브랜치에 푸시한다.** dev에 푸시하면 테스트 서버 https://trenchline-dev.kosang0234.workers.dev 에 자동 배포된다(화면에 "테스트 서버" 표시, 세이브는 `dev:` 접두어로 분리).
- **`main`은 실제 유저가 쓰는 서버다**(https://trenchline.kosang0234.workers.dev). 사용자가 테스트 서버에서 확인하고 "배포해"라고 할 때만 `dev`를 `main`에 합쳐 푸시한다.
- GitHub Actions(`.github/workflows/deploy.yml`)가 문법 검사 후 배포한다. 저장소 Secret `CLOUDFLARE_API_TOKEN` 사용. 토큰은 절대 커밋하지 않는다.
- 세이브 호환성은 실제 유저가 있으므로 더 엄격히 지킨다. 필드 이름 변경·삭제 금지, 새 필드는 기본값.

## 파일 구조
- `public/index.html` — 게임 전체(HTML+CSS+JS 한 파일). 이게 유일한 원본.
- `src/index.js` — Worker: 정적 파일 + 세이브 API(`/api/ping`, `POST /api/account`, `GET|PUT /api/save/:code`). KV 바인딩 `SAVES`.
- `wrangler.toml` — Worker 설정. KV id는 비밀이 아니다.
- `tests/smoke.py` — 브라우저 스모크 테스트.
- `tests/sim.py` — 전략별 자동 전투 승률(`QUICK=1 N=8 PATCH='{"mg":{"hp":30}}' python3 tests/sim.py smart2`). `tests/duel.py` — 같은 CP 병과 대결.
- 게임 끝의 `window.__TL`은 테스트 전용 훅이다. 게임 로직에서 쓰지 않는다.

## index.html 지도 (섹션 주석 `/* ---------- 이름 ---------- */` 기준)
| 무엇 | 어디 |
|---|---|
| 병과 수치 | `const U={...}` (cost, hp, dmg, range, rof=발사 간격, acc, cd=재배치 대기) |
| 특성 / 유물 / 영구 강화 | `PERKS`, `RELICS`, `META_UP` |
| 특성·유물 효과 적용 | `buildStats()`(스탯), `newGame()`(전투 시작값), `hit()`/`hitChance()`(전투 중) |
| 보급(CP) | `PAY_INT`, `PAY_BASE`, `payInterval()`, `payAmount()`, 증강 `surge()`(60초마다 +20%) |
| 지원 카드 | `SUP`(수치), `SUP_ORDER`, `SUP_ICON`, `callSupport()`(효과), `supCd()`, 적 사용은 `aiStep()` 끝부분. 보유 `RUN.support`, 출전 `RUN.loadout`(슬롯 `supSlots()`) |
| 출신·등급 | `ORIGINS`, `RANKS`, `rk()`(현재 등급), `startSetup()`→`pickRank()`→`newRun(origin,rank)`. 기록 `META.rank`(열린 등급), `META.clears`("출신:등급") |
| 적 난이도 | `startBattle()`의 `CFG.diff`(보급 배율), `buildStats()`의 적 분기 |
| 적 AI | `aiStep()` |
| 사건 | `EVENTS` |
| 지형·바이옴 | `BIOMES`, `FEAT`, `genTerrain()`, `buildGround()` |
| 스프라이트 | `pixel sprites` 섹션 — 문자 격자 + 팔레트(`PAL`) |
| 저장 | `storage`, `cloud save` 섹션. localStorage 키 `trenchline.run/meta/code/savedAt` |

## 도트 규칙
- 모든 그림은 코드 안의 문자 격자다. 한 글자 = 1픽셀, `.`은 투명. 굽기(`bake`)는 게임이 시작할 때 한다.
- 전장은 2배 해상도(`SC=2`)로 그린다. 전장 스프라이트(`SPR`)는 굽고 나서 `epx()`(Scale2x)로 윤곽을 다듬어 2배가 되며, `lw`/`lh`가 월드 단위 크기다. 그림 좌표는 계속 월드 단위로 쓴다.
- 출신 그림: `ORIGIN_ART`에 24×14, 팔레트 `RELIC_PAL`. 사람 얼굴 대신 병과 무기를 그린다.
- 유닛: 높이 12px 안팎, 팔레트 `PAL[1]`(아군)·`PAL[-1]`(적)의 같은 글자를 써서 두 진영 색이 자동으로 갈리게 한다.
- 유물 아이콘: `RELIC_ICON`에 12×12, 팔레트 `RELIC_PAL`만 사용. 외곽선은 `k`(진한 갈색), 하이라이트 1~2픽셀. 새 유물을 추가하면 아이콘도 같이 넣는다. 없으면 ◆로 대체된다.
- 색을 새로 넣지 말고 기존 팔레트 글자를 쓴다. 꼭 필요하면 NOTES에 적고 팀장 확인.

## 지켜야 할 것
- 세이브 호환성: `RUN`/`META` 필드를 지우거나 이름을 바꾸지 않는다. 새 필드는 기본값을 둔다.
- 시드 재현성: 지도·지형 생성 안에서는 `seeded()` 밖의 난수를 쓰지 않는다.
- 색은 아군 올리브, 적 회청색 톤을 유지한다.
- 외부 라이브러리 없이 한 파일로 유지한다.
