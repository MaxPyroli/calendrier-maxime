if(location.protocol==='https:' && 'serviceWorker' in navigator){
 navigator.serviceWorker.register('./sw.js').catch(console.error);
 const button=document.createElement('button');button.textContent='Installer l’application';button.hidden=true;
 document.querySelector('nav').append(button);
 let prompt;
 window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();prompt=event;button.hidden=false;});
 button.addEventListener('click',async()=>{if(!prompt)return;await prompt.prompt();await prompt.userChoice;prompt=null;button.hidden=true;});
 window.addEventListener('appinstalled',()=>{prompt=null;button.hidden=true;});
 const status=document.createElement('p');status.textContent='Hors connexion : dernier agenda enregistré sur cet appareil.';
 document.querySelector('header').append(status);
 const update=()=>status.hidden=navigator.onLine;update();
 window.addEventListener('online',update);window.addEventListener('offline',update);
}
