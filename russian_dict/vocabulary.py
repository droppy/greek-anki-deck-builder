"""Russian vocabulary for kids — basic (150) + conversational (350) words."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RussianWord:
    """A single vocabulary entry."""

    russian: str  # Russian word
    english: str  # English translation
    theme: str  # Thematic category
    level: str  # "basic" or "conversational"
    pos: str  # Part of speech: noun, verb, adj, adv, phrase, num, pron
    gender: Optional[str] = None  # m, f, n (for nouns)
    plural: Optional[str] = None  # Plural form if irregular/useful
    notes: Optional[str] = None  # Extra info (e.g., "imperfective")

    @property
    def key(self) -> str:
        """Cache key — lowercase Russian word."""
        return self.russian.lower().strip()


# ── BASIC LEVEL (~150 words) ──────────────────────────────────────

_BASIC_WORDS = [
    # ── Greetings & Phrases (12) ──
    ("привет", "hello/hi", "phrases", "phrase"),
    ("пока", "bye", "phrases", "phrase"),
    ("да", "yes", "phrases", "phrase"),
    ("нет", "no", "phrases", "phrase"),
    ("спасибо", "thank you", "phrases", "phrase"),
    ("пожалуйста", "please / you're welcome", "phrases", "phrase"),
    ("извините", "sorry / excuse me", "phrases", "phrase"),
    ("хорошо", "good / okay", "phrases", "phrase"),
    ("доброе утро", "good morning", "phrases", "phrase"),
    ("спокойной ночи", "good night", "phrases", "phrase"),
    ("как дела?", "how are you?", "phrases", "phrase"),
    ("меня зовут", "my name is", "phrases", "phrase"),

    # ── Family (12) ──
    ("мама", "mom", "family", "noun", "f"),
    ("папа", "dad", "family", "noun", "m"),
    ("брат", "brother", "family", "noun", "m"),
    ("сестра", "sister", "family", "noun", "f"),
    ("бабушка", "grandma", "family", "noun", "f"),
    ("дедушка", "grandpa", "family", "noun", "m"),
    ("семья", "family", "family", "noun", "f"),
    ("сын", "son", "family", "noun", "m"),
    ("дочь", "daughter", "family", "noun", "f"),
    ("ребёнок", "child", "family", "noun", "m"),
    ("друг", "friend (m)", "family", "noun", "m"),
    ("подруга", "friend (f)", "family", "noun", "f"),

    # ── Animals (15) ──
    ("кот", "cat", "animals", "noun", "m"),
    ("собака", "dog", "animals", "noun", "f"),
    ("рыба", "fish", "animals", "noun", "f"),
    ("птица", "bird", "animals", "noun", "f"),
    ("медведь", "bear", "animals", "noun", "m"),
    ("заяц", "rabbit/hare", "animals", "noun", "m"),
    ("лошадь", "horse", "animals", "noun", "f"),
    ("корова", "cow", "animals", "noun", "f"),
    ("свинья", "pig", "animals", "noun", "f"),
    ("мышь", "mouse", "animals", "noun", "f"),
    ("лев", "lion", "animals", "noun", "m"),
    ("слон", "elephant", "animals", "noun", "m"),
    ("волк", "wolf", "animals", "noun", "m"),
    ("лиса", "fox", "animals", "noun", "f"),
    ("утка", "duck", "animals", "noun", "f"),

    # ── Colors (10) ──
    ("красный", "red", "colors", "adj"),
    ("синий", "blue", "colors", "adj"),
    ("зелёный", "green", "colors", "adj"),
    ("жёлтый", "yellow", "colors", "adj"),
    ("белый", "white", "colors", "adj"),
    ("чёрный", "black", "colors", "adj"),
    ("оранжевый", "orange", "colors", "adj"),
    ("розовый", "pink", "colors", "adj"),
    ("коричневый", "brown", "colors", "adj"),
    ("серый", "gray", "colors", "adj"),

    # ── Numbers (12) ──
    ("один", "one", "numbers", "num"),
    ("два", "two", "numbers", "num"),
    ("три", "three", "numbers", "num"),
    ("четыре", "four", "numbers", "num"),
    ("пять", "five", "numbers", "num"),
    ("шесть", "six", "numbers", "num"),
    ("семь", "seven", "numbers", "num"),
    ("восемь", "eight", "numbers", "num"),
    ("девять", "nine", "numbers", "num"),
    ("десять", "ten", "numbers", "num"),
    ("сто", "hundred", "numbers", "num"),
    ("ноль", "zero", "numbers", "num"),

    # ── Food & Drink (16) ──
    ("хлеб", "bread", "food", "noun", "m"),
    ("молоко", "milk", "food", "noun", "n"),
    ("вода", "water", "food", "noun", "f"),
    ("яблоко", "apple", "food", "noun", "n"),
    ("банан", "banana", "food", "noun", "m"),
    ("сыр", "cheese", "food", "noun", "m"),
    ("суп", "soup", "food", "noun", "m"),
    ("каша", "porridge", "food", "noun", "f"),
    ("мясо", "meat", "food", "noun", "n"),
    ("рис", "rice", "food", "noun", "m"),
    ("яйцо", "egg", "food", "noun", "n"),
    ("торт", "cake", "food", "noun", "m"),
    ("мороженое", "ice cream", "food", "noun", "n"),
    ("сок", "juice", "food", "noun", "m"),
    ("чай", "tea", "food", "noun", "m"),
    ("конфета", "candy", "food", "noun", "f"),

    # ── Body (12) ──
    ("голова", "head", "body", "noun", "f"),
    ("рука", "hand/arm", "body", "noun", "f"),
    ("нога", "leg/foot", "body", "noun", "f"),
    ("глаз", "eye", "body", "noun", "m"),
    ("нос", "nose", "body", "noun", "m"),
    ("рот", "mouth", "body", "noun", "m"),
    ("ухо", "ear", "body", "noun", "n"),
    ("зуб", "tooth", "body", "noun", "m"),
    ("палец", "finger/toe", "body", "noun", "m"),
    ("живот", "belly/stomach", "body", "noun", "m"),
    ("спина", "back", "body", "noun", "f"),
    ("сердце", "heart", "body", "noun", "n"),

    # ── Home & Objects (14) ──
    ("дом", "house/home", "home", "noun", "m"),
    ("стол", "table", "home", "noun", "m"),
    ("стул", "chair", "home", "noun", "m"),
    ("кровать", "bed", "home", "noun", "f"),
    ("окно", "window", "home", "noun", "n"),
    ("дверь", "door", "home", "noun", "f"),
    ("книга", "book", "home", "noun", "f"),
    ("мяч", "ball", "home", "noun", "m"),
    ("игрушка", "toy", "home", "noun", "f"),
    ("телефон", "phone", "home", "noun", "m"),
    ("ключ", "key", "home", "noun", "m"),
    ("часы", "clock/watch", "home", "noun", "m"),
    ("лампа", "lamp", "home", "noun", "f"),
    ("зеркало", "mirror", "home", "noun", "n"),

    # ── Clothes (8) ──
    ("шапка", "hat", "clothes", "noun", "f"),
    ("куртка", "jacket", "clothes", "noun", "f"),
    ("ботинки", "shoes/boots", "clothes", "noun", "m"),
    ("штаны", "pants", "clothes", "noun", "m"),
    ("платье", "dress", "clothes", "noun", "n"),
    ("футболка", "t-shirt", "clothes", "noun", "f"),
    ("носки", "socks", "clothes", "noun", "m"),
    ("варежки", "mittens", "clothes", "noun", "f"),

    # ── Nature & Weather (10) ──
    ("солнце", "sun", "nature", "noun", "n"),
    ("луна", "moon", "nature", "noun", "f"),
    ("звезда", "star", "nature", "noun", "f"),
    ("дерево", "tree", "nature", "noun", "n"),
    ("цветок", "flower", "nature", "noun", "m"),
    ("снег", "snow", "nature", "noun", "m"),
    ("дождь", "rain", "nature", "noun", "m"),
    ("небо", "sky", "nature", "noun", "n"),
    ("река", "river", "nature", "noun", "f"),
    ("море", "sea", "nature", "noun", "n"),

    # ── Basic Verbs (18) ──
    ("есть", "to eat", "verbs", "verb"),
    ("пить", "to drink", "verbs", "verb"),
    ("спать", "to sleep", "verbs", "verb"),
    ("идти", "to go/walk", "verbs", "verb"),
    ("бежать", "to run", "verbs", "verb"),
    ("играть", "to play", "verbs", "verb"),
    ("читать", "to read", "verbs", "verb"),
    ("писать", "to write", "verbs", "verb"),
    ("рисовать", "to draw", "verbs", "verb"),
    ("смотреть", "to look/watch", "verbs", "verb"),
    ("слушать", "to listen", "verbs", "verb"),
    ("говорить", "to speak/say", "verbs", "verb"),
    ("хотеть", "to want", "verbs", "verb"),
    ("любить", "to love/like", "verbs", "verb"),
    ("знать", "to know", "verbs", "verb"),
    ("мочь", "can/to be able", "verbs", "verb"),
    ("дать", "to give", "verbs", "verb"),
    ("делать", "to do/make", "verbs", "verb"),

    # ── Basic Adjectives (10) ──
    ("большой", "big", "adjectives", "adj"),
    ("маленький", "small/little", "adjectives", "adj"),
    ("хороший", "good", "adjectives", "adj"),
    ("плохой", "bad", "adjectives", "adj"),
    ("новый", "new", "adjectives", "adj"),
    ("старый", "old", "adjectives", "adj"),
    ("горячий", "hot", "adjectives", "adj"),
    ("холодный", "cold", "adjectives", "adj"),
    ("вкусный", "tasty/delicious", "adjectives", "adj"),
    ("красивый", "beautiful/pretty", "adjectives", "adj"),
]

# ── CONVERSATIONAL LEVEL (~350 words, extends basic) ──────────────

_CONVERSATIONAL_WORDS = [
    # ── More Phrases (15) ──
    ("до свидания", "goodbye (formal)", "phrases", "phrase"),
    ("добрый день", "good afternoon", "phrases", "phrase"),
    ("добрый вечер", "good evening", "phrases", "phrase"),
    ("я не понимаю", "I don't understand", "phrases", "phrase"),
    ("повторите, пожалуйста", "please repeat", "phrases", "phrase"),
    ("сколько это стоит?", "how much does it cost?", "phrases", "phrase"),
    ("где туалет?", "where is the bathroom?", "phrases", "phrase"),
    ("помогите", "help!", "phrases", "phrase"),
    ("я хочу", "I want", "phrases", "phrase"),
    ("мне нравится", "I like (it)", "phrases", "phrase"),
    ("мне не нравится", "I don't like (it)", "phrases", "phrase"),
    ("я люблю", "I love", "phrases", "phrase"),
    ("можно?", "may I? / is it okay?", "phrases", "phrase"),
    ("конечно", "of course", "phrases", "phrase"),
    ("правильно", "correct/right", "phrases", "phrase"),

    # ── More Family & People (10) ──
    ("тётя", "aunt", "family", "noun", "f"),
    ("дядя", "uncle", "family", "noun", "m"),
    ("двоюродный брат", "cousin (m)", "family", "noun", "m"),
    ("двоюродная сестра", "cousin (f)", "family", "noun", "f"),
    ("мальчик", "boy", "people", "noun", "m"),
    ("девочка", "girl", "people", "noun", "f"),
    ("мужчина", "man", "people", "noun", "m"),
    ("женщина", "woman", "people", "noun", "f"),
    ("учитель", "teacher", "people", "noun", "m"),
    ("врач", "doctor", "people", "noun", "m"),

    # ── More Animals (12) ──
    ("черепаха", "turtle", "animals", "noun", "f"),
    ("обезьяна", "monkey", "animals", "noun", "f"),
    ("жираф", "giraffe", "animals", "noun", "m"),
    ("крокодил", "crocodile", "animals", "noun", "m"),
    ("бабочка", "butterfly", "animals", "noun", "f"),
    ("паук", "spider", "animals", "noun", "m"),
    ("змея", "snake", "animals", "noun", "f"),
    ("петух", "rooster", "animals", "noun", "m"),
    ("курица", "chicken/hen", "animals", "noun", "f"),
    ("овца", "sheep", "animals", "noun", "f"),
    ("коза", "goat", "animals", "noun", "f"),
    ("ёжик", "hedgehog", "animals", "noun", "m"),

    # ── More Food (14) ──
    ("масло", "butter/oil", "food", "noun", "n"),
    ("картошка", "potato", "food", "noun", "f"),
    ("морковь", "carrot", "food", "noun", "f"),
    ("помидор", "tomato", "food", "noun", "m"),
    ("огурец", "cucumber", "food", "noun", "m"),
    ("апельсин", "orange (fruit)", "food", "noun", "m"),
    ("клубника", "strawberry", "food", "noun", "f"),
    ("арбуз", "watermelon", "food", "noun", "m"),
    ("пицца", "pizza", "food", "noun", "f"),
    ("макароны", "pasta", "food", "noun", "m"),
    ("печенье", "cookie/biscuit", "food", "noun", "n"),
    ("шоколад", "chocolate", "food", "noun", "m"),
    ("завтрак", "breakfast", "food", "noun", "m"),
    ("обед", "lunch", "food", "noun", "m"),
    # ("ужин", "dinner", "food", "noun", "m"),  -- added below in daily life

    # ── Places (15) ──
    ("школа", "school", "places", "noun", "f"),
    ("парк", "park", "places", "noun", "m"),
    ("магазин", "store/shop", "places", "noun", "m"),
    ("улица", "street", "places", "noun", "f"),
    ("город", "city", "places", "noun", "m"),
    ("деревня", "village", "places", "noun", "f"),
    ("больница", "hospital", "places", "noun", "f"),
    ("библиотека", "library", "places", "noun", "f"),
    ("аэропорт", "airport", "places", "noun", "m"),
    ("вокзал", "train station", "places", "noun", "m"),
    ("площадь", "square/plaza", "places", "noun", "f"),
    ("музей", "museum", "places", "noun", "m"),
    ("театр", "theater", "places", "noun", "m"),
    ("зоопарк", "zoo", "places", "noun", "m"),
    ("пляж", "beach", "places", "noun", "m"),

    # ── Transport (8) ──
    ("машина", "car", "transport", "noun", "f"),
    ("автобус", "bus", "transport", "noun", "m"),
    ("поезд", "train", "transport", "noun", "m"),
    ("самолёт", "airplane", "transport", "noun", "m"),
    ("велосипед", "bicycle", "transport", "noun", "m"),
    ("корабль", "ship", "transport", "noun", "m"),
    ("метро", "metro/subway", "transport", "noun", "n"),
    ("такси", "taxi", "transport", "noun", "n"),

    # ── More Home & Objects (12) ──
    ("кухня", "kitchen", "home", "noun", "f"),
    ("ванная", "bathroom", "home", "noun", "f"),
    ("комната", "room", "home", "noun", "f"),
    ("пол", "floor", "home", "noun", "m"),
    ("стена", "wall", "home", "noun", "f"),
    ("потолок", "ceiling", "home", "noun", "m"),
    ("холодильник", "refrigerator", "home", "noun", "m"),
    ("компьютер", "computer", "home", "noun", "m"),
    ("тарелка", "plate", "home", "noun", "f"),
    ("чашка", "cup", "home", "noun", "f"),
    ("ложка", "spoon", "home", "noun", "f"),
    ("вилка", "fork", "home", "noun", "f"),

    # ── More Nature & Weather (10) ──
    ("ветер", "wind", "nature", "noun", "m"),
    ("облако", "cloud", "nature", "noun", "n"),
    ("гора", "mountain", "nature", "noun", "f"),
    ("озеро", "lake", "nature", "noun", "n"),
    ("лес", "forest", "nature", "noun", "m"),
    ("трава", "grass", "nature", "noun", "f"),
    ("камень", "stone/rock", "nature", "noun", "m"),
    ("песок", "sand", "nature", "noun", "m"),
    ("остров", "island", "nature", "noun", "m"),
    ("земля", "earth/ground", "nature", "noun", "f"),

    # ── More Clothes (8) ──
    ("пальто", "coat", "clothes", "noun", "n"),
    ("рубашка", "shirt", "clothes", "noun", "f"),
    ("юбка", "skirt", "clothes", "noun", "f"),
    ("шарф", "scarf", "clothes", "noun", "m"),
    ("перчатки", "gloves", "clothes", "noun", "f"),
    ("очки", "glasses", "clothes", "noun", "m"),
    ("сумка", "bag", "clothes", "noun", "f"),
    ("зонт", "umbrella", "clothes", "noun", "m"),

    # ── More Body (6) ──
    ("волосы", "hair", "body", "noun", "m"),
    ("лицо", "face", "body", "noun", "n"),
    ("шея", "neck", "body", "noun", "f"),
    ("плечо", "shoulder", "body", "noun", "n"),
    ("колено", "knee", "body", "noun", "n"),
    ("кожа", "skin", "body", "noun", "f"),

    # ── Daily Life (12) ──
    ("утро", "morning", "time", "noun", "n"),
    ("день", "day/afternoon", "time", "noun", "m"),
    ("вечер", "evening", "time", "noun", "m"),
    ("ночь", "night", "time", "noun", "f"),
    ("сегодня", "today", "time", "adv"),
    ("завтра", "tomorrow", "time", "adv"),
    ("вчера", "yesterday", "time", "adv"),
    ("сейчас", "now", "time", "adv"),
    ("потом", "then/later", "time", "adv"),
    ("всегда", "always", "time", "adv"),
    ("никогда", "never", "time", "adv"),
    ("ужин", "dinner", "food", "noun", "m"),

    # ── Days & Months (12) ──
    ("понедельник", "Monday", "time", "noun", "m"),
    ("вторник", "Tuesday", "time", "noun", "m"),
    ("среда", "Wednesday", "time", "noun", "f"),
    ("четверг", "Thursday", "time", "noun", "m"),
    ("пятница", "Friday", "time", "noun", "f"),
    ("суббота", "Saturday", "time", "noun", "f"),
    ("воскресенье", "Sunday", "time", "noun", "n"),
    ("неделя", "week", "time", "noun", "f"),
    ("месяц", "month", "time", "noun", "m"),
    ("год", "year", "time", "noun", "m"),
    ("зима", "winter", "time", "noun", "f"),
    ("лето", "summer", "time", "noun", "n"),

    # ── More Verbs (30) ──
    ("петь", "to sing", "verbs", "verb"),
    ("танцевать", "to dance", "verbs", "verb"),
    ("плавать", "to swim", "verbs", "verb"),
    ("прыгать", "to jump", "verbs", "verb"),
    ("сидеть", "to sit", "verbs", "verb"),
    ("стоять", "to stand", "verbs", "verb"),
    ("лежать", "to lie down", "verbs", "verb"),
    ("открыть", "to open", "verbs", "verb"),
    ("закрыть", "to close", "verbs", "verb"),
    ("взять", "to take", "verbs", "verb"),
    ("положить", "to put/place", "verbs", "verb"),
    ("найти", "to find", "verbs", "verb"),
    ("потерять", "to lose", "verbs", "verb"),
    ("купить", "to buy", "verbs", "verb"),
    ("учить", "to learn/teach", "verbs", "verb"),
    ("помогать", "to help", "verbs", "verb"),
    ("ждать", "to wait", "verbs", "verb"),
    ("думать", "to think", "verbs", "verb"),
    ("понимать", "to understand", "verbs", "verb"),
    ("видеть", "to see", "verbs", "verb"),
    ("слышать", "to hear", "verbs", "verb"),
    ("начать", "to begin/start", "verbs", "verb"),
    ("кончить", "to finish/end", "verbs", "verb"),
    ("мыть", "to wash", "verbs", "verb"),
    ("готовить", "to cook", "verbs", "verb"),
    ("одеваться", "to get dressed", "verbs", "verb"),
    ("гулять", "to walk/stroll", "verbs", "verb"),
    ("летать", "to fly", "verbs", "verb"),
    ("падать", "to fall", "verbs", "verb"),
    ("нести", "to carry", "verbs", "verb"),

    # ── More Adjectives (20) ──
    ("быстрый", "fast/quick", "adjectives", "adj"),
    ("медленный", "slow", "adjectives", "adj"),
    ("длинный", "long", "adjectives", "adj"),
    ("короткий", "short (length)", "adjectives", "adj"),
    ("высокий", "tall/high", "adjectives", "adj"),
    ("низкий", "short/low", "adjectives", "adj"),
    ("тяжёлый", "heavy", "adjectives", "adj"),
    ("лёгкий", "light/easy", "adjectives", "adj"),
    ("сильный", "strong", "adjectives", "adj"),
    ("слабый", "weak", "adjectives", "adj"),
    ("умный", "smart/clever", "adjectives", "adj"),
    ("глупый", "silly/stupid", "adjectives", "adj"),
    ("весёлый", "fun/cheerful", "adjectives", "adj"),
    ("грустный", "sad", "adjectives", "adj"),
    ("добрый", "kind", "adjectives", "adj"),
    ("злой", "angry/evil", "adjectives", "adj"),
    ("чистый", "clean", "adjectives", "adj"),
    ("грязный", "dirty", "adjectives", "adj"),
    ("мягкий", "soft", "adjectives", "adj"),
    ("твёрдый", "hard/solid", "adjectives", "adj"),

    # ── Question Words & Pronouns (15) ──
    ("я", "I", "pronouns", "pron"),
    ("ты", "you (informal)", "pronouns", "pron"),
    ("он", "he", "pronouns", "pron"),
    ("она", "she", "pronouns", "pron"),
    ("мы", "we", "pronouns", "pron"),
    ("они", "they", "pronouns", "pron"),
    ("кто", "who", "pronouns", "pron"),
    ("что", "what", "pronouns", "pron"),
    ("где", "where", "pronouns", "adv"),
    ("когда", "when", "pronouns", "adv"),
    ("почему", "why", "pronouns", "adv"),
    ("как", "how", "pronouns", "adv"),
    ("сколько", "how much/many", "pronouns", "adv"),
    ("этот", "this", "pronouns", "pron"),
    ("тот", "that", "pronouns", "pron"),

    # ── Prepositions & Connectors (15) ──
    ("в", "in/into", "grammar", "prep"),
    ("на", "on/onto", "grammar", "prep"),
    ("с", "with", "grammar", "prep"),
    ("без", "without", "grammar", "prep"),
    ("для", "for", "grammar", "prep"),
    ("от", "from", "grammar", "prep"),
    ("до", "before/until", "grammar", "prep"),
    ("после", "after", "grammar", "prep"),
    ("и", "and", "grammar", "conj"),
    ("но", "but", "grammar", "conj"),
    ("или", "or", "grammar", "conj"),
    ("потому что", "because", "grammar", "conj"),
    ("тоже", "also/too", "grammar", "adv"),
    ("очень", "very", "grammar", "adv"),
    ("уже", "already", "grammar", "adv"),

    # ── Emotions & States (12) ──
    ("счастливый", "happy", "emotions", "adj"),
    ("голодный", "hungry", "emotions", "adj"),
    ("усталый", "tired", "emotions", "adj"),
    ("больной", "sick/ill", "emotions", "adj"),
    ("испуганный", "scared", "emotions", "adj"),
    ("сердитый", "angry/mad", "emotions", "adj"),
    ("удивлённый", "surprised", "emotions", "adj"),
    ("скучно", "boring/bored", "emotions", "adv"),
    ("интересно", "interesting", "emotions", "adv"),
    ("страшно", "scary/frightening", "emotions", "adv"),
    ("смешно", "funny", "emotions", "adv"),
    ("здоровый", "healthy", "emotions", "adj"),

    # ── School & Activities (12) ──
    ("урок", "lesson", "school", "noun", "m"),
    ("класс", "class/classroom", "school", "noun", "m"),
    ("ручка", "pen", "school", "noun", "f"),
    ("карандаш", "pencil", "school", "noun", "m"),
    ("тетрадь", "notebook", "school", "noun", "f"),
    ("рюкзак", "backpack", "school", "noun", "m"),
    ("домашнее задание", "homework", "school", "noun", "n"),
    ("перемена", "recess/break", "school", "noun", "f"),
    ("математика", "math", "school", "noun", "f"),
    ("музыка", "music", "school", "noun", "f"),
    ("спорт", "sport", "school", "noun", "m"),
    ("каникулы", "vacation/holidays", "school", "noun", "m"),

    # ── More Numbers (8) ──
    ("двадцать", "twenty", "numbers", "num"),
    ("тридцать", "thirty", "numbers", "num"),
    ("сорок", "forty", "numbers", "num"),
    ("пятьдесят", "fifty", "numbers", "num"),
    ("первый", "first", "numbers", "adj"),
    ("второй", "second", "numbers", "adj"),
    ("третий", "third", "numbers", "adj"),
    ("последний", "last", "numbers", "adj"),
]


def _build_word(raw: tuple) -> RussianWord:
    """Build a RussianWord from a raw tuple."""
    russian, english, theme, pos = raw[0], raw[1], raw[2], raw[3]
    gender = raw[4] if len(raw) > 4 else None
    return RussianWord(
        russian=russian, english=english, theme=theme,
        level="basic", pos=pos, gender=gender,
    )


def _build_words(raw_list: list, level: str) -> List[RussianWord]:
    words = []
    for raw in raw_list:
        w = _build_word(raw)
        w.level = level
        words.append(w)
    return words


# Pre-built word lists
BASIC_WORDS: List[RussianWord] = _build_words(_BASIC_WORDS, "basic")
CONVERSATIONAL_WORDS: List[RussianWord] = _build_words(_CONVERSATIONAL_WORDS, "conversational")
ALL_WORDS: List[RussianWord] = BASIC_WORDS + CONVERSATIONAL_WORDS


def get_words(level: str = "basic") -> List[RussianWord]:
    """Get words for a given level.

    'basic' returns ~150 starter words.
    'conversational' returns ~350 additional words.
    'all' returns all ~500 words (basic + conversational).
    """
    if level == "basic":
        return list(BASIC_WORDS)
    elif level == "conversational":
        return list(CONVERSATIONAL_WORDS)
    elif level == "all":
        return list(ALL_WORDS)
    else:
        raise ValueError(f"Unknown level: {level!r}. Use 'basic', 'conversational', or 'all'.")


def get_themes() -> dict:
    """Return dict of {theme: count} across all words."""
    themes = {}
    for w in ALL_WORDS:
        themes[w.theme] = themes.get(w.theme, 0) + 1
    return dict(sorted(themes.items(), key=lambda x: -x[1]))


def get_word(russian: str) -> Optional[RussianWord]:
    """Look up a word by Russian text."""
    key = russian.lower().strip()
    for w in ALL_WORDS:
        if w.key == key:
            return w
    return None
