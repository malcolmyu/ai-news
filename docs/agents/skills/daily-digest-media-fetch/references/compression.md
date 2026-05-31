# Image Compression (Post-Download)

Always compress images after `fetch-daily-media.sh` runs. Raw Twitter images are often 100-300KB each, and some product screenshots are much wider than the cards need.

```bash
python3 -c "from PIL import Image, ImageFilter; import os
for f in os.listdir('docs/daily/assets/YYYY-MM-DD'):
    if not f.endswith('.jpg'): continue
    p=os.path.join('docs/daily/assets/YYYY-MM-DD',f)
    img=Image.open(p);img.load()
    if img.mode in ('P','RGBA','LA','CMYK'):img=img.convert('RGB')
    w,h=img.size
    if w<800: print(f'WARNING: {f} is only {w}px wide — consider re-downloading via wsrv.nl')
    elif w>1200:img=img.resize((800,int(h*800/w)),Image.LANCZOS)
    img=img.filter(ImageFilter.UnsharpMask(radius=1,percent=80,threshold=2))
    img.save(p,'JPEG',quality=85,optimize=True,progressive=True)
    print(f'{f}: {os.path.getsize(p)//1024}KB')"
```

**Target**: 800px wide for large images, quality 85, <100KB per image when possible, <600KB total for a typical daily.
**Why 800px**: Builder cards are often inspected on Retina displays and may span ~500-700px in desktop layouts. 400px/55q was visibly too soft.
**Mode fix**: Twitter images may be palette (P) mode — must `.convert('RGB')` before JPEG save.
**HTML rule**: after compression, keep intrinsic `width`/`height` attributes in the `<img>` tag. They allow the masonry layout to estimate item height before images finish decoding.
