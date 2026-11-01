"""Parse a user's Telegram Quran video request without triggering rendering or delivery."""
from __future__ import annotations

import re
import unicodedata

SURAH_NAMES = [
    "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف",
    "الأنفال", "التوبة", "يونس", "هود", "يوسف", "الرعد", "إبراهيم", "الحجر",
    "النحل", "الإسراء", "الكهف", "مريم", "طه", "الأنبياء", "الحج", "المؤمنون",
    "النور", "الفرقان", "الشعراء", "النمل", "القصص", "العنكبوت", "الروم",
    "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر", "يس", "الصافات", "ص", "الزمر",
    "غافر", "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية", "الأحقاف", "محمد",
    "الفتح", "الحجرات", "ق", "الذاريات", "الطور", "النجم", "القمر", "الرحمن",
    "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة", "الصف", "الجمعة",
    "المنافقون", "التغابن", "الطلاق", "التحريم", "الملك", "القلم", "الحاقة",
    "المعارج", "نوح", "الجن", "المزمل", "المدثر", "القيامة", "الإنسان",
    "المرسلات", "النبأ", "النازعات", "عبس", "التكوير", "الانفطار", "المطففين",
    "الانشقاق", "البروج", "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد",
    "الشمس", "الليل", "الضحى", "الشرح", "التين", "العلق", "القدر", "البينة",
    "الزلزلة", "العاديات", "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل",
    "قريش", "الماعون", "الكوثر", "الكافرون", "النصر", "المسد", "الإخلاص",
    "الفلق", "الناس",
]

_TRANSLATION = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")


def _clean(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).translate(_TRANSLATION)
    value = value.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    value = re.sub(r"[ًٌٍَُِّْـ]", "", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def parse_quran_request(message: str) -> dict:
    """Accept e.g. 'فيديو سورة الرحمن' or 'فيديو سورة البقرة الآيات 1-5'."""
    if not isinstance(message, str) or not message.strip():
        raise ValueError("ابعث اسم السورة، مثال: فيديو سورة الرحمن")
    cleaned = _clean(message)
    cleaned = re.sub(r"^(?:(?:اريد|نحب|اعمل|حضر)\s+)?(?:فيديو\s+)?سورة\s+", "", cleaned)
    match = re.fullmatch(
        r"(?P<name>.+?)(?:\s+(?:الايات|اية|من)\s*(?P<start>\d+)\s*(?:-|الى|إلى|ل)\s*(?P<end>\d+))?",
        cleaned,
    )
    if not match:
        raise ValueError("الصيغة موش واضحة. مثال: فيديو سورة البقرة الآيات 1-5")
    requested_name = match.group("name").strip()
    names = {_clean(name): i + 1 for i, name in enumerate(SURAH_NAMES)}
    surah = names.get(requested_name)
    if surah is None:
        raise ValueError("ما تعرفتش على اسم السورة. ابعث الاسم العربي الصحيح.")
    has_range = match.group("start") is not None
    start = int(match.group("start") or 1)
    end = int(match.group("end")) if has_range else None
    if start < 1 or (has_range and (end < start or end - start > 9)):
        raise ValueError("الطلب لازم يكون من آية إلى 10 آيات متتالية.")
    return {
        "surah_number": surah,
        "surah_name": SURAH_NAMES[surah - 1],
        "start_ayah": start,
        "end_ayah": end,
        "request_type": "single_surah_passage" if has_range else "full_surah",
        "status": "parsed_only_not_rendered_not_sent",
        "rendering_allowed": False,
        "telegram_delivery": False,
        "auto_publish": False,
    }
