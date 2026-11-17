"""Standalone cinematic Quran renderer.

This module intentionally has no imports from the legacy/classic preview engine.
It owns its own scene preparation, Arabic overlays, cover rendering and FFmpeg
composition. Review-only: it never publishes or sends notifications.
"""
from __future__ import annotations

import io
import json
import math
import subprocess
import urllib.request
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, features

WIDTH, HEIGHT, FPS = 1080, 1920, 30
COVER_IDS = ("blue_night", "emerald_green", "dark_marble", "sunset")
COVER_ARCHIVE = Path("assets/background_photos/quran_cover_templates.zip")
PALETTE = ((12, 31, 46), (220, 190, 125))
SURAH_NAMES = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]
SURAH_TASHKEEL = ["الْفَاتِحَةِ","الْبَقَرَةِ","آلِ عِمْرَانَ","النِّسَاءِ","الْمَائِدَةِ","الْأَنْعَامِ","الْأَعْرَافِ","الْأَنْفَالِ","التَّوْبَةِ","يُونُسَ","هُودٍ","يُوسُفَ","الرَّعْدِ","إِبْرَاهِيمَ","الْحِجْرِ","النَّحْلِ","الْإِسْرَاءِ","الْكَهْفِ","مَرْيَمَ","طٰهٰ","الْأَنْبِيَاءِ","الْحَجِّ","الْمُؤْمِنُونَ","النُّورِ","الْفُرْقَانِ","الشُّعَرَاءِ","النَّمْلِ","الْقَصَصِ","الْعَنْكَبُوتِ","الرُّومِ","لُقْمَانَ","السَّجْدَةِ","الْأَحْزَابِ","سَبَأَ","فَاطِرٍ","يسٓ","الصَّافَّاتِ","صٓ","الزُّمَرِ","غَافِرٍ","فُصِّلَتْ","الشُّورَىٰ","الزُّخْرُفِ","الدُّخَانِ","الْجَاثِيَةِ","الْأَحْقَافِ","مُحَمَّدٍ","الْفَتْحِ","الْحُجُرَاتِ","قٓ","الذَّارِيَاتِ","الطُّورِ","النَّجْمِ","الْقَمَرِ","الرَّحْمَٰنِ","الْوَاقِعَةِ","الْحَدِيدِ","الْمُجَادِلَةِ","الْحَشْرِ","الْمُمْتَحَنَةِ","الصَّفِّ","الْجُمُعَةِ","الْمُنَافِقُونَ","التَّغَابُنِ","الطَّلَاقِ","التَّحْرِيمِ","الْمُلْكِ","الْقَلَمِ","الْحَاقَّةِ","الْمَعَارِجِ","نُوحٍ","الْجِنِّ","الْمُزَّمِّلِ","الْمُدَّثِّرِ","الْقِيَامَةِ","الْإِنْسَانِ","الْمُرْسَلَاتِ","النَّبَإِ","النَّازِعَاتِ","عَبَسَ","التَّكْوِيرِ","الْإِنْفِطَارِ","الْمُطَفِّفِينَ","الْإِنْشِقَاقِ","الْبُرُوجِ","الطَّارِقِ","الْأَعْلَىٰ","الْغَاشِيَةِ","الْفَجْرِ","الْبَلَدِ","الشَّمْسِ","اللَّيْلِ","الضُّحَىٰ","الشَّرْحِ","التِّينِ","الْعَلَقِ","الْقَدْرِ","الْبَيِّنَةِ","الزَّلْزَلَةِ","الْعَادِيَاتِ","الْقَارِعَةِ","التَّكَاثُرِ","الْعَصْرِ","الْهُمَزَةِ","الْفِيلِ","قُرَيْشٍ","الْمَاعُونِ","الْكَوْثَرِ","الْكَافِرُونَ","النَّصْرِ","الْمَسَدِ","الْإِخْلَاصِ","الْفَلَقِ","النَّاسِ"]

def font_file() -> str:
    p = subprocess.check_output(["fc-match","-f","%{file}","Amiri:style=Bold"], text=True).strip()
    if not p or not Path(p).is_file():
        raise RuntimeError("Amiri Bold font unavailable")
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM is required for Arabic shaping")
    return p

