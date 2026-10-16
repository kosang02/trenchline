# 참호전선 (Trench Line) — 작업 규칙

도트 그래픽 참호 줄다리기 RTS + 로그라이크. 사용자: 고상혁(kosang02). 이 문서는 이 저장소에서 일하는 모든 Claude 세션이 따른다.

## 역할
- **팀장 (Opus 세션)**: 모든 코드 작업(시스템, 구조, 기능, 버그, 스프라이트), 배포, 다른 세션 작업 검토와 최종 결정.
- **팀원 (Sonnet 세션)**: 기획과 밸런스 설계, 세계관·문구, 측정 결과 분석. 결과물은 `docs/`의 문서와 `NOTES.md`로 낸다.
  - 팀원은 `public/index.html`의 **데이터 값과 문구만** 직접 고칠 수 있다(`U`·`PERKS`·`RELICS`·`SUP`·`EVENTS`·`ORIGINS`·`RANKS`의 숫자와 텍스트, 번역 표 `I18N_EN`). 함수나 로직은 고치지 않는다.
  - 로직이 필요한 제안은 `NOTES.md`의 "팀장 확인 필요"에 적는다.

## 작업 순서 (충돌 방지)
1. 시작 전 반드시 `git checkout dev && git pull`.
2. 한 번에 한 세션만 `public/index.html`을 고친다. 사용자가 누구 차례인지 정한다.
3. 작고 의미 있는 단위로 커밋하고 바로 `git push`. 커밋 메시지는 한국어로, 무엇을 왜 바꿨는지.
4. 푸시 전 검사: `node --check`로 스크립트 문법 확인(아래 명령), 가능하면 `python3 tests/smoke.py`.
5. 끝나면 `NOTES.md`의 변경 기록에 한 줄 남긴다.

문법 검사(번역 표를 건드렸으면 `node tests/i18n_check.mjs`도):
```
sed -n '/<script>/,/<\/script>/p' public/index.html | sed '1d;$d' > /tmp/g.js && node --check /tmp/g.js
```

