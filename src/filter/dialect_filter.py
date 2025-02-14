"""Dialect Filter for Algerian Arabic (Darija).

Identifies authentic Algerian Darija in both Arabic script and Arabizi (Latin script).
Aggressively excludes pure Modern Standard Arabic (MSA) and pure French.
"""

import re
from typing import Dict, List, Set, Tuple

# Algerian Darija Lexicon & Morphemes (Arabic Script)
DARIJA_ARABIC_MARKERS: Set[str] = {
    # Negative particles and circumfixes
    "ماكانش", "ماكاش", "مكانش", "مكاش", "ماشي", "مازال", "ماعنديش", "مانعرفش",
    "مارانيش", "مناش", "ميهمنيش", "ميحبش", "معندهاش", "ماكش", "متزيدش",
    # Demonstratives & Interrogatives (Strict dialectal spellings)
    "واش", "وقتاش", "وين", "علاش", "كفاش", "كيفاه", "كفاه", "شكون",
    "هدا", "هادي", "هاد", "هدوك", "هكا", "هاكدا", "كيما", "وش",
    # Pronouns & Auxiliaries
    "كاين", "بزاف", "شوية", "شوي", "برك", "دروك", "ضرك", "دك", "حنا", "نتوما",
    "راني", "راك", "راه", "راهم", "راكم", "قاعد", "قاعدة",
    # Verbs & Common Slang / Idiomatic Words
    "نهدر", "يهدر", "تهدر", "هدرة", "شاف", "يشوف", "تشوف", "روح", "يروح", "تروح",
    "حاب", "حابة", "حابين", "جاب", "يجي", "تجي", "يدي", "تديه",
    "مليح", "مليحة", "شاب", "شابة", "فور", "علامة", "صحيت", "يعطيك الصحة",
    "خويا", "خاوتي", "حومة", "زنقة", "بلاك", "تاع", "نتاع", "تاعك", "تاعو",
    "باغي", "نحوس", "يحوس", "غادي", "والو", "حاجة", "طبة", "حبابنا",
    "دزاير", "الجزاير", "فالدزاير", "عفسة", "عفايس", "قسنطينة", "وهران", "عنابة",
    "لاباس", "بصح", "كي", "جيت", "لي", "درت", "دارو", "خدمة", "قرعة",
}

# Negative circumfix regex (ما + verb + ش)
DARIJA_CIRCUMFIX_REGEX = re.compile(r"\bما\w+ش\b")

# Modern Standard Arabic (MSA) Formal Function Words
MSA_FORMAL_MARKERS: Set[str] = {
    "إن", "أن", "سوف", "حيث", "لذلك", "وبالتالي", "كذلك", "الذي", "التي",
    "اللذان", "اللتان", "الذين", "اللواتي", "اللاتي", "وفقا", "بينما", "نحو",
    "إذ", "فضلا", "علاوة", "ينبغي", "يجب", "تجدر", "الإشارة", "أكد", "صرح",
    "من الجدير بالذكر", "فيما يتعلق", "أعرب عن", "بناء على", "هذا وقد",
}

# Arabizi Darija Markers (Latin Script + Digits)
ARABIZI_MARKERS: Set[str] = {
    "bzaf", "bezzaf", "rak", "rani", "rah", "chouf", "choufi", "sahbi",
    "khoya", "khouya", "khti", "kayen", "makanch", "makash", "machi",
    "wash", "wesh", "wach", "3lash", "3lach", "wa9tach", "waqtach", "kifah",
    "chkoun", "hada", "hadi", "hadik", "haka", "hakda", "daymen", "dorka",
    "drk", "bark", "chwya", "chwiya", "ntouma", "lah", "hmd", "inchallah",
    "inshallah", "yaatik", "saha", "m3ak", "fina", "fiha", "mzyan", "mle7",
    "chaba", "chbab", "ta3", "nta3", "te3", "baghi", "nro7", "yro7", "yji",
    "ghadi", "walou", "walo", "bla", "dzair", "algerie", "dz", "3labali",
    "ma3labalich", "imaginiw", "chkoun", "bah", "thasseb", "fla",
}

# Digit characters representing Arabic sounds in Arabizi: 2, 3, 5, 7, 9
ARABIZI_DIGIT_REGEX = re.compile(r"[a-zA-Z]+[23579][a-zA-Z0-9]*|[23579][a-zA-Z]+")

