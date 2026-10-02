import numpy as np, cv2, glob
from PIL import Image
U={k:glob.glob(f'/root/.claude/uploads/*/{k}-image.webp')[0] for k in ['ce7a9f16','774e02e9','05be9c0e','b938e39b']}
def load(k): return np.array(Image.open(U[k]).convert('RGB'))
def gc(img, rect, bgthr=None, it=6):
    mask=np.full(img.shape[:2],cv2.GC_PR_BGD,np.uint8)
    x0,y0,x1,y1=rect
    mask[y0:y1,x0:x1]=cv2.GC_PR_FGD
    mask[:y0,:]=cv2.GC_BGD; mask[y1:,:]=cv2.GC_BGD; mask[:,:x0]=cv2.GC_BGD; mask[:,x1:]=cv2.GC_BGD
    b=np.zeros((1,65)); f=np.zeros((1,65))
    cv2.grabCut(img,mask,None,b,f,it,cv2.GC_INIT_WITH_MASK)
    m=((mask==1)|(mask==3)).astype(np.uint8)
    mx=img.max(2).astype(int); mn=img.min(2).astype(int)
    m[(mn>150)&((mx-mn)<45)]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    # keep largest component + fill holes
    n,l,s,_=cv2.connectedComponentsWithStats(m)
    if n>1: m=(l==1+np.argmax(s[1:,4])).astype(np.uint8)
    cnt,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    out=np.zeros_like(m); cv2.drawContours(out,cnt,-1,1,-1)
    return out
def save(name,img,m):
    ys,xs=np.where(m>0); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    a=cv2.GaussianBlur((m*255).astype(np.uint8),(3,3),0)
    rgba=np.dstack([img,a])[y0:y1,x0:x1]
    Image.fromarray(rgba).save(name); print(name,rgba.shape)
    # preview on magenta
    bg=np.zeros_like(rgba[:,:,:3]); bg[:]=(255,0,255)
    al=rgba[:,:,3:4]/255.
    Image.fromarray((rgba[:,:,:3]*al+bg*(1-al)).astype(np.uint8)).save(name.replace('.png','_prev.png'))
# image4 box+bottle
i=load('b938e39b'); save('p_box.png',i,gc(i,(30,40,478,472)))
# image3 bottle
i=load('05be9c0e'); save('p_info.png',i,gc(i,(5,100,240,420)))
# image2 side
i=load('774e02e9'); save('p_side.png',i,gc(i,(100,15,410,398)))
# image1 top
i=load('ce7a9f16'); save('p_top.png',i,gc(i,(20,40,425,478)))