## 배포 (테스트 서버 → 실제 서버)
- **모든 작업은 `dev` 브랜치에 푸시한다.** dev에 푸시하면 테스트 서버 https://dev.playtrenchline.com 에 자동 배포된다(화면에 "테스트 서버" 표시, 세이브는 `dev:` 접두어로 분리).
- **`main`은 실제 유저가 쓰는 서버다**(https://playtrenchline.com, 옛 주소 trenchline.kosang0234.workers.dev도 유지). 사용자가 테스트 서버에서 확인하고 "배포해"라고 할 때만 `dev`를 `main`에 합쳐 푸시한다.
- GitHub Actions(`.github/workflows/deploy.yml`)가 문법 검사 후 배포한다. 저장소 Secret `CLOUDFLARE_API_TOKEN` 사용. 토큰은 절대 커밋하지 않는다.
- 세이브 호환성은 실제 유저가 있으므로 더 엄격히 지킨다. 필드 이름 변경·삭제 금지, 새 필드는 기본값.

## 파일 구조
- `public/index.html` — 게임 전체(HTML+CSS+JS 한 파일). 이게 유일한 원본.
- `src/index.js` — Worker: 정적 파일 + 세이브 API(`/api/ping`, `POST /api/account`, `GET|PUT /api/save/:code`). KV 바인딩 `SAVES`.
- `wrangler.toml` — Worker 설정. KV id는 비밀이 아니다.
- `tests/smoke.py` — 브라우저 스모크 테스트.
- `tests/sim.py` — 전략별 자동 전투 승률(`QUICK=1 N=8 PATCH='{"mg":{"hp":30}}' python3 tests/sim.py smart2`). `tests/duel.py` — 같은 CP 병과 대결. `tests/sniper.py` — 참호 사수 중 적 저격수 압박(`K=3 N=24`). `tests/assault.py` — 참호 돌파(`UNITS=rifle,flame D=10 BUDGET=150`). 3막 보스: `RUNX='{"floors":24}' SIMF='7:boss,15:boss,23:boss' python3 tests/sim.py smart2`. `CARDS=1`이면 출전 카드 중 포격·야포를 쓴다(RUNX에 `support`·`loadout`). 정책 `smart3`은 전차·돌격조를 뽑고 우세하면 총공세.
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
| 위생병·관측병 | `auxWant()`(위치), 치료는 `step()`의 healers, 관측은 `spotted()` |
| 수송차 | `APC_RIDE`(탑승 병과), `spawn()`(탑승), `apcCard()`, `apcStep()`/`apcUnload()`, `apcMax()`, `popCount()` |
| 작전 길이·막 | `FL()`(RUN.floors, 옛 세이브 10), `ACT`, `ACTS`, `genActMap()`, `nodeCfg()`(막별 diff·ehq, `ef`=0~9 환산 전선), 막 보스 승리 → `keystoneChoice()` |
| 적 지휘관 | `CMDRS`, `cmdOf()`, 효과는 `aiStep()`의 `CFG.cmd` 분기 |
| 유물 풀·희귀도 | `RELICS`의 `req`(병과·카드·특성 중 하나), `rar`(rare·key), `relicPool(src)`, `keystonePool()` |
| 생환병 | `VET_NAMES`, `VET_RANKS`, `vetsAfter()`, `vetDied()`, `RUN.vets`, `META.fallen` |
| 마지막 방어선·돌발 사건 | `lastStand()`/`applyLS()`, `fieldEvent()`/`grabCrate()` |
| 업적·오늘의 작전 | `ACH`/`checkAch()`(`META.ach`), `DAILY`/`showDaily()`(`RUN.daily`) |
| 사기·연쇄 사살 | `morale(side,d)`(`S.mor`, 붕괴 `S.rout`, 기세 `S.surgeT`), `onKill()`(사기·연쇄 `S.chain`·교리 보상), 총공세 `bigPush()`/`pushMax()`, 적 총반격 `S.eCounter` |
| 교리·백병전 | `PERKS[k].t`(inf·art·arm·def·mob·log), `DOCT`, `doctLv()`/`doct(t,n)`, `MELEE`(병과별 백병전 승률), 전설 특성 `PERKS[k].gold` |
| 가스·갱도·전투 명령 | `SUP.gas`/`SUP.tunnel`(`callSupport`, `S.gases`), `OBJ`(전투 명령), 역사 사건은 `EVENTS` 뒤쪽 + `giveSup()`/`givePerk()` |
| 적 AI | `aiStep()` |
| 사건 | `EVENTS` |
| 지형·바이옴 | `BIOMES`, `FEAT`, `genTerrain()`, `buildGround()` |
| 스프라이트 | `pixel sprites` 섹션 — 문자 격자 + 팔레트(`PAL`) |
| 번역(한/영) | `i18n` 섹션(스크립트 맨 위): `I18N_EN` 표, `LANG`, `_t()`, `translateDOM()`, `setLang()` |
| 저장 | `storage`, `cloud save` 섹션. localStorage 키 `trenchline.run/meta/code/savedAt` |

## 도트 규칙
- 모든 그림은 코드 안의 문자 격자다. 한 글자 = 1픽셀, `.`은 투명. 굽기(`bake`)는 게임이 시작할 때 한다.
- 전장은 2배 해상도(`SC=2`)로 그린다. 전장 스프라이트(`SPR`)는 굽고 나서 `epx()`(Scale2x)로 윤곽을 다듬어 2배가 되며, `lw`/`lh`가 월드 단위 크기다. 그림 좌표는 계속 월드 단위로 쓴다.
- 출신 그림: `ORIGIN_ART`에 24×14, 팔레트 `RELIC_PAL`. 사람 얼굴 대신 병과 무기를 그린다.
- 유닛: 높이 12px 안팎, 팔레트 `PAL[1]`(아군)·`PAL[-1]`(적)의 같은 글자를 써서 두 진영 색이 자동으로 갈리게 한다.
- 유물 아이콘: `RELIC_ICON`에 12×12, 팔레트 `RELIC_PAL`만 사용. 외곽선은 `k`(진한 갈색), 하이라이트 1~2픽셀. 새 유물을 추가하면 아이콘도 같이 넣는다. 없으면 ◆로 대체된다.
- 색을 새로 넣지 말고 기존 팔레트 글자를 쓴다. 꼭 필요하면 NOTES에 적고 팀장 확인.

## 번역 (한국어/영어)
- 언어: 저장값 `trenchline.lang`이 있으면 그것, 없으면 기기 언어가 한국어일 때 `ko`, 그 밖은 `en`. 첫 화면 버튼으로 바꾸면 새로고침된다.
- 화면에 나오는 새 문구는 반드시 `_t('한국어 원문')`으로 쓴다. 값이 들어가면 `_t('{0}명 남음', n)`처럼 자리표시를 쓴다. 정적 HTML 문구는 `translateDOM()`이 자동으로 바꾼다.
- `I18N_EN`은 한국어 원문 → 영어. 빈 값이면 한국어가 나온다. 자리표시 `{0}`·태그는 그대로 둔다.
- **한국어 문구를 고치면 표의 키도 같이 고친다.** 확인: `node tests/i18n_check.mjs` (표에 없음·안 쓰임·자리표시 불일치가 0이어야 한다).
- 번역된 글자를 로직 비교에 쓰지 않는다(`name===...` 금지). 구분은 id(`k`, `short` 등)로 한다.

## 지켜야 할 것
- 세이브 호환성: `RUN`/`META` 필드를 지우거나 이름을 바꾸지 않는다. 새 필드는 기본값을 둔다.
- 시드 재현성: 지도·지형 생성 안에서는 `seeded()` 밖의 난수를 쓰지 않는다.
- 색은 아군 올리브, 적 회청색 톤을 유지한다.
- 외부 라이브러리 없이 한 파일로 유지한다.
