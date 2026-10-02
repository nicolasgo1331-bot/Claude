from build import *
import os
os.makedirs('out',exist_ok=True)
CIN=lambda s,w=600: font('Cinzel.ttf',s,w)
COR=lambda s,w=500: font('CormorantGaramond.ttf',s,w)
MON=lambda s,w=400: font('Montserrat.ttf',s,w)
def comp(im,ov): return Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB')
def panel(ov,box,r=18,fill=(20,6,8,170),outline=(226,182,112,150)):
    ImageDraw.Draw(ov).rounded_rectangle(box,r,fill=fill,outline=outline,width=1)

# ---------- 1: caja + frasco
im=background(1,glow=(0.5,0.52),floor=0.80)
smoke(im,11,60,500,960,560,0.55)
im=place(im,prep('p_box.png',700),540,int(0.80*H)+10)
im=add_light_streak(im,540,300,1080,w=380,a=0.10)
im=finish(im,1)
ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); frame(d)
text(d,(W/2,92),'EAU  DE  PARFUM',MON(22,500),GOLD,sp=8,anchor='m')
text(d,(W/2,140),'RAYHAAN',CIN(118,600),CREAM,sp=10,anchor='m')
gline(d,W/2,292,260)
text(d,(W/2,312),'C R I M S O N',CIN(36,500),GOLD,anchor='m')
text(d,(W/2,1168),'Calidez especiada que no pasa desapercibida',COR(40,500),CREAM,anchor='m')
text(d,(W/2,1236),'DESLIZÁ PARA DESCUBRIRLO  →',MON(20,500),GOLD,sp=5,anchor='m')
dots(d,0); comp(im,ov).save('out/slide1.png')

# ---------- 2: vista superior + notas
im=background(2,glow=(0.5,0.34),tone=1,floor=2.0)
smoke(im,22,100,60,880,700,0.5)
pr=prep('p_top.png',560)
# sombra proyectada (luz desde arriba-izquierda)
cx,cy=540,495
sh=Image.new('L',im.size,0); sh.paste(pr.split()[3].point(lambda v:int(v*0.9)),(int(cx-pr.width/2)+40,int(cy-pr.height/2)+46))
sh=sh.filter(ImageFilter.GaussianBlur(26)); im.paste(Image.new('RGB',im.size,(0,0,0)),(0,0),sh)
g=Image.new('RGBA',im.size,(0,0,0,0)); gl=Image.new('RGBA',pr.size,(255,140,60,255)); gl.putalpha(pr.split()[3].point(lambda v:int(v*0.8)))
g.paste(gl,(int(cx-pr.width/2),int(cy-pr.height/2))); g=g.filter(ImageFilter.GaussianBlur(30)); im.paste(g,(0,0),g.split()[3].point(lambda v:int(v*0.45)))
im.paste(pr,(int(cx-pr.width/2),int(cy-pr.height/2)),pr)
im=finish(im,2)
ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); frame(d)
text(d,(W/2,84),'SUS  NOTAS',CIN(58,600),CREAM,sp=8,anchor='m')
# grilla 3x2
notes=['CANELA','PIMIENTA ROSA','BENJUÍ','HABA TONKA','VAINILLA','CARDAMOMO']
cw,chh,gx,gy=290,120,22,22; x0=(W-(3*cw+2*gx))/2; y0=860
for i,n in enumerate(notes):
    r,c=divmod(i,3); bx=x0+c*(cw+gx); by=y0+r*(chh+gy)
    panel(ov,(bx,by,bx+cw,by+chh))
    d=ImageDraw.Draw(ov)
    d.polygon([(bx+cw/2,by+22),(bx+cw/2+7,by+29),(bx+cw/2,by+36),(bx+cw/2-7,by+29)],fill=GOLD)
    text(d,(bx+cw/2,by+56),n,CIN(27 if len(n)<12 else 24,600),CREAM,sp=2,anchor='m')
text(d,(W/2,1190),'Un viaje dulce, cálido y especiado',COR(38,500),GOLD,anchor='m')
text(d,(W/2,1258),'EL ORIGEN DE SU CARÁCTER',MON(18,500),(200,160,130),sp=5,anchor='m')
dots(d,1); comp(im,ov).save('out/slide2.png')

