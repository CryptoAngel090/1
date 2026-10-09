import sys
sys.argv=['x']
exec(open('banner2.py').read().split('# ---------- A:')[0])   # reuse helpers & constants
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops
BLUE=(40,90,255)
def center_text(img):
    d=ImageDraw.Draw(img); cx=W//2
    anton=ImageFont.truetype(F+'Anton.ttf',196)
    t1='FOX USA '; t2='CAM'
    w1=d.textlength(t1,font=anton); w2=d.textlength(t2,font=anton); tw=w1+w2
    bb=d.textbbox((0,0),'FOX',font=anton); th=bb[3]-bb[1]
    top=SY0+22; tx=cx-tw/2; ty=top-bb[1]
    img=text_glow(img,(tx,ty),t1,anton,WHITE)
    g=Image.new('L',(W,H),0); ImageDraw.Draw(g).text((tx+w1,ty),t2,font=anton,fill=130); g=g.filter(ImageFilter.GaussianBlur(28))
    img=ImageChops.screen(img,Image.composite(Image.new('RGB',(W,H),RED),Image.new('RGB',(W,H),(0,0,0)),g))
    img=text_glow(img,(tx+w1,ty),t2,anton,RED)
    d=ImageDraw.Draw(img)
    ly=top+th+24
    d.rectangle((cx-tw/2,ly,cx-tw/2+140,ly+6),fill=RED); d.rectangle((cx-tw/2+152,ly,cx+tw/2-152,ly+6),fill=(70,70,76)); d.rectangle((cx+tw/2-140,ly,cx+tw/2,ly+6),fill=RED)
    osw=ImageFont.truetype(F+'Oswald-500.woff',52); sl='EVERY BODYCAM VIDEO HAS A BEFORE AND AN AFTER.'
    sw=d.textlength(sl,font=osw); sy=ly+22
    img=text_glow(img,(cx-sw/2,sy),sl,osw,WHITE,r=10,a=220); d=ImageDraw.Draw(img)
    osb=ImageFont.truetype(F+'Oswald-700.woff',38); pl='NEW FULL CASE EVERY WEEK'
    sub=ImageFont.truetype(F+'Oswald-500.woff',33); s2='911 CALL  •  BODYCAM  •  COURT OUTCOME'
    pw=d.textlength(pl,font=osb)+44; s2w=d.textlength(s2,font=sub); total=pw+28+s2w
    px=cx-total/2; py=sy+52+30
    d.rectangle((px,py,px+pw,py+60),fill=RED); d.text((px+22,py+6),pl,font=osb,fill=WHITE)
    img=text_glow(img,(px+pw+28,py+13),s2,sub,(210,210,215),r=8,a=230)
    assert py+60<SY1, py
    return img,(cx-tw/2,cx+tw/2,top,py+60)
def side_elements(img,box):
    d=ImageDraw.Draw(img); x0,x1,y0,y1=box; cy=(y0+y1)//2
    # 1) viewfinder brackets hugging text block (inside safe zone)
    pad=70; L=70; T=6; bx0,bx1,by0,by1=x0-pad,x1+pad,SY0+6,SY1-6
    for (x,y,sx,sy) in [(bx0,by0,1,1),(bx1,by0,-1,1),(bx0,by1,1,-1),(bx1,by1,-1,-1)]:
        d.rectangle((min(x,x+sx*L),min(y,y+sy*T),max(x,x+sx*L),max(y,y+sy*T)),fill=RED)
        d.rectangle((min(x,x+sx*T),min(y,y+sy*L),max(x,x+sx*T),max(y,y+sy*L)),fill=RED)
    # 2) vertical HUD scales left/right (ticks)
    for side in (-1,1):
        X = bx0-60 if side<0 else bx1+60
        for i in range(-12,13):
            y=cy+i*18; ln=34 if i%4==0 else 16
            d.line((X-ln//2*(1 if side<0 else 0)-(0 if side<0 else 0), y, X+ (ln if side>0 else -ln), y), fill=(150,150,158) if i%4 else WHITE, width=3)
    # 3) police light bars far left / right (desktop & TV), red-blue alternating
    for side in (-1,1):
        X = 190 if side<0 else W-190
        cols=[RED,BLUE,RED,BLUE] if side<0 else [BLUE,RED,BLUE,RED]
        for k,c in enumerate(cols):
            y=cy-150+k*100
            img=light(img,X,y,120,c,170)
        dd=ImageDraw.Draw(img)
        for k,c in enumerate(cols):
            y=cy-150+k*100
            dd.rounded_rectangle((X-70,y-26,X+70,y+26),radius=14,fill=tuple(min(255,int(v*1.0)) for v in c))
            dd.rounded_rectangle((X-70,y-26,X+70,y+26),radius=14,outline=(255,255,255),width=2)
    # 4) evidence-style data blocks between bars and safe zone
    d=ImageDraw.Draw(img); mono=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',30)
    left=['CASE FILE','CAM 01-04','911 AUDIO','BODY CAM']; right=['FULL CASE','UNEDITED','COURT DOCS','TIMELINE']
    for i,(a,b) in enumerate(zip(left,right)):
        y=cy-110+i*62
        wa=d.textlength(a,font=mono); d.text((475-wa,y),a,font=mono,fill=(170,170,178)); d.rectangle((475-wa-26,y+8,475-wa-16,y+26),fill=RED)
        wb=d.textlength(b,font=mono); d.text((W-475,y),b,font=mono,fill=(170,170,178)); d.rectangle((W-475+wb+16,y+8,W-475+wb+26,y+26),fill=RED)
    return img
bg=Image.new('RGB',(W,H),BG)
bg=light(bg,W//2,720,820,(80,8,14),255)
bg=vignette(bg,0.7)
img,box=center_text(bg)
img=side_elements(img,box)
img=grain(scan(hud(img)),7)
img.save('banner_center.jpg',quality=93)
print('ok',box)
