const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async()=>{
  const [,,html,out]=process.argv; const FPS=30;
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+html); await p.evaluate(()=>document.fonts.ready);
  const dur=await p.evaluate(()=>window.DUR); const N=Math.round(dur*FPS);
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(FPS),'-i','-','-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-shortest','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  for(let i=0;i<N;i++){ await p.evaluate(t=>render(t),i/FPS); const buf=await p.screenshot({type:'png'}); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('frames',N);
})();
