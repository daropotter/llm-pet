from pathlib import Path
from PIL import Image, ImageDraw
import json

r=Path(__file__).parent
a=Image.open(r/'final/spritesheet-extended.png').convert('RGBA')
spec=[('idle',6),('running-right',8),('running-left',8),('waving',4),('jumping',5),('failed',8),('waiting',6),('running',6),('review',6),('look-1',8),('look-2',8)]
out=r/'final/previews';out.mkdir(exist_ok=True)
all_frames=[];by_state={}
for row,(state,n) in enumerate(spec):
    frames=[]
    directory=out/'frames'/state;directory.mkdir(parents=True,exist_ok=True)
    for c in range(n):
        cell=a.crop((c*192,row*208,(c+1)*192,(row+1)*208))
        cell.save(directory/f'{c:02}.png')
        panel=Image.new('RGBA',(240,240),'#f2f2f2');panel.alpha_composite(cell,(24,22))
        ImageDraw.Draw(panel).text((8,6),f'{state} {c+1}/{n}',fill='#222222')
        frames.append(panel.convert('RGB'))
    by_state[state]=frames
    all_frames.extend(frames)
    frames[0].save(out/f'{state}.gif',save_all=True,append_images=frames[1:],duration=170,loop=0)
all_frames[0].save(out/'all-states.gif',save_all=True,append_images=all_frames[1:],duration=170,loop=0)
transition=by_state['idle']+by_state['jumping']+by_state['idle']
transition[0].save(out/'idle-jump-idle.gif',save_all=True,append_images=transition[1:],duration=170,loop=0)
looks=by_state['look-1']+by_state['look-2']
looks[0].save(out/'look-loop.gif',save_all=True,append_images=looks[1:],duration=170,loop=0)
stills=Image.new('RGB',(960,240),'white')
for i,(s,c) in enumerate([('idle',0),('waving',1),('jumping',2),('review',3)]):stills.paste(by_state[s][c],(i*240,0))
stills.save(out/'four-stills.png')
video=out/'video-frames';video.mkdir(exist_ok=True)
for i,im in enumerate(all_frames):im.save(video/f'{i:03}.png')
(out/'manifest.json').write_text(json.dumps({'source':str(r/'final/spritesheet-extended.png'),'frames':len(all_frames),'frame_duration_ms':170},indent=2))