def prepare_moving_background(candidate: dict, destination: Path) -> dict:
    request = urllib.request.Request(candidate["direct_video_url"], headers={"User-Agent":"CinematicQuranRenderer/1.0"})
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk: break
            out.write(chunk)
    if destination.stat().st_size < 100_000:
        raise RuntimeError("Moving background download is incomplete")
    raw = subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","format=duration:stream=codec_name,width,height","-of","json",str(destination)], text=True)
    data = json.loads(raw); stream = data["streams"][0]
    if stream.get("codec_name") not in {"h264","hevc","vp9","av1"}:
        raise RuntimeError("Background is not a supported moving video")
    duration = float(data.get("format",{}).get("duration") or candidate.get("duration_seconds") or 0)
    if duration <= 0: raise RuntimeError("Background duration is invalid")
    return {"id":candidate["id"],"duration_seconds":round(duration,3),"description":candidate.get("description",candidate["id"]),"source_page_url":candidate.get("source_page_url",""),"codec":stream.get("codec_name"),"width":stream.get("width"),"height":stream.get("height")}

def make_frame(verse: dict, surah: int, index: int, out: Path, font_path: str, surah_name: str) -> None:
    if not features.check("raqm"): raise RuntimeError("Arabic shaping unavailable")
    image = Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0)); draw=ImageDraw.Draw(image)
    accent=PALETTE[1]
    draw.rectangle((0,0,WIDTH,HEIGHT),fill=(12,31,46,30))
    draw.rounded_rectangle((82,320,998,1600),radius=48,fill=(3,12,18,148),outline=(*accent,175),width=2)
    title=f"سورة {surah_name}"
    title_font=ImageFont.truetype(font_path,58,layout_engine=ImageFont.Layout.RAQM)
    draw.text((540,465),title,font=title_font,fill=accent,anchor="mm",direction="rtl",language="ar")
    draw.line((210,575,870,575),fill=(*accent,155),width=2)
    arabic=verse["arabic"]; font=ImageFont.truetype(font_path,78,layout_engine=ImageFont.Layout.RAQM)
    draw.text((540,865),arabic,font=font,fill=(255,255,250,255),anchor="mm",direction="rtl",language="ar")
    number=str(verse["number"]).translate(str.maketrans("0123456789","٠١٢٣٤٥٦٧٨٩"))
    draw.ellipse((491,1086,589,1184),outline=(*accent,245),width=4)
    draw.text((540,1135),number,font=ImageFont.truetype(font_path,40,layout_engine=ImageFont.Layout.RAQM),fill=accent,anchor="mm",direction="rtl",language="ar")
    english=verse.get("english","")
    ef=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",30)
    words=english.split(); lines=[]; line=""
    for word in words:
        trial=(line+" "+word).strip()
        if draw.textbbox((0,0),trial,font=ef)[2] > 820:
            lines.append(line); line=word
        else: line=trial
    if line: lines.append(line)
    y=1370-(len(lines)-1)*22
    for i,s in enumerate(lines): draw.text((540,y+i*44),s,font=ef,fill=(248,249,246,255),anchor="mm")
    image.save(out)

def make_intro_frame(surah_number: int, start_ayah: int, end_ayah: int, out: Path, font_path: str, surah_name: str, background_frame: Path|None=None, cover_rotation_index: int=0) -> str:
    if not 0 <= cover_rotation_index < len(COVER_IDS): raise ValueError("Invalid cover rotation")
    with zipfile.ZipFile(COVER_ARCHIVE) as archive:
        raw=archive.read(f"cover_{COVER_IDS[cover_rotation_index]}.jpg")
    source=Image.open(io.BytesIO(raw)).convert("RGBA")
    bg=ImageOps.fit(source,(WIDTH,HEIGHT)).filter(ImageFilter.GaussianBlur(28))
    image=Image.alpha_composite(bg,Image.new("RGBA",(WIDTH,HEIGHT),(2,7,10,112)))
    fh=round(source.height*WIDTH/source.width); fg=source.resize((WIDTH,fh)); top=(HEIGHT-fh)//2
    image.alpha_composite(fg,(0,top)); draw=ImageDraw.Draw(image)
    title=f"سُورَةُ {SURAH_TASHKEEL[surah_number-1]}"
    tf=ImageFont.truetype(font_path,100,layout_engine=ImageFont.Layout.RAQM)
    draw.text((540,top+round(fh*.41)),title,font=tf,fill=(255,226,158,255),anchor="mm",direction="rtl",language="ar")
    digits=str.maketrans("0123456789","٠١٢٣٤٥٦٧٨٩")
    label=f"الْآيَاتُ {str(start_ayah).translate(digits)} - {str(end_ayah).translate(digits)}"
    draw.text((540,top+round(fh*.66)),label,font=ImageFont.truetype(font_path,48,layout_engine=ImageFont.Layout.RAQM),fill=(255,229,169,255),anchor="mm",direction="rtl",language="ar")
    image.save(out); return COVER_IDS[cover_rotation_index]

