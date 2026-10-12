#!/usr/bin/env python3
"""숫자숲 탐험대 웹앱(GitHub Pages) 빌드
- 입력: /home/claude/math-forest.html (테스트판과 같은 코드)
- 출력: dist/ (index.html, manifest.webmanifest, sw.js, 아이콘)
- 바뀌는 점: BUILD='web' (태블릿 기록 맞추기 켜짐), 완전한 HTML 문서, 홈 화면 설치·오프라인
사용: python3 build.py   (config.json에 Supabase 주소·공개 키를 넣으면 앱에 기본값으로 들어감)
"""
import json, os, re, shutil, hashlib, time
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = '/home/claude/math-forest.html'
DIST = os.path.join(HERE, 'dist')
cfg = {'url': '', 'key': ''}
cp = os.path.join(HERE, 'config.json')
if os.path.exists(cp):
    cfg.update(json.load(open(cp)))

src = open(SRC, encoding='utf-8').read()
assert "const BUILD='artifact';" in src
src = src.replace("const BUILD='artifact';", "const BUILD='web';")
src = src.replace("const SYNC_DEFAULT={url:'',key:''};",
                  "const SYNC_DEFAULT=" + json.dumps({'url': cfg['url'], 'key': cfg['key']}) + ";")

i = src.index('<div class="app">')
head, body = src[:i], src[i:]
ver = hashlib.sha1(src.encode()).hexdigest()[:10]

html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#EAF6EC">
<meta name="mobile-web-app-capable" content="yes">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-192.png">
<style>html,body{{margin:0}}:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}</style>
{head}
</head>
<body>
{body}
<script>
/* 홈 화면 앱: 오프라인에서도 열리게 서비스 워커 등록 */
if('serviceWorker' in navigator){{window.addEventListener('load',()=>{{navigator.serviceWorker.register('sw.js').catch(()=>{{}});}});}}
</script>
</body>
</html>
"""

if os.path.exists(DIST):
    shutil.rmtree(DIST)
os.makedirs(DIST)
open(os.path.join(DIST, 'index.html'), 'w', encoding='utf-8').write(html)

manifest = {
    "name": "숫자숲 탐험대",
    "short_name": "숫자숲",
    "description": "초등 연산 탐험 게임",
    "lang": "ko",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "any",
    "background_color": "#EAF6EC",
    "theme_color": "#EAF6EC",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
    ]
}
json.dump(manifest, open(os.path.join(DIST, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

sw = f"""/* 숫자숲 탐험대 서비스 워커 v{ver}
   - 앱 화면은 인터넷이 되면 새 버전을 받고, 안 되면 저장해 둔 것을 씀
   - 글꼴은 한 번 받으면 저장
   - 기록 맞추기(Supabase)는 저장하지 않고 항상 인터넷으로 */
const CACHE='numforest-{ver}';
const CORE=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png'];
self.addEventListener('install',e=>{{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()));}});
self.addEventListener('activate',e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));}});
self.addEventListener('fetch',e=>{{
  const req=e.request;if(req.method!=='GET')return;
  const u=new URL(req.url);
  if(u.hostname.endsWith('supabase.co'))return;
  if(req.mode==='navigate'||u.pathname.endsWith('index.html')){{
    e.respondWith(fetch(req).then(r=>{{const cl=r.clone();caches.open(CACHE).then(c=>c.put('index.html',cl));return r;}}).catch(()=>caches.match('index.html')));return;
  }}
  e.respondWith(caches.match(req).then(hit=>hit||fetch(req).then(r=>{{
    if(r.ok||r.type==='opaque'){{const cl=r.clone();caches.open(CACHE).then(c=>c.put(req,cl));}}return r;}})));
}});
"""
open(os.path.join(DIST, 'sw.js'), 'w', encoding='utf-8').write(sw)

# 아이콘: 솜구름 + 연두 배경
char = Image.open('/home/claude/assets/sorgureum.png').convert('RGBA')
def icon(size, pad, round_):
    bg = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(bg)
    if round_:
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.22), fill=(234, 246, 236, 255))
    else:
        d.rectangle([0, 0, size, size], fill=(234, 246, 236, 255))
    s = int(size * (1 - 2 * pad))
    c = char.resize((s, s), Image.LANCZOS)
    bg.alpha_composite(c, ((size - s) // 2, (size - s) // 2 + int(size * 0.02)))
    return bg
icon(192, 0.06, True).save(os.path.join(DIST, 'icon-192.png'))
icon(512, 0.06, True).save(os.path.join(DIST, 'icon-512.png'))
icon(512, 0.16, False).save(os.path.join(DIST, 'icon-maskable-512.png'))
shutil.copy(os.path.join(HERE, 'supabase-setup.sql'), os.path.join(DIST, 'supabase-setup.sql'))
open(os.path.join(DIST, '.nojekyll'), 'w').write('')
print('빌드 완료', ver, 'Supabase 기본값', '있음' if cfg['url'] else '없음 (앱 설정에서 입력)')
