"""Russian alphabet data — 33 letters with phonetic information."""
from dataclasses import dataclass
from typing import List


@dataclass
class RussianLetter:
    """A single Russian alphabet letter."""

    position: int  # 1-33
    upper: str  # Uppercase letter
    lower: str  # Lowercase letter
    name: str  # Letter name in Russian (transliterated)
    ipa: str  # IPA pronunciation
    english_approx: str  # English sound approximation
    letter_type: str  # "vowel", "consonant", or "sign"
    example_word: str  # Common Russian word starting with this letter
    example_translation: str  # English translation
    notes: str  # Additional phonetic notes

    @property
    def key(self) -> str:
        """Cache key."""
        return self.lower

    @property
    def display(self) -> str:
        """Display string for the letter."""
        return f"{self.upper}{self.lower}"


# fmt: off
RUSSIAN_ALPHABET: List[RussianLetter] = [
    RussianLetter(1,  "А", "а", "ah",         "/a/",     "a as in father",        "vowel",     "арбуз",     "watermelon",  ""),
    RussianLetter(2,  "Б", "б", "beh",        "/b/",     "b as in bat",           "consonant", "банан",     "banana",      ""),
    RussianLetter(3,  "В", "в", "veh",        "/v/",     "v as in vine",          "consonant", "волк",      "wolf",        "Looks like English B but sounds like V!"),
    RussianLetter(4,  "Г", "г", "geh",        "/ɡ/",     "g as in go",            "consonant", "гриб",      "mushroom",    "Looks like an upside-down L"),
    RussianLetter(5,  "Д", "д", "deh",        "/d/",     "d as in dog",           "consonant", "дом",       "house",       "Looks like a little house"),
    RussianLetter(6,  "Е", "е", "yeh",        "/je/",    "ye as in yet",          "vowel",     "ежик",      "hedgehog",    "Looks like E but says 'ye'"),
    RussianLetter(7,  "Ё", "ё", "yo",         "/jo/",    "yo as in yoke",         "vowel",     "ёлка",      "Christmas tree", "Always stressed; dots are important!"),
    RussianLetter(8,  "Ж", "ж", "zheh",       "/ʐ/",     "zh as in treasure",     "consonant", "жук",       "beetle",      "Looks like a bug with legs spread out"),
    RussianLetter(9,  "З", "з", "zeh",        "/z/",     "z as in zoo",           "consonant", "зебра",     "zebra",       "Looks like the number 3"),
    RussianLetter(10, "И", "и", "ee",         "/i/",     "ee as in see",          "vowel",     "игра",      "game",        "Looks like a backwards N"),
    RussianLetter(11, "Й", "й", "ee kratkoe", "/j/",     "y as in boy",           "consonant", "йогурт",    "yogurt",      "Short ee — has a little hat (breve)"),
    RussianLetter(12, "К", "к", "kah",        "/k/",     "k as in kite",          "consonant", "кот",       "cat",         "Same as English K"),
    RussianLetter(13, "Л", "л", "el",         "/l/",     "l as in lamp",          "consonant", "лев",       "lion",        "Looks like a tent or Lambda"),
    RussianLetter(14, "М", "м", "em",         "/m/",     "m as in mom",           "consonant", "мяч",       "ball",        "Same as English M"),
    RussianLetter(15, "Н", "н", "en",         "/n/",     "n as in no",            "consonant", "нос",       "nose",        "Looks like English H but sounds like N!"),
    RussianLetter(16, "О", "о", "oh",         "/o/",     "o as in more",          "vowel",     "облако",    "cloud",       "Same as English O"),
    RussianLetter(17, "П", "п", "peh",        "/p/",     "p as in pet",           "consonant", "пицца",     "pizza",       "Looks like a goalpost or Greek Pi"),
    RussianLetter(18, "Р", "р", "er",         "/r/",     "r as in run (rolled)",  "consonant", "ракета",    "rocket",      "Looks like English P but sounds like R!"),
    RussianLetter(19, "С", "с", "es",         "/s/",     "s as in sun",           "consonant", "собака",    "dog",         "Looks like English C, sounds like S"),
    RussianLetter(20, "Т", "т", "teh",        "/t/",     "t as in top",           "consonant", "тигр",      "tiger",       "Same as English T"),
    RussianLetter(21, "У", "у", "oo",         "/u/",     "oo as in moon",         "vowel",     "утка",      "duck",        "Looks like a downward hook"),
    RussianLetter(22, "Ф", "ф", "ef",         "/f/",     "f as in fun",           "consonant", "футбол",    "football",    "Looks like a person with hands on hips"),
    RussianLetter(23, "Х", "х", "khah",       "/x/",     "h as in loch",          "consonant", "хлеб",      "bread",       "Same shape as English X, but sounds like 'kh'"),
    RussianLetter(24, "Ц", "ц", "tseh",       "/ts/",    "ts as in cats",         "consonant", "цветок",    "flower",      "Like Ч but with a hook"),
    RussianLetter(25, "Ч", "ч", "cheh",       "/tɕ/",    "ch as in cheese",       "consonant", "часы",      "clock/watch", "Looks like the number 4"),
    RussianLetter(26, "Ш", "ш", "shah",       "/ʂ/",     "sh as in ship",         "consonant", "шапка",     "hat",         "Looks like a comb with 3 teeth"),
    RussianLetter(27, "Щ", "щ", "shchah",     "/ɕː/",    "shch as in fresh cheese", "consonant", "щенок",   "puppy",       "Like Ш but with a tail — longer, softer sound"),
    RussianLetter(28, "Ъ", "ъ", "tvyordy znak", "",      "(hard sign — no sound)", "sign",     "",          "",            "Makes the consonant before it 'hard'; rare"),
    RussianLetter(29, "Ы", "ы", "y",          "/ɨ/",     "i as in bit (deeper)",  "vowel",     "рыба",      "fish",        "No English equivalent — say 'ee' but pull tongue back"),
    RussianLetter(30, "Ь", "ь", "myagky znak", "",       "(soft sign — no sound)", "sign",     "",          "",            "Makes the consonant before it 'soft'; very common"),
    RussianLetter(31, "Э", "э", "eh",         "/ɛ/",     "e as in met",           "vowel",     "экран",     "screen",      "Backwards E — pure 'eh' without the 'y' of Е"),
    RussianLetter(32, "Ю", "ю", "yu",         "/ju/",    "yu as in universe",     "vowel",     "юла",       "spinning top", ""),
    RussianLetter(33, "Я", "я", "yah",        "/ja/",    "ya as in yard",         "vowel",     "яблоко",    "apple",       "Last letter — looks like a backwards R"),
]
# fmt: on


def get_letter(char: str) -> RussianLetter:
    """Look up a letter by its upper or lower form."""
    char = char.strip()
    for letter in RUSSIAN_ALPHABET:
        if char in (letter.upper, letter.lower):
            return letter
    raise ValueError(f"Unknown Russian letter: {char!r}")


def get_all_letters() -> List[RussianLetter]:
    """Return all 33 letters in order."""
    return list(RUSSIAN_ALPHABET)
