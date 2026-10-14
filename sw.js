/* 숫자숲 탐험대 서비스 워커 v1a3ae44e40
   - 앱 화면은 인터넷이 되면 새 버전을 받고, 안 되면 저장해 둔 것을 씀
   - 글꼴은 한 번 받으면 저장
   - 기록 맞추기(Supabase)는 저장하지 않고 항상 인터넷으로 */
const CACHE='numforest-1a3ae44e40';
const CORE=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  const req=e.request;if(req.method!=='GET')return;
  const u=new URL(req.url);
  if(u.hostname.endsWith('supabase.co'))return;
  if(req.mode==='navigate'||u.pathname.endsWith('index.html')){
    e.respondWith(fetch(req).then(r=>{const cl=r.clone();caches.open(CACHE).then(c=>c.put('index.html',cl));return r;}).catch(()=>caches.match('index.html')));return;
  }
  e.respondWith(caches.match(req).then(hit=>hit||fetch(req).then(r=>{
    if(r.ok||r.type==='opaque'){const cl=r.clone();caches.open(CACHE).then(c=>c.put(req,cl));}return r;})));
});
