const CACHE='maxime-agenda-v1';
const ROOT=new URL('./',self.location).href;
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll([ROOT, new URL('index.html',ROOT).href,...['install.js','manifest.webmanifest','icon-192.png','icon-512.png'].map(p=>new URL(p,ROOT).href)]))));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);
 if(event.request.method!=='GET'||url.origin!==self.location.origin||!url.href.startsWith(ROOT))return;
 event.respondWith((async()=>{
  const cache=await caches.open(CACHE);
  try{
   const response=await fetch(event.request);
   if(response.ok)await cache.put(event.request,response.clone());
   return response;
  }catch(error){
   const stored=await cache.match(event.request);
   if(stored)return stored;
   if(event.request.mode==='navigate')return (await cache.match(ROOT))||Response.error();
   return Response.error();
  }
 })());
});
