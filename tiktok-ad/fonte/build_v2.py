"""Builds ad2.html (voice-synced) from ad.html + cues.json, and writes timeline.json for the audio."""
import json, sys
src, cues_path, out_html, out_tl = sys.argv[1:5]
cues = json.load(open(cues_path))
C = [{"s": round(c["s"], 3), "e": round(c["e"], 3)} for c in cues["chunks"]]
P = {int(k): v for k, v in cues["phrases"].items()}
BAR = 2.25
NS = [0.0] + [round(P[k]["s"] - 0.3, 3) for k in (3, 4, 5, 6, 7, 8, 9)]
END = round(NS[7] + 3 * BAR + 0.9, 3)
NS.append(END)
OS = [0, 2.4, 4.6, 6.9, 9.1, 11.3, 13.6, 15.9, 20]
anch = []
for k in range(8):
    a, b, A, B = OS[k], OS[k + 1], NS[k], NS[k + 1]
    for o, n in ((a, A), (a + .8, A + .8), (b - .45, B - .45)):
        if not anch or (o > anch[-1][0] and n > anch[-1][1]): anch.append((round(o, 3), round(n, 3)))
anch.append((20.0, END))
TL = {"C": C, "NS": NS, "END": END, "anch": anch, "OS": OS}
json.dump(TL, open(out_tl, 'w'), indent=1)

s = open(src).read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)

# --- markup changes to match the spoken words ---
rep('<span class="line"><span>Feito para</span></span>', '<span class="line"><span>Feito pra</span></span>')
rep('<div class="tag" id="s3t" style="left:0;width:1080px;text-align:center;top:250px">Monitoramento 24h</div>',
    '<div class="tag" id="s3t" style="left:0;width:1080px;text-align:center;top:250px">Monitoramento de saúde</div>')
rep('font-size:84px"><span class="line"><span>Sua saúde, no pulso.</span></span></div>',
    'font-size:80px"><span class="line"><span>24 horas no seu pulso.</span></span></div>')
rep('<div class="sub" id="s3s" style="left:0;width:1080px;text-align:center;top:1400px">Batimentos · Oxigênio · Pressão · ECG</div>',
    '<div class="sub" id="s3s" style="left:0;width:1080px;text-align:center;top:1400px;font-size:40px;color:#fff;font-weight:700"><span id="k0">Batimento</span><span id="k1"> · Oxigênio</span><span id="k2"> · Pressão</span></div>')
rep('<span class="line"><span>Encosta.</span></span><span class="line"><span>Carrega.</span></span><span class="line"><span style="color:#ffb020">Sem fio.</span></span>',
    '<span class="line"><span>Carrega</span></span><span class="line"><span>sem fio.</span></span><span class="line"><span style="color:#ffb020">É só encostar.</span></span>')
rep('<span class="line"><span>Atenda ligações</span></span><span class="line"><span style="color:#6f95ff">pelo pulso.</span></span>',
    '<span class="line"><span>Atende ligação</span></span><span class="line"><span style="color:#6f95ff">direto do pulso.</span></span>')
rep('<div class="chip">Bluetooth</div><div class="chip">NFC</div><div class="chip">GPS</div><div class="chip">Voz</div>',
    '<div class="chip" id="ch0">Bluetooth</div><div class="chip" id="ch1">NFC</div><div class="chip" id="ch2">GPS</div>')
rep('<span class="line"><span>Uma pulseira.</span></span><span class="line"><span>Três estilos.</span></span>',
    '<span class="line"><span>Vem com duas</span></span><span class="line"><span>pulseiras extras</span></span><span class="line"><span style="color:#ff6a1a">e capinha!</span></span>')
rep('id="s7s" style="left:64px;top:530px;width:480px">2 pulseiras extras e capinha protetora já vêm na caixa.',
    'id="s7s" style="left:64px;top:640px;width:480px">Troque o estilo em segundos.')
rep('🛒 Toque e garanta o seu', '🛒 Toca no carrinho')
rep('<div class="info"><b>Frete grátis</b>', '<div class="info" id="inf1"><b>Frete grátis</b>')
rep('<div class="info" style="margin-top:8px">', '<div class="info" id="inf2" style="margin-top:8px">')

# --- timing: ambient layer runs on warped time, text runs on voice cues ---
rep("const DUR=20;", "const TL=" + json.dumps(TL) + ";\nconst DUR=TL.END;\n"
    "function warp(T){const A=TL.anch;if(T<=A[0][1])return A[0][0];for(let i=0;i<A.length-1;i++){const[a,b]=[A[i],A[i+1]];if(T<=b[1])return a[0]+(b[0]-a[0])*(T-a[1])/(b[1]-a[1]);}return A[A.length-1][0]+(T-A[A.length-1][1]);}")