# Common French Stopwords (Used to detect pure French comments)
FRENCH_COMMON_WORDS: Set[str] = {
    "le", "la", "les", "des", "un", "une", "du", "de", "ce", "cet", "cette",
    "ces", "mon", "ton", "son", "notre", "votre", "leur", "je", "tu", "il",
    "elle", "nous", "vous", "ils", "elles", "et", "ou", "mais", "donc", "or",
    "ni", "car", "pour", "dans", "sur", "avec", "sans", "sous", "par",
    "est", "sont", "été", "avoir", "être", "fait", "faire", "plus", "moins",
    "très", "bien", "merci", "beaucoup", "bonjour", "bon", "courage", "bravo",
    "tout", "tous", "toute", "toutes", "comme", "aussi", "vrai", "vraie",
    "horrible", "écoute", "entendre", "parler", "mélanger", "conseil",
}


def analyze_arabic_text(text: str) -> Tuple[bool, str, List[str]]:
    """Evaluates Arabic script text for Darija dialect vs MSA.

    Returns:
        (is_valid_darija, status_code, markers_found)
    """
    words = re.findall(r"[\u0600-\u06FF]+", text)
    if not words:
        return False, "no_arabic_tokens", []

    found_markers = []
    for w in words:
        if w in DARIJA_ARABIC_MARKERS:
            found_markers.append(w)

    # Check for negative circumfix patterns (e.g., ماعنديش, ماقالكش)
    circumfix_matches = DARIJA_CIRCUMFIX_REGEX.findall(text)
    for match in circumfix_matches:
        if match not in found_markers:
            found_markers.append(match)

    found_msa = [w for w in words if w in MSA_FORMAL_MARKERS]

    # If formal MSA markers significantly outweigh or accompany weak Darija markers
    if len(found_msa) >= 2 and len(found_markers) < 2:
        return False, "filtered_pure_msa", found_msa

    # If it has strong Darija markers, accept as authentic Darija
    if len(found_markers) >= 1:
        return True, "algerian_darija", found_markers

    # If pure MSA markers exist and no Darija markers, reject as MSA
    if len(found_msa) >= 1:
        return False, "filtered_pure_msa", found_msa

    # If no distinctive markers either way, reject to maintain strict dataset quality
    return False, "filtered_insufficient_dialect_markers", []


def analyze_latin_text(text: str) -> Tuple[bool, str, List[str]]:
    """Evaluates Latin script text for Arabizi Darija vs pure French/English.

    Returns:
        (is_valid_darija, status_code, markers_found)
    """
    words = [w.lower() for w in re.findall(r"[a-zA-Z0-9]+", text)]
    if not words:
        return False, "no_latin_tokens", []

    found_arabizi = [w for w in words if w in ARABIZI_MARKERS]
    digit_words = ARABIZI_DIGIT_REGEX.findall(text.lower())
    for dw in digit_words:
        if dw not in found_arabizi:
            found_arabizi.append(dw)

    found_french = [w for w in words if w in FRENCH_COMMON_WORDS]

    # If Arabizi markers or digit phonemes are present, accept as Darija Arabizi
    if len(found_arabizi) >= 1:
        return True, "algerian_darija_arabizi", found_arabizi

    # If the text is heavily French and lacks any Arabizi markers, reject as French
    if len(found_french) >= 3 or (len(words) > 0 and len(found_french) / len(words) > 0.4):
        return False, "filtered_pure_french", found_french

    return False, "filtered_insufficient_dialect_markers", []


def filter_dialect(text: str, script_type: str) -> Dict[str, any]:
    """Applies dialect validation based on script type.

    Args:
        text: Input cleaned text string.
        script_type: 'arabic', 'latin', or 'mixed'.

    Returns:
        Dictionary with classification result, status, and markers detected.
    """
    if script_type == "arabic":
        is_darija, status, markers = analyze_arabic_text(text)
    elif script_type == "latin":
        is_darija, status, markers = analyze_latin_text(text)
    elif script_type == "mixed":
        # For code-switched text, check both Arabic and Latin components
        is_ar, status_ar, markers_ar = analyze_arabic_text(text)
        is_lat, status_lat, markers_lat = analyze_latin_text(text)
        is_darija = is_ar or is_lat
        status = "algerian_darija_mixed" if is_darija else "filtered_mixed_non_darija"
        markers = list(set(markers_ar + markers_lat))
    else:
        is_darija, status, markers = False, "unknown_script", []

    return {
        "is_darija": is_darija,
        "status": status,
        "markers": markers,
    }
