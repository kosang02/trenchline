// 참호전선 세이브 서버 — Cloudflare Worker + KV
// 계정 = 12자리 난수 코드(Crockford Base32, 약 60비트). 코드 자체는 저장하지 않고 SHA-256 해시를 키로 쓴다.
const ALPHABET = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
const CODE_RE = /^[0-9A-HJKMNP-TV-Z]{12}$/;
const MAX_BYTES = 256 * 1024;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });

function newCode() {
  const bytes = crypto.getRandomValues(new Uint8Array(12));
  let s = '';
  for (const b of bytes) s += ALPHABET[b & 31];
  return s;
}

async function keyFor(code, env) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode('trenchline:' + code));
  return (env.PREFIX || '') + 'save:' + [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    if (!path.startsWith('/api/')) return env.ASSETS.fetch(request);

    if (path === '/api/ping') return json({ ok: true });

    if (path === '/api/account' && request.method === 'POST') {
      for (let i = 0; i < 3; i++) {
        const code = newCode();
        const key = await keyFor(code, env);
        if (await env.SAVES.get(key)) continue;
        const now = Date.now();
        await env.SAVES.put(key, JSON.stringify({ savedAt: 0, createdAt: now, data: null }));
        return json({ code });
      }
      return json({ error: '코드 생성에 실패했습니다' }, 500);
    }

    const m = path.match(/^\/api\/save\/([^/]+)$/);
    if (m) {
      const code = decodeURIComponent(m[1]).toUpperCase();
      if (!CODE_RE.test(code)) return json({ error: '잘못된 코드 형식' }, 400);
      const key = await keyFor(code, env);
      let cur = await env.SAVES.get(key, 'json');
      // 개발자 슈퍼계정(GOAT-GOAT-GOAT): 처음 쓰면 빈 계정을 만든다. 서버 쪽 특권은 없다(DEV 도구는 클라이언트).
      if (!cur && code === 'G0ATG0ATG0AT') { cur = { savedAt: 0, createdAt: Date.now(), data: null }; await env.SAVES.put(key, JSON.stringify(cur)); }
      if (!cur) return json({ error: '계정 없음' }, 404);

      if (request.method === 'GET') return json({ savedAt: cur.savedAt || 0, data: cur.data });

      if (request.method === 'PUT') {
        const text = await request.text();
        if (text.length > MAX_BYTES) return json({ error: '세이브가 너무 큽니다' }, 413);
        let body;
        try { body = JSON.parse(text); } catch { return json({ error: 'JSON 형식 오류' }, 400); }
        const savedAt = Number(body.savedAt) || Date.now();
        if (savedAt < (cur.savedAt || 0)) return json({ ok: false, stale: true, savedAt: cur.savedAt }, 409);
        await env.SAVES.put(key, JSON.stringify({ ...cur, savedAt, data: body.data ?? null }));
        return json({ ok: true, savedAt });
      }
      return json({ error: '허용되지 않는 메서드' }, 405);
    }
    return json({ error: '없는 경로' }, 404);
  },
};