def probe(path: Path) -> dict:
    raw=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_name,width,height","-of","json",str(path)],text=True)
    data=json.loads(raw); video=next(s for s in data["streams"] if "width" in s); audio=next(s for s in data["streams"] if "width" not in s)
    duration=float(data["format"]["duration"])
    if (video["width"],video["height"])!=(WIDTH,HEIGHT) or audio["codec_name"]!="mp3" or not 0<duration<=45: raise RuntimeError("Rendered media validation failed")
    return {"duration_seconds":round(duration,3),"width":WIDTH,"height":HEIGHT,"video_codec":video["codec_name"],"audio_codec":audio["codec_name"]}

def render_cinematic_preview(scenes: list[dict], intro: Path, output: Path, work: Path) -> dict:
    if not scenes or not intro.is_file(): raise ValueError("Cinematic preview needs scenes and cover")
    durations=[float(s["duration"]) for s in scenes]
    if any(not math.isfinite(d) or d<=0 for d in durations): raise ValueError("Invalid ayah timing")
    total=sum(durations); transition=min(.45,min(durations)*.16) if len(scenes)>1 else 0
    inputs=[]; filters=[]
    for i,(scene,duration) in enumerate(zip(scenes,durations)):
        clip=duration+(transition if i<len(scenes)-1 else 0)
        inputs += ["-stream_loop","-1","-i",str(scene["background"])]
        filters.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(1+0.00009*on,1.04)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=1080x1920:fps=30,trim=duration={clip:.6f},setpts=PTS-STARTPTS,setsar=1,format=yuv420p,settb=AVTB[v{i}]")
    current="v0"; elapsed=durations[0]
    for i in range(1,len(scenes)):
        label=f"x{i}"; filters.append(f"[{current}][v{i}]xfade=transition=fade:duration={transition:.6f}:offset={elapsed:.6f}[{label}]"); current=label; elapsed+=durations[i]
    filters.append(f"[{current}]trim=duration={total:.6f},setpts=PTS-STARTPTS,format=yuv420p[outv]")
    reel=work/"cinematic_background_reel.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",*inputs,"-filter_complex",";".join(filters),"-map","[outv]","-an","-t",f"{total:.6f}","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-r","30",str(reel)],check=True)
    alist=work/"cinematic_audio.txt"; alist.write_text("".join(f"file '{Path(s['audio']).resolve()}'\n" for s in scenes),encoding="utf-8")
    audio=work/"cinematic_audio.mp3"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(alist),"-c:a","copy",str(audio)],check=True)
    args=["-i",str(reel),"-i",str(audio),"-loop","1","-framerate","30","-i",str(intro)]
    filters=["[0:v]setpts=PTS-STARTPTS[v0]","[v0][2:v]overlay=0:0:format=auto:enable='lt(t,0.6)'[cover]"]; current="cover"; elapsed=0
    for i,scene in enumerate(scenes):
        args += ["-loop","1","-framerate","30","-i",str(scene["frame"])]
        start=max(elapsed,.6) if i==0 else elapsed; end=elapsed+durations[i]; label=f"verse{i}"
        filters.append(f"[{current}][{i+3}:v]overlay=0:0:format=auto:enable='gte(t,{start:.6f})*lt(t,{end:.6f})'[{label}]")
        current=label; elapsed=end
    output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",*args,"-filter_complex",";".join(filters),"-map",f"[{current}]","-map","1:a:0","-t",f"{total:.6f}","-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p","-c:a","copy","-shortest","-movflags","+faststart",str(output)],check=True)
    return {"duration_seconds":round(total,3),"transition_seconds":round(transition,3),"scene_count":len(scenes),"motion":"slow_centered_zoom","renderer":"standalone_cinematic"}