rep("function fadeEl(", """function linesAt(el,t,starts,b){
  const ls=el.querySelectorAll('.line>span');
  ls.forEach((s,i)=>{const a=starts[Math.min(i,starts.length-1)];const pin=eExpo(prog(t,a,a+.55));s.style.transform=`translateY(${(1-pin)*110}%)`;});
  el.style.opacity=1-eIO(prog(t,b-.3,b)); el.style.filter=`blur(${eIO(prog(t,b-.3,b))*10}px)`;
  el.style.visibility=(t<starts[0]-.05||t>b)?'hidden':'visible';
}
function fadeEl(""")
rep("function render(t){", "function render(T){\n  const t=warp(T);")
rep("$('fade').style.opacity=1-eOut(prog(t,0,.35));", "$('fade').style.opacity=1-eOut(prog(T,0,.35));")
rep("const b1=prog(t,.15,1.6), b8=prog(t,16.0,17.0);", "const b1=prog(T,TL.C[0].s,TL.C[1].s+.45), b8=prog(t,16.0,17.0);")
rep("$('nav').style.opacity=eOut(prog(t,.3,1.0))*(1-eIO(prog(t,19.6,20)));", "$('nav').style.opacity=eOut(prog(t,.3,1.0));")

start = s.index("  // scenes\n"); stop = s.index("  // photo\n")
s = s[:start] + """  // scenes (voice-synced: C[i] = spoken chunk i)
  const C=TL.C, NS=TL.NS, L=.12, d=i=>C[i].e-C[i].s, at=(i,f)=>C[i].s+f*d(i)-L;
  linesAt($('s1h'),T,[at(2,0),at(2,.38),at(2,.72)],NS[1]);
  const c2=eExpo(prog(T,C[3].s,C[5].s+.3)); $('s2n').textContent=(lerp(0,2.02,c2)).toFixed(2).replace('.',',');
  fadeEl($('s2c'),T,NS[1]+.05,NS[2],60); linesAt($('s2h'),T,[at(3,0),at(5,0),at(5,.4)],NS[2]); fadeEl($('s2s'),T,C[5].e-.1,NS[2]);
  fadeEl($('s3t'),T,NS[2]+.1,NS[3]); linesAt($('s3h'),T,[at(9,0)],NS[3]); fadeEl($('s3s'),T,at(6,0),NS[3],20,.3);
  [6,7,8].forEach((ci,k)=>{const p=eOut(prog(T,at(ci,0),at(ci,0)+.3));$('k'+k).style.opacity=.15+.85*p;});
  const c4=eExpo(prog(T,C[10].s-.1,C[10].s+1.0)); $('s4n').textContent=Math.round(lerp(0,380,c4));
  fadeEl($('s4c'),T,NS[3]+.05,NS[4],60); linesAt($('s4h'),T,[at(10,0),at(10,.45),at(11,0)],NS[4]); fadeEl($('s4s'),T,C[11].e-.1,NS[4]);
  linesAt($('s5h'),T,[at(12,0),at(12,.48)],NS[5]); fadeEl($('s5c'),T,C[12].e-.35,NS[5]);
  [[0,C[12].e-.35],[1,at(13,.35)],[2,at(14,.25)]].forEach(([k,a])=>{const p=eOut(prog(T,a,a+.3));const el=$('ch'+k);el.style.opacity=p;el.style.transform=`translateY(${(1-p)*20}px)`;el.style.borderColor=p>0&&T<a+.6?'rgba(111,149,255,.9)':'rgba(255,255,255,.18)';});
""" + s[stop:]
start = s.index("  fadeEl($('s6t')"); stop = s.index("}\nwindow.render")
s = s[:start] + """  fadeEl($('s6t'),T,at(15,0),NS[6]); linesAt($('s6h'),T,[at(16,0),at(17,0)],NS[6]); fadeEl($('s6s'),T,C[17].e-.1,NS[6]);
  linesAt($('s7h'),T,[at(18,.1),at(18,.4),at(18,.74)],NS[7]); fadeEl($('s7s'),T,C[18].e-.2,NS[7]); fadeEl($('s7w'),T,NS[6]+.4,NS[7]);
  const swi=t<14.2?0:Math.min(2,Math.floor((t-14.2)/0.6+.4));
  for(let i=0;i<3;i++)$('sw'+i).style.borderColor=i===swi?'#fff':'transparent';
  linesAt($('s8h'),T,[NS[7]+.15],TL.END+1);
  const of=$('offer'); fadeEl(of,T,at(19,0),TL.END+1,80,.5);
  const pa=C[19].s+.25, pb=C[19].s+.5*d(19);
  const dp=eExpo(prog(T,pa,pb)); $('disc').textContent='-'+Math.round(80*dp)+'%';
  $('price').textContent=Math.round(lerp(259,53,eExpo(prog(T,pa,pb))));
  fadeEl($('inf1'),T,at(19,.68),TL.END+1,20,.35); fadeEl($('inf2'),T,at(19,.85),TL.END+1,20,.35);
  const ca=at(20,0); $('cta').style.opacity=eOut(prog(T,ca,ca+.3));
  $('cta').style.transform=`scale(${(.85+.15*eOut(prog(T,ca,ca+.3)))*(1+.04*Math.max(0,Math.sin((T-ca)*6)))})`;
""" + s[stop:]
open(out_html, 'w').write(s)
print(json.dumps({"NS": NS, "END": END}))
