const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async()=>{
  const [,,html,base,out]=process.argv; const FPS=30;
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+html); await p.evaluate(()=>document.fonts.ready);
  const dur=await p.evaluate(()=>window.DUR); const N=Math.round(dur*FPS);
  const ff=spawn('ffmpeg',['-y','-v','error','-i',base,'-f','image2pipe','-framerate',String(FPS),'-c:v','png','-i','-','-filter_complex','[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]','-map','[v]','-c:v','libx264','-preset','slow','-crf','17','-profile:v','high','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  for(let i=0;i<N;i++){ await p.evaluate(t=>render(t),i/FPS); const buf=await p.screenshot({type:'png',omitBackground:true}); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('frames',N);
})();
