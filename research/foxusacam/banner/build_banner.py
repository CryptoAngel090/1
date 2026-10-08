from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance,ImageChops
import numpy as np, random, math
random.seed(7); np.random.seed(7)
F='fonts/'; W,H=2560,1440; BG=(8,8,10); RED=(0xE3,0x26,0x2E); WHITE=(246,244,240); GREY=(165,165,172)
SX0,SY0,SX1,SY1=507,508,2053,931
def grade(im, tint=(1.0,0.55,0.55), dark=0.45, blur=16):
    im=im.convert('RGB').filter(ImageFilter.GaussianBlur(blur))
    a=np.array(im).astype(float)/255
    lum=a.mean(2,keepdims=True)
    a=a*0.6+lum*0.4                      # desaturate a bit
    a=a*np.array(tint)*dark
    return Image.fromarray((a.clip(0,1)*255).astype('uint8'))
def cover(im,w,h,focus=(0.5,0.5)):
    r=max(w/im.width,h/im.height); im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
    x=int((im.width-w)*focus[0]); y=int((im.height-h)*focus[1]); return im.crop((x,y,x+w,y+h))
def vignette(img,strength=0.85):
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).ellipse((-W*0.15,-H*0.35,W*1.15,H*1.35),fill=255)
    m=m.filter(ImageFilter.GaussianBlur(260)); dark=Image.new('RGB',(W,H),BG)
    return Image.composite(img,Image.blend(dark,img,1-strength),m)
