import numpy as np, cv2, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
W,H=1080,1350
F='/home/user/Claude/work/fonts/'
def font(name,size,wght=None):
    f=ImageFont.truetype(F+name,size)
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception as e: print('var fail',e)
    return f
GOLD=(226,182,112); CREAM=(246,232,214); RED=(190,40,40)

def background(seed, glow=(0.5,0.45), tone=0, floor=0.80):
    rng=np.random.default_rng(seed)
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    gx,gy=glow[0]*W,glow[1]*H
    d=np.sqrt(((xx-gx)/W)**2+((yy-gy)/H*0.8)**2)
    base=np.array([8,3,4],np.float32)
    wine=np.array([[120,18,26],[150,40,22]][tone],np.float32)
    amber=np.array([255,150,60],np.float32)
    g1=np.exp(-(d/0.42)**2)[...,None]; g2=np.exp(-(d/0.17)**2)[...,None]
    img=base+wine*g1*0.85+amber*g2*0.45
    # arabesque-like soft pattern (rotated squares lattice) very subtle
    p=(np.sin((xx+yy)/38)*np.sin((xx-yy)/38))
    img+= (p[...,None]*np.array([30,8,8])*np.exp(-(d/0.6)**2)[...,None])*0.35
    # floor: glossy dark surface
    fy=int(floor*H)
    t=np.clip((yy-fy)/(H-fy),0,1)[...,None]
    floorcol=np.array([14,5,6],np.float32)+wine*0.35*np.exp(-(d/0.5)**2)[...,None]
    m=(yy>=fy)[...,None]
    img=np.where(m,floorcol*(1-0.55*t)+amber*0.10*np.exp(-((xx-gx)/(W*0.35))**2)[...,None]*(1-t)**2,img)
    # horizon highlight line
    img+= (np.exp(-((yy-fy)/2.5)**2)[...,None]*np.array([120,70,40])*0.5)
    im=Image.fromarray(np.clip(img,0,255).astype(np.uint8)).convert('RGB')
    # bokeh
    bk=Image.new('RGB',(W,H),(0,0,0)); dr=ImageDraw.Draw(bk)
    for _ in range(46):
        x=rng.uniform(0,W); y=rng.uniform(0,fy*0.95); r=rng.uniform(10,46)
        a=rng.uniform(0.15,0.55); col=tuple(int(c*a) for c in (255,175,80))
        dr.ellipse((x-r,y-r,x+r,y+r),fill=col)
    bk=bk.filter(ImageFilter.GaussianBlur(7))
    im=ImageChops.add(im,bk.point(lambda v:int(v*0.55)))
    # golden dust (sharp small)
    dust=Image.new('RGB',(W,H),(0,0,0)); dr=ImageDraw.Draw(dust)
    for _ in range(140):
        x=rng.uniform(0,W); y=rng.uniform(0,H*0.95); r=rng.uniform(0.8,2.6); a=rng.uniform(0.3,1)
        dr.ellipse((x-r,y-r,x+r,y+r),fill=(int(255*a),int(200*a),int(120*a)))
    dust=dust.filter(ImageFilter.GaussianBlur(0.7))
    im=ImageChops.add(im,dust)
    return im

