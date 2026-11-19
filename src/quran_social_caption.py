"""Varied, content-aware Arabic/English captions and exactly-five hashtag sets."""
from __future__ import annotations

import hashlib
from typing import Any

THEMES = (
    ("patience", ("patience", "patient", "persevere", "hardship", "ease", "fear", "grief"),
     "الصبر والثبات عند الشدائد، وأن مع العسر يسراً",
     "patience, perseverance, and hope through hardship",
     "#الصبر_والفرج", "#PatienceAndHope"),
    ("mercy", ("mercy", "forgiving", "forgive", "compassion", "merciful", "forgiven"),
     "رحمة الله ومغفرته، وفتح باب الرجوع إليه",
     "Allah’s mercy, forgiveness, and the door of repentance",
     "#رحمة_ومغفرة", "#MercyAndForgiveness"),
    ("prayer", ("prayer", "pray", "worship", "prostrate", "righteous deeds"),
     "الإخلاص في العبادة والمحافظة على الصلاة والعمل الصالح",
     "sincere worship, prayer, and righteous deeds",
     "#الصلاة_والعبادة", "#PrayerAndWorship"),
    ("gratitude", ("thankful", "thanks", "gratitude", "blessing", "favor"),
     "شكر نعم الله والاعتراف بفضله",
     "gratitude for Allah’s blessings",
     "#الشكر_والنعم", "#GratitudeToAllah"),
    ("guidance", ("guide", "guidance", "path", "believe", "faith", "light"),
     "الهداية والإيمان والثبات على الطريق المستقيم",
     "faith, guidance, and steadfastness on the straight path",
     "#الهداية_والإيمان", "#FaithAndGuidance"),
    ("afterlife", ("resurrection", "judgment", "paradise", "hell", "hereafter", "day of"),
     "الآخرة والجزاء وتذكّر الوقوف بين يدي الله",
     "the Hereafter, accountability, and the final return to Allah",
     "#الآخرة_والحساب", "#HereafterReminder"),
    ("tawheed", ("one god", "one", "eternal refuge", "begets", "equivalent", "creator"),
     "توحيد الله وتعظيمه وإفراده بالعبادة",
     "the oneness of Allah and devotion to Him alone",
     "#توحيد_الله", "#Tawheed"),
)

# Broad, Quran-relevant pools. Selection balances least-used tags over confirmed posts.
AR_HASHTAGS = (
    "#القرآن_الكريم", "#تلاوة_قرآنية", "#آيات_قرآنية", "#تدبر_القرآن",
    "#ذكر_الله", "#نور_القرآن", "#القرآن", "#تذكير_إيماني",
    "#كلام_الله", "#تلاوة_خاشعة", "#آيات_من_القرآن", "#مع_القرآن",
    "#رسالة_قرآنية", "#آيات_للتدبر", "#هداية", "#الذكر_الحكيم",
    "#تدبر_وعمل", "#طمأنينة_القلب", "#تذكير_بالله", "#آيات_الله",
)
EN_HASHTAGS = (
    "#Quran", "#QuranVerses", "#QuranRecitation", "#IslamicReminder",
    "#ReflectOnQuran", "#QuranReflection", "#DailyQuran", "#WordsOfAllah",
    "#ListenToQuran", "#QuranDaily", "#FaithReminder", "#AyahOfTheDay",
    "#QuranInspiration", "#IslamicContent", "#QuranReminder", "#QuranTime",
    "#Islam", "#ReminderForTheSoul", "#QuranAndSunnah", "#ReadQuran",
)

HOOKS = (
    ("reflection", "وقفة قصيرة للتدبّر في آيات من كتاب الله", "A quiet moment to reflect on verses from the Quran"),
    ("listen", "أنصت بقلبك إلى كلام الله", "Listen closely and reflect on the words of Allah"),
    ("reminder", "تذكير قرآني نحتاجه في كل يوم", "A Quran reminder for every day"),
    ("heart", "امنح قلبك لحظة مع القرآن الكريم", "Give your heart a moment with the Quran"),
    ("pause", "توقّف قليلاً واستمع إلى هذه الآيات", "Pause for a moment and listen to these verses"),
    ("light", "مع آيات من القرآن، نجدد صلتنا بكتاب الله", "Reconnect with the Quran through these verses"),
    ("daily", "آيات نتلوها ونتدبّرها", "Verses to listen to and reflect upon"),
    ("calm", "لحظات من السكينة مع تلاوة القرآن", "A moment of calm with Quran recitation"),
    ("meaning", "افتح قلبك للتلاوة والتدبّر", "Open your heart to recitation and reflection"),
    ("share", "اجعل للقرآن نصيباً من وقتك اليوم", "Make time for the Quran today"),
)