def grain(img,amt=10):
    n=np.random.normal(0,amt,(H//2,W//2)).astype('int16'); n=np.kron(n,np.ones((2,2),dtype='int16'))
    a=np.array(img).astype('int16')+n[...,None]; return Image.fromarray(a.clip(0,255).astype('uint8'))
def scan(img,alpha=10):
    s=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(s)
    for y in range(0,H,4): d.line((0,y,W,y),fill=(0,0,0,alpha*3))
    return Image.alpha_composite(img.convert('RGBA'),s).convert('RGB')
def light(img,cx,cy,r,color,a=170):
    l=Image.new('RGB',(W,H),(0,0,0)); ImageDraw.Draw(l).ellipse((cx-r,cy-r,cx+r,cy+r),fill=tuple(int(c*a/255) for c in color))
    l=l.filter(ImageFilter.GaussianBlur(r*0.6)); return ImageChops.screen(img,l)
def darken_band(img,x0,x1,amt=0.75):
    # darker zone behind text for legibility (horizontal gradient)
    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    for x in range(W):
        if x<x0: v=0
        elif x<x1: v=int(255*amt*(x-x0)/(x1-x0))
        else: v=int(255*amt)
        d.line((x,0,x,H),fill=v)
    m=m.filter(ImageFilter.GaussianBlur(40)); return Image.composite(Image.new('RGB',(W,H),BG),img,m)
def hud(img):
    d=ImageDraw.Draw(img); mono=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',34)
    d.ellipse((92,82,128,118),fill=RED); d.text((148,78),'REC',font=mono,fill=WHITE)
    d.text((W-330,78),'02:15:07',font=mono,fill=GREY)
    d.text((92,H-120),'BODY-WORN CAMERA',font=mono,fill=GREY); d.text((W-280,H-120),'CAM 01',font=mono,fill=GREY)
    L=90;T=7
    for (x,y,sx,sy) in [(50,50,1,1),(W-50,50,-1,1),(50,H-50,1,-1),(W-50,H-50,-1,-1)]:
        d.rectangle((min(x,x+sx*L),min(y,y+sy*T),max(x,x+sx*L),max(y,y+sy*T)),fill=WHITE)
        d.rectangle((min(x,x+sx*T),min(y,y+sy*L),max(x,x+sx*T),max(y,y+sy*L)),fill=WHITE)
    return img
def text_glow(img,xy,txt,font,fill,glow=(0,0,0),r=14,a=200):
    g=Image.new('L',(W,H),0); ImageDraw.Draw(g).text(xy,txt,font=font,fill=a); g=g.filter(ImageFilter.GaussianBlur(r))
    img=Image.composite(Image.new('RGB',(W,H),glow),img,g); ImageDraw.Draw(img).text(xy,txt,font=font,fill=fill); return img
def content(img):
    D=410; logo=Image.open('avatar.png').convert('RGB').resize((D,D),Image.LANCZOS)
    m=Image.new('L',(D,D),0); ImageDraw.Draw(m).ellipse((2,2,D-3,D-3),fill=255)
    lx=SX0+20; ly=(SY0+SY1)//2-D//2
    # logo shadow
    sh=Image.new('L',(W,H),0); ImageDraw.Draw(sh).ellipse((lx-10,ly+10,lx+D+10,ly+D+30),fill=230); sh=sh.filter(ImageFilter.GaussianBlur(30))
    img=Image.composite(Image.new('RGB',(W,H),(0,0,0)),img,sh)
    # red halo
    img=light(img,lx+D//2,ly+D//2,D*0.62,RED,95)
    img.paste(logo,(lx,ly),m)
    d=ImageDraw.Draw(img)
    tx=lx+D+64
    anton=ImageFont.truetype(F+'Anton.ttf',198)
    bb=d.textbbox((0,0),'FOX',font=anton); th=bb[3]-bb[1]; ty=ly+6-bb[1]
    t1='FOX USA '; w1=d.textlength(t1,font=anton)
    img=text_glow(img,(tx,ty),t1,anton,WHITE); img=text_glow(img,(tx+w1,ty),'CAM',anton,RED,glow=(0,0,0))
    # subtle red glow on CAM
    g=Image.new('L',(W,H),0); ImageDraw.Draw(g).text((tx+w1,ty),'CAM',font=anton,fill=120); g=g.filter(ImageFilter.GaussianBlur(26))
    img=ImageChops.screen(img,Image.composite(Image.new('RGB',(W,H),RED),Image.new('RGB',(W,H),(0,0,0)),g))
    ImageDraw.Draw(img).text((tx+w1,ty),'CAM',font=anton,fill=RED)
    d=ImageDraw.Draw(img); titlew=w1+d.textlength('CAM',font=anton)
    ly2=ly+6+th+30
    d.rectangle((tx,ly2,tx+120,ly2+6),fill=RED); d.rectangle((tx+132,ly2,tx+titlew,ly2+6),fill=(70,70,76))
    osw=ImageFont.truetype(F+'Oswald-500.woff',47); sl='EVERY BODYCAM VIDEO HAS A BEFORE AND AN AFTER.'
    sy=ly2+26; img=text_glow(img,(tx,sy),sl,osw,WHITE,r=10,a=220); d=ImageDraw.Draw(img)
    osb=ImageFont.truetype(F+'Oswald-700.woff',36); pl='NEW FULL CASE EVERY WEEK'; pw=d.textlength(pl,font=osb)
    py=sy+47+38
    d.rectangle((tx,py,tx+pw+40,py+58),fill=RED); d.text((tx+20,py+5),pl,font=osb,fill=WHITE)
    sub=ImageFont.truetype(F+'Oswald-500.woff',31); s2='911 CALL • BODYCAM • COURT OUTCOME'
    img=text_glow(img,(tx+pw+64,py+12),s2,sub,(205,205,210),r=8,a=230)
    right=max(tx+titlew,tx+d.textlength(sl,font=osw),tx+pw+64+d.textlength(s2,font=sub)); bottom=py+58
    assert right<SX1-5 and bottom<SY1, (right,bottom)
    return img
def finish(img): return grain(scan(hud(img)),7)

# ---------- A: night scene (fire + red light) ----------
src=Image.open('sbx/64engcACtH4_maxres2.jpg'); src=src.crop((0,int(src.height*0.04),src.width,int(src.height*0.74)))
bgA=grade(cover(src,W,H,(0.5,0.45)),tint=(1.0,0.62,0.6),dark=0.62,blur=18)
bgA=light(bgA,2250,420,420,RED,120); bgA=light(bgA,2300,760,260,RED,110)
bgA=darken_band(bgA,700,1250,0.62); bgA=vignette(bgA,0.8)
A=finish(content(bgA))
# ---------- B: police lights ----------
src=Image.open('sbx/fxFVB2fOJEs_maxres2.jpg'); src=src.crop((0,int(src.height*0.04),src.width,int(src.height*0.80)))
bgB=grade(cover(src,W,H,(0.5,0.5)),tint=(0.8,0.75,0.95),dark=0.45,blur=22)
for (x,y,r,c,a) in [(180,330,260,RED,190),(420,230,170,(40,90,255),170),(2380,300,250,(40,90,255),180),(2150,210,170,RED,170),(2460,1150,230,RED,140),(120,1180,200,(40,90,255),130),(230,720,230,RED,200),(2330,700,230,(40,90,255),200)]:
    bgB=light(bgB,x,y,r,c,a)
bgB=darken_band(bgB,650,1200,0.6); bgB=vignette(bgB,0.75)
B=finish(content(bgB))
# ---------- C: minimal pro ----------
bgC=Image.new('RGB',(W,H),BG)
bgC=light(bgC,800,720,700,(90,8,14),255)
st=Image.new('L',(W,H),0); ImageDraw.Draw(st).polygon([(1500,0),(1640,0),(900,H),(760,H)],fill=40); st=st.filter(ImageFilter.GaussianBlur(60))
bgC=Image.composite(Image.new('RGB',(W,H),(60,10,14)),bgC,st)
bgC=vignette(bgC,0.7)
C=finish(content(bgC))
for n,im in [('A',A),('B',B),('C',C)]:
    im.save(f'bannerv_{n}.jpg',quality=93)
print('ok')