def smoke(im,seed,x0,y0,w,h,strength=0.5):
    rng=np.random.default_rng(seed)
    n=np.zeros((h//8+1,w//8+1),np.float32)
    for o,s in enumerate([8,16,32,64]):
        small=rng.random((h//s+2,w//s+2)).astype(np.float32)
        n+=cv2.resize(small,(n.shape[1],n.shape[0]),interpolation=cv2.INTER_CUBIC)/(o+1)
    n=cv2.resize(n,(w,h),interpolation=cv2.INTER_CUBIC); n=(n-n.min())/(n.max()-n.min())
    n=np.clip((n-0.45)*2.2,0,1)
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    mask=np.exp(-(((xx-w/2)/(w*0.45))**2+((yy-h*0.55)/(h*0.5))**2))
    win=np.clip(np.minimum(xx,w-xx)/(w*0.2),0,1)*np.clip(np.minimum(yy,h-yy)/(h*0.2),0,1)
    a=(n*mask*win*strength)[...,None]
    layer=np.array([255,160,110],np.float32)*a
    reg=np.array(im.crop((x0,y0,x0+w,y0+h))).astype(np.float32)
    im.paste(Image.fromarray(np.clip(reg+layer*0.5,0,255).astype(np.uint8)),(x0,y0))

def prep(path,height,mask_erode=1):
    p=Image.open(path).convert('RGBA')
    s=height/p.height
    p=p.resize((max(1,round(p.width*s)),height),Image.LANCZOS)
    a=np.array(p.split()[3])
    if mask_erode: a=cv2.erode(a,np.ones((3,3),np.uint8),iterations=mask_erode); a=cv2.GaussianBlur(a,(5,5),0)
    p.putalpha(Image.fromarray(a))
    rgb=p.convert('RGB').filter(ImageFilter.UnsharpMask(2,90,2))
    # warm grade + contrast to sit in the scene
    arr=np.array(rgb).astype(np.float32)/255
    arr=np.clip((arr-0.5)*1.06+0.5,0,1)
    arr[...,0]*=1.03; arr[...,2]*=0.93
    arr=np.clip(arr,0,1)
    rgb=Image.fromarray((arr*255).astype(np.uint8))
    rgb.putalpha(Image.fromarray(a)); return rgb

def place(im,prod,cx,base_y,rot=0,reflect=True,rim=True,shadow=True):
    prod=prod if not rot else prod.rotate(rot,Image.BICUBIC,expand=True)
    x=int(cx-prod.width/2); y=int(base_y-prod.height)
    if rim:  # warm rim glow behind
        a=prod.split()[3]
        glow=Image.new('RGBA',prod.size,(255,140,60,0)); glow.putalpha(a.point(lambda v:int(v*0.9)))
        g=Image.new('RGBA',im.size,(0,0,0,0)); g.paste(glow,(x,y))
        g=g.filter(ImageFilter.GaussianBlur(26)); 
        im.paste(g,(0,0),g.point(lambda v:int(v*0.55)) if False else g.split()[3].point(lambda v:int(v*0.45)))
    if shadow:
        sh=Image.new('L',im.size,0); d=ImageDraw.Draw(sh)
        d.ellipse((cx-prod.width*0.55,base_y-18,cx+prod.width*0.55,base_y+26),fill=210)
        sh=sh.filter(ImageFilter.GaussianBlur(16))
        im.paste(Image.new('RGB',im.size,(0,0,0)),(0,0),sh)
    if reflect:
        fl=prod.transpose(Image.FLIP_TOP_BOTTOM)
        arr=np.array(fl).astype(np.float32); hh=fl.height
        fade=np.clip(1-np.arange(hh)/(hh*0.55),0,1)**2*0.42
        arr[...,3]*=fade[:,None]
        fl=Image.fromarray(arr.astype(np.uint8),'RGBA').filter(ImageFilter.GaussianBlur(1.6))
        im.paste(fl,(x,int(base_y+4)),fl)
    im.paste(prod,(x,y),prod)
    return im

def add_light_streak(im,cx,y0,y1,w=300,a=0.18):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    m=np.exp(-((xx-cx)/w)**2)*np.clip(1-(yy-y0)/(y1-y0),0,1)*np.clip((yy-y0+200)/200,0,1)*(yy>=y0-200)
    arr=np.array(im).astype(np.float32)+m[...,None]*np.array([255,170,90])*a
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8))

def finish(im,seed):
    arr=np.array(im).astype(np.float32)
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    v=1-0.55*(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.75))**2)
    arr*=np.clip(v,0.25,1)[...,None]
    rng=np.random.default_rng(seed); arr+=rng.normal(0,3.2,(H,W,1))
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8))

def tw(d,text,f,sp=0):
    return sum(d.textlength(c,font=f)+sp for c in text)-sp
def text(d,xy,s,f,fill,sp=0,anchor='l'):
    x,y=xy; w=tw(d,s,f,sp)
    if anchor=='m': x-=w/2
    elif anchor=='r': x-=w
    for c in s:
        d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+sp
def gline(d,cx,y,w=160,col=GOLD):
    d.line((cx-w/2,y,cx+w/2,y),fill=col+(255,) if len(col)==3 else col,width=2)
    d.polygon([(cx,y-6),(cx+6,y),(cx,y+6),(cx-6,y)],fill=col)
def dots(d,cur,n=4,y=H-48):
    x0=W/2-(n-1)*18
    for i in range(n):
        d.ellipse((x0+i*36-5,y-5,x0+i*36+5,y+5),fill=GOLD if i==cur else (110,70,60))
def frame(d):
    d.rectangle((34,34,W-34,H-34),outline=(226,182,112,120),width=1)

def overlay(im): return im.convert('RGBA'), None