# ---------- 3: vista lateral + ocasión
im=background(3,glow=(0.5,0.45),floor=0.72)
smoke(im,33,40,380,1000,520,0.5)
im=place(im,prep('p_side.png',620),540,int(0.72*H)+8)
im=add_light_streak(im,540,300,970,w=350,a=0.10)
im=finish(im,3)
ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); frame(d)
text(d,(W/2,92),'EL  MOMENTO  IDEAL',MON(22,500),GOLD,sp=8,anchor='m')
text(d,(W/2,138),'Hecho para las noches',CIN(66,600),CREAM,anchor='m')
text(d,(W/2,222),'frescas de otoño e invierno',COR(46,500),GOLD,anchor='m')
occ=[('CITAS','nocturnas'),('CENAS','y eventos'),('SALIDAS','elegantes')]
cw,chh,gx=300,140,24; x0=(W-(3*cw+2*gx))/2; y0=1090
for i,(a,b) in enumerate(occ):
    bx=x0+i*(cw+gx); panel(ov,(bx,y0,bx+cw,y0+chh))
d=ImageDraw.Draw(ov)
for i,(a,b) in enumerate(occ):
    bx=x0+i*(cw+gx)
    text(d,(bx+cw/2,y0+34),a,CIN(34,600),CREAM,sp=3,anchor='m')
    text(d,(bx+cw/2,y0+84),b,COR(34,500),GOLD,anchor='m')
text(d,(W/2,1252),'Mejor en clima frío · Aroma de carácter',MON(18,500),(200,160,130),sp=3,anchor='m')
dots(d,2); comp(im,ov).save('out/slide3.png')

# ---------- 4: ficha
im=background(4,glow=(0.28,0.4),floor=0.60)
smoke(im,44,0,260,560,520,0.45)
im=place(im,prep('p_info.png',520),285,int(0.60*H)+6)
im=finish(im,4)
ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); frame(d)
text(d,(W/2,84),'RAYHAAN  CRIMSON',CIN(54,600),CREAM,sp=6,anchor='m')
text(d,(W/2,160),'EAU DE PARFUM · FICHA DEL PERFUME',MON(18,500),GOLD,sp=5,anchor='m')
gline(d,W/2,214,200)
text(d,(750,262),'ACORDES PRINCIPALES',MON(18,600),GOLD,sp=4,anchor='m')
acc=[('cálido especiado',1.0,(214,66,10),(255,244,230)),('avainillado',0.84,(252,238,176),(70,45,20)),
     ('canela',0.74,(226,150,92),(60,25,10)),('ámbar',0.68,(212,126,80),(60,25,10)),('especiado suave',0.58,(240,176,150),(70,30,20))]
bx0,bw,bh,gap,by0=520,500,56,16,300
for i,(n,k,c,tc) in enumerate(acc):
    y=by0+i*(bh+gap); d.rounded_rectangle((bx0,y,bx0+bw*k,y+bh),10,fill=c+(255,))
    text(d,(bx0+bw*k/2,y+14),n,MON(24,600),tc,anchor='m')
# stats
cards=[('DURACIÓN','8 hs','aprox. sobre la piel'),('ESTELA','Fuerte','se deja notar'),('IDEAL PARA','Noche','otoño · invierno')]
cw,chh,gx=300,260,24; x0=(W-(3*cw+2*gx))/2; y0=930
for i in range(3):
    bx=x0+i*(cw+gx); panel(ov,(bx,y0,bx+cw,y0+chh))
d=ImageDraw.Draw(ov)
for i,(a,b,c) in enumerate(cards):
    bx=x0+i*(cw+gx)
    text(d,(bx+cw/2,y0+34),a,MON(19,600),GOLD,sp=5,anchor='m')
    text(d,(bx+cw/2,y0+78),b,CIN(66 if len(b)<6 else 54,600),CREAM,anchor='m')
    text(d,(bx+cw/2,y0+170),c,COR(30,500),(214,190,160),anchor='m')
    if i==1:
        for j in range(5): d.rounded_rectangle((bx+cw/2-70+j*30,y0+214,bx+cw/2-48+j*30,y0+226),4,fill=GOLD if j<5 else (90,60,50))
    if i==2: pass
text(d,(W/2,1250),'Consultá disponibilidad y hacé tu pedido por DM',MON(20,500),CREAM,sp=1,anchor='m')
dots(d,3,y=H-32); comp(im,ov).save('out/slide4.png')
