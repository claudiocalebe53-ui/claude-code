"""Builds the real-footage base video (1080x1920) cut to the narration scenes."""
import json, subprocess, sys
src, tl_path, out, segs_out = sys.argv[1:5]
TL = json.load(open(tl_path)); NS = TL['NS']; END = TL['END']
d = [NS[i + 1] - NS[i] for i in range(8)]
q = d[7] / 4
# (src_start, src_end, dst_dur, z0, z1, cx, cy)
S = [
    (0.0, 2.0, d[0], 1.00, 1.12, .42, .40),
    (12.4, 14.3, d[1], 1.22, 1.38, .48, .42),
    (6.6, 9.6, d[2], 1.15, 1.00, .45, .45),
    (4.0, 5.4, d[3], 1.00, 1.10, .40, .45),
    (9.6, 12.4, d[4], 1.08, 1.20, .40, .45),
    (2.0, 4.0, d[5], 1.20, 1.05, .45, .38),
    (14.3, 16.7, d[6], 1.00, 1.10, .50, .45),
    (5.4, 6.6, q, 1.10, 1.20, .42, .42),
    (16.7, 18.0, q, 1.00, 1.10, .45, .40),
    (12.6, 14.2, q, 1.15, 1.25, .48, .42),
    (7.5, 8.7, END - NS[7] - 3 * q, 1.00, 1.10, .50, .38),
]
fc, labels = [], []
for i, (a, b, dd, z0, z1, cx, cy) in enumerate(S):
    sp = (b - a) / dd; n = max(1, round(dd * 30))
    fc.append(f"[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp:.5f},minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1,tpad=stop_mode=clone:stop_duration=1,"
              f"trim=end_frame={n},setpts=N/30/TB,scale=2160:2460:flags=lanczos,"
              f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':d=1:x='{cx}*iw-iw/zoom/2':y='{cy}*ih-ih/zoom/2':s=1080x1230:fps=30,"
              f"unsharp=5:5:0.6,setsar=1[s{i}]")
    labels.append(f"[s{i}]")
fc.append("".join(labels) + f"concat=n={len(S)}:v=1:a=0,split[fg][bgs]")
fc.append("[bgs]scale=-2:1920,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.28:saturation=0.8[bg]")
fc.append("[bg][fg]overlay=0:330,format=yuv420p[v]")
cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", ";".join(fc), "-map", "[v]", "-r", "30",
       "-c:v", "libx264", "-preset", "medium", "-crf", "14", out]
subprocess.run(cmd, check=True)
cuts, t = [], 0.0
for s in S: cuts.append(round(t, 3)); t += s[2]
json.dump({"cuts": cuts}, open(segs_out, "w"))
print("cuts", cuts)