CTAS = (
    ("reflect", "استمع وتدبّر، وارجع إلى الآيات بتأنٍ", "Listen, reflect, and revisit the verses"),
    ("save", "احفظ المقطع لتعود إلى التلاوة لاحقاً", "Save this recitation to revisit it later"),
    ("share", "شارك التذكير مع من تحب", "Share this reminder with someone you care about"),
    ("follow", "تابعنا لمزيد من التلاوات والتذكير بالقرآن", "Follow for more Quran recitations and reminders"),
    ("daily", "اجعل تلاوة القرآن جزءاً من يومك", "Make Quran recitation part of your day"),
    ("listen", "أنصت للتلاوة كاملة، بارك الله فيك", "Take a moment to listen to the full recitation"),
    ("return", "عود نفسك الرجوع إلى كتاب الله", "Keep returning to the Book of Allah"),
    ("remind", "أرسلها لمن قد ينتفع بهذا التذكير", "Send this reminder to someone who may appreciate it"),
    ("reflect2", "تدبّر الآيات من المصحف", "Reflect on the verses while reading the Quran"),
    ("support", "إن نفعك المقطع، ساهم في نشره", "If this benefited you, help share the reminder"),
)


def empty_social_history() -> dict[str, Any]:
    return {"schema_version": 1, "posts": []}


def _history_counts(history: dict[str, Any] | None, field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not history:
        return counts
    if history.get("schema_version") != 1 or not isinstance(history.get("posts"), list):
        raise ValueError("Social-content history is malformed or unsupported.")
    for post in history["posts"]:
        values = post.get(field, [])
        if isinstance(values, list):
            for value in values:
                if isinstance(value, str):
                    counts[value] = counts.get(value, 0) + 1
    return counts


def _choose(pool: tuple, counts: dict[str, int], seed: str, count: int = 1) -> list:
    ranked = sorted(
        pool,
        key=lambda value: (
            counts.get(value, 0),
            hashlib.sha256(f"{seed}:{value}".encode("utf-8")).hexdigest(),
        ),
    )
    return ranked[:count]


def detect_theme(verses: list[dict[str, Any]]) -> tuple[str, str, str, str, str]:
    text = " ".join(str(v.get("english", "")) for v in verses).lower()
    scored = []
    for theme in THEMES:
        score = sum(text.count(word) for word in theme[1])
        if score:
            scored.append((score, theme))
    if not scored:
        return ("general", "وتدعونا الآيات إلى الإيمان بالله والعمل بالخير والتدبّر في هديه",
                "these verses invite faith, reflection, and righteous action",
                "#تدبر_وعمل", "#QuranReflection")
    selected = max(scored, key=lambda item: (item[0], -THEMES.index(item[1])))[1]
    return selected[0], selected[2], selected[3], selected[4], selected[5]


def build_social_caption(
    manifest: dict[str, Any],
    video_id: str,
    history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(manifest, dict) or not isinstance(video_id, str) or not video_id.strip():
        raise ValueError("A manifest and stable non-empty video id are required.")
    source = manifest.get("source", {})
    verses = manifest.get("verses", [])
    if not isinstance(verses, list) or not verses:
        raise ValueError("Caption requires at least one selected verse.")
    name = str(source.get("surah_name_ar", "")).strip()
    english_name = str(source.get("surah_name_en", "")).strip()
    numbers = source.get("verses", [])
    if not name or not isinstance(numbers, list) or not numbers:
        raise ValueError("Caption requires the surah name and selected ayah numbers.")
    first, last = int(numbers[0]), int(numbers[-1])
    theme, description_ar, description_en, topic_ar, topic_en = detect_theme(verses)

    ar_counts = _history_counts(history, "hashtags_ar")
    en_counts = _history_counts(history, "hashtags_en")
    hook_counts = _history_counts(history, "hook_ids")
    cta_counts = _history_counts(history, "cta_ids")
    ar_tags = _choose(tuple(tag for tag in AR_HASHTAGS if tag != topic_ar), ar_counts, video_id, 2)
    en_tags = _choose(tuple(tag for tag in EN_HASHTAGS if tag != topic_en), en_counts, video_id, 1)
    hashtags_ar = ar_tags + [topic_ar]
    hashtags_en = en_tags + [topic_en]
    hook_id = _choose(tuple(item[0] for item in HOOKS), hook_counts, video_id)[0]
    cta_id = _choose(tuple(item[0] for item in CTAS), cta_counts, video_id)[0]
    hook_ar, hook_en = next((item[1], item[2]) for item in HOOKS if item[0] == hook_id)
    cta_ar, cta_en = next((item[1], item[2]) for item in CTAS if item[0] == cta_id)

    return {
        "arabic_caption": f"سورة {name} | الآيات {first}-{last}\n{hook_ar}. {description_ar}. {cta_ar}.",
        "english_caption": f"Surah {english_name or name} | Verses {first}-{last}. {hook_en}. {description_en.capitalize()}. {cta_en}.",
        "hashtags_ar": hashtags_ar,
        "hashtags_en": hashtags_en,
        "theme": theme,
        "hook_id": hook_id,
        "cta_id": cta_id,
    }
