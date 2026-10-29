import json, numpy as np, torch, sys, subprocess
from pathlib import Path
from PIL import Image
from spandrel import ModelLoader
P = Path('/tmp/work/n2/f1/prep')
m = ModelLoader().load_from_file('/tmp/work/models/realesr-general-x4v3.pth').eval()
torch.set_num_threads(4)
for i, off, n in json.load(open(P / 'crops.json')):
    src = P / f'crop{i}'; dst = P / f'hq{i}'; dst.mkdir(exist_ok=True)
    for f in sorted(src.glob('*.png')):
        o = dst / f.name
        if o.exists(): continue
        im = Image.open(f).convert('RGB')
        x = torch.from_numpy(np.array(im)).permute(2, 0, 1).float().div(255)[None]
        with torch.no_grad(): y = m(x)[0].clamp(0, 1).permute(1, 2, 0).numpy()
        up = Image.fromarray((y * 255).round().astype('uint8')).resize((1080, 1920), Image.LANCZOS)
        base = im.resize((1080, 1920), Image.LANCZOS)
        Image.blend(base, up, 0.55).save(o)
        print(i, f.name, flush=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', str(dst / '%05d.png'), '-vf',
                    'unsharp=5:5:0.6:5:5:0,noise=alls=4:allf=t,eq=contrast=1.05:saturation=1.07', '-c:v', 'libx264', '-crf', '12',
                    '-preset', 'slow', '-pix_fmt', 'yuv420p', str(P / f'hq{i}.mp4')], check=True)
print('FIM')
