"""Fit approved extracted pixels consistently; preserve each row's motion."""
import json
from pathlib import Path
from PIL import Image

root = Path(__file__).parent
records = []
for directory in sorted((root / 'qa/extracted').iterdir()):
    if not directory.is_dir():
        continue
    files = sorted(directory.glob('*.png'))
    frames = [Image.open(p).convert('RGBA') for p in files]
    scaled = [im.resize((163, 177), Image.Resampling.LANCZOS) for im in frames]
    bounds = [im.getchannel('A').point(lambda v: 255 if v > 16 else 0).getbbox() for im in scaled]
    ground = max(b[3] for b in bounds)
    offset = (14, 190 - ground)
    out = root / 'qa/frames' / directory.name
    out.mkdir(parents=True, exist_ok=True)
    for path, frame in zip(files, scaled):
        target = Image.new('RGBA', (192,208))
        target.alpha_composite(frame, offset)
        target.save(out / path.name)
    records.append({'state':directory.name,'shared_scale':[163/192,177/208],'translation':offset,'baseline':190})
(root/'qa/registration.json').write_text(json.dumps(records,indent=2))
