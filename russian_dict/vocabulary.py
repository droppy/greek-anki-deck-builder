"""Russian vocabulary for kids — basic (~283) + conversational (~372) words.

Order is by IMPORTANCE for daily use, not topical/alphabetical:
  TIER 1: Survival phrases (привет, спасибо, мама, я, помоги мне) — used every day
  TIER 2: Foundational grammar (gender, adjective endings, verb conjugation)
  TIER 3: Needs & feelings (хочу пить, болит живот) — body/emotional needs
  TIER 4: Asking the teacher / classmates (у тебя есть, можно в туалет?)
  TIER 5: Adult-to-kid commands (молодец, осторожно, садись)
  TIER 6: Social play invites (пойдём играть, можно с тобой?)
  TIER 7+: Topical expansion (verbs, adjectives, animals, food, etc.)

Cards with pos="grammar" are pre-filled from GRAMMAR_PRESETS in grammar_presets.py
and skip the API call.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RussianWord:
    """A single vocabulary entry."""

    russian: str  # Russian word
    english: str  # English translation
    theme: str  # Thematic category
    level: str  # "basic" or "conversational"
    pos: str  # Part of speech: noun, verb, adj, adv, phrase, num, pron, grammar
    gender: Optional[str] = None  # m, f, n (for nouns)
    plural: Optional[str] = None  # Plural form if irregular/useful
    notes: Optional[str] = None  # Extra info (e.g., "imperfective")

    @property
    def key(self) -> str:
        """Cache key — lowercase Russian word."""
        return self.russian.lower().strip()


# ── BASIC LEVEL (~283 words) ──────────────────────────────────────
# Ordered by importance for a 6yo English-speaking kid in a 70%-Russian
# classroom. The first ~100 cards are the daily-survival set.

_BASIC_WORDS = [
    # ── TIER 1: Survival phrases (21) — said/heard every day ──
    ("привет", "hello/hi", "phrases", "phrase"),
    ("пока", "bye", "phrases", "phrase"),
    ("да", "yes", "phrases", "phrase"),
    ("нет", "no", "phrases", "phrase"),
    ("спасибо", "thank you", "phrases", "phrase"),
    ("пожалуйста", "please / you're welcome", "phrases", "phrase"),
    ("извините", "sorry / excuse me", "phrases", "phrase"),
    ("хорошо", "good / okay", "phrases", "phrase"),
    ("я", "I", "pronouns", "pron"),
    ("ты", "you (informal)", "pronouns", "pron"),
    ("мама", "mom", "family", "noun", "f"),
    ("папа", "dad", "family", "noun", "m"),
    ("меня зовут", "my name is", "phrases", "phrase"),
    ("как дела?", "how are you?", "phrases", "phrase"),
    ("доброе утро", "good morning", "phrases", "phrase"),
    ("спокойной ночи", "good night", "phrases", "phrase"),
    ("молодец!", "good job!", "commands", "phrase"),
    ("помоги мне", "help me", "school_phrases", "phrase"),
    ("где", "where", "pronouns", "adv"),
    ("что", "what", "pronouns", "pron"),
    ("кто", "who", "pronouns", "pron"),

    # ── TIER 2: Foundational grammar (12) — see GRAMMAR_PRESETS ──
    ("он, она, оно", "he/she/it — every Russian noun has a gender", "grammar_concepts", "grammar"),
    ("род существительных", "How to tell noun gender from the last letter", "grammar_concepts", "grammar"),
    ("большой / большая / большое / большие", "BIG — adjective changes by noun gender", "grammar_concepts", "grammar"),
    ("красный / красная / красное / красные", "RED — same pattern; -ый instead of -ой", "grammar_concepts", "grammar"),
    ("хороший / хорошая / хорошее / хорошие", "GOOD — gender pattern with hush-letter spelling rule", "grammar_concepts", "grammar"),
    ("мой / моя / моё / мои", "MY — possessives change by noun gender", "grammar_concepts", "grammar"),
    ("твой / твоя / твоё / твои", "YOUR (informal) — same four endings", "grammar_concepts", "grammar"),
    ("этот / эта / это / эти", "THIS — demonstratives match the noun's gender", "grammar_concepts", "grammar"),
    ("я хочу, ты хочешь, он хочет", "Verbs change by WHO does it — хотеть (to want)", "grammar_concepts", "grammar"),
    ("я ем, ты ешь, он ест", "есть (to eat) — same conjugation idea, six endings", "grammar_concepts", "grammar"),
    ("я сказал / я сказала", "Past tense changes with the speaker's gender (boy/girl!)", "grammar_concepts", "grammar"),
    ("столы, книги, окна, дома", "How plurals form — usually -ы/-и, neuter -о→-а", "grammar_concepts", "grammar"),

    # ── TIER 3: Needs & feelings (14) — мне ___ / хочу ___ / болит ___ ──
    ("хочу пить", "I want a drink", "needs", "phrase"),
    ("хочу есть", "I'm hungry", "needs", "phrase"),
    ("хочу домой", "I want to go home", "needs", "phrase"),
    ("мне холодно", "I'm cold", "needs", "phrase"),
    ("мне жарко", "I'm hot", "needs", "phrase"),
    ("мне страшно", "I'm scared", "needs", "phrase"),
    ("мне скучно", "I'm bored", "needs", "phrase"),
    ("мне грустно", "I'm sad", "needs", "phrase"),
    ("мне больно", "it hurts", "needs", "phrase"),
    ("болит живот", "my stomach hurts", "needs", "phrase"),
    ("болит голова", "my head hurts", "needs", "phrase"),
    ("я устала", "I'm tired", "needs", "phrase"),
    ("я не могу", "I can't", "needs", "phrase"),
    ("я сама!", "I'll do it myself!", "needs", "phrase"),

    # ── TIER 4: Asking teacher / classmates (11) ──
    ("у тебя есть...?", "do you have...?", "school_phrases", "phrase"),
    ("можно взять?", "may I borrow it?", "school_phrases", "phrase"),
    ("дай, пожалуйста", "pass it please", "school_phrases", "phrase"),
    ("поделись со мной", "share with me", "school_phrases", "phrase"),
    ("я забыла дома", "I forgot it at home", "school_phrases", "phrase"),
    ("у меня нет", "I don't have one", "school_phrases", "phrase"),
    ("где...?", "where is...?", "school_phrases", "phrase"),
    ("можно в туалет?", "may I go to the bathroom?", "school_phrases", "phrase"),
    ("можно попить?", "may I get a drink?", "school_phrases", "phrase"),
    ("я закончила", "I'm done", "school_phrases", "phrase"),
    ("я не знаю", "I don't know", "school_phrases", "phrase"),

    # ── TIER 5: Adult-to-kid commands (9) — receptive vocabulary ──
    ("умница!", "clever girl!", "commands", "phrase"),
    ("осторожно!", "watch out!", "commands", "phrase"),
    ("аккуратно", "be careful / neatly", "commands", "phrase"),
    ("нельзя", "not allowed / don't", "commands", "phrase"),
    ("иди сюда", "come here", "commands", "phrase"),
    ("садись", "sit down", "commands", "phrase"),
    ("тише", "quieter / shh", "commands", "phrase"),
    ("покажи", "show me", "commands", "phrase"),
    ("подними руку", "raise your hand", "commands", "phrase"),

    # ── TIER 6: Social play invites (7) ──
    ("пойдём играть!", "let's go play!", "social", "phrase"),
    ("хочешь поиграть?", "want to play?", "social", "phrase"),
    ("давай вместе", "let's do it together", "social", "phrase"),
    ("можно с тобой?", "may I join you?", "social", "phrase"),
    ("что ты делаешь?", "what are you doing?", "social", "phrase"),
    ("что вы играете?", "what are you playing?", "social", "phrase"),
    ("я тоже хочу", "I want to too", "social", "phrase"),

    # ── TIER 7: Family & close people (10) ──
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

    # ── TIER 8: Foundational verbs (53) ──
    # Daily survival verbs (existing 18)
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
    # Motion (8)
    ("пойти", "to set off (walking)", "verbs", "verb"),
    ("поехать", "to set off (by transport)", "verbs", "verb"),
    ("прийти", "to arrive (walking)", "verbs", "verb"),
    ("приехать", "to arrive (by transport)", "verbs", "verb"),
    ("уйти", "to leave (walking)", "verbs", "verb"),
    ("уехать", "to leave (by transport)", "verbs", "verb"),
    ("встать", "to get up / stand up", "verbs", "verb"),
    ("упасть", "to fall", "verbs", "verb"),
    # Daily routine (10)
    ("просыпаться", "to wake up", "verbs", "verb"),
    ("вставать", "to get up (impf)", "verbs", "verb"),
    ("умываться", "to wash one's face", "verbs", "verb"),
    ("чистить зубы", "to brush teeth", "verbs", "verb"),
    ("одеться", "to get dressed (perf)", "verbs", "verb"),
    ("раздеться", "to get undressed", "verbs", "verb"),
    ("завтракать", "to have breakfast", "verbs", "verb"),
    ("обедать", "to have lunch", "verbs", "verb"),
    ("ужинать", "to have dinner", "verbs", "verb"),
    ("отдыхать", "to rest", "verbs", "verb"),
    # Communication (8)
    ("спросить", "to ask (perf)", "verbs", "verb"),
    ("ответить", "to answer (perf)", "verbs", "verb"),
    ("сказать", "to say (perf)", "verbs", "verb"),
    ("рассказать", "to tell (a story)", "verbs", "verb"),
    ("смеяться", "to laugh", "verbs", "verb"),
    ("плакать", "to cry", "verbs", "verb"),
    ("улыбаться", "to smile", "verbs", "verb"),
    ("обнимать", "to hug", "verbs", "verb"),
    # School / cognitive (5)
    ("учиться", "to study (be a student)", "verbs", "verb"),
    ("запомнить", "to memorize", "verbs", "verb"),
    ("забыть", "to forget", "verbs", "verb"),
    ("считать", "to count", "verbs", "verb"),
    ("повторять", "to repeat (impf)", "verbs", "verb"),
    # Action (4)
    ("показать", "to show", "verbs", "verb"),
    ("принести", "to bring", "verbs", "verb"),
    ("бросать", "to throw", "verbs", "verb"),
    ("ловить", "to catch", "verbs", "verb"),

    # ── TIER 9: Foundational adjectives (25) ──
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
    # NEW basic adj — sensory + texture + character (15)
    ("мокрый", "wet", "adjectives", "adj"),
    ("сухой", "dry", "adjectives", "adj"),
    ("сладкий", "sweet", "adjectives", "adj"),
    ("кислый", "sour", "adjectives", "adj"),
    ("солёный", "salty", "adjectives", "adj"),
    ("круглый", "round", "adjectives", "adj"),
    ("толстый", "thick / fat", "adjectives", "adj"),
    ("тонкий", "thin", "adjectives", "adj"),
    ("громкий", "loud", "adjectives", "adj"),
    ("тихий", "quiet", "adjectives", "adj"),
    ("смелый", "brave", "adjectives", "adj"),
    ("стеснительный", "shy", "adjectives", "adj"),
    ("важный", "important", "adjectives", "adj"),
    ("любимый", "favorite", "adjectives", "adj"),
    ("готовый", "ready", "adjectives", "adj"),

    # ── TIER 10: School objects (18) ──
    ("фломастер", "marker", "school", "noun", "m"),
    ("ластик", "eraser", "school", "noun", "m"),
    ("ножницы", "scissors", "school", "noun", "f"),
    ("клей", "glue", "school", "noun", "m"),
    ("линейка", "ruler", "school", "noun", "f"),
    ("точилка", "pencil sharpener", "school", "noun", "f"),
    ("краски", "paints", "school", "noun", "f"),
    ("кисточка", "paintbrush", "school", "noun", "f"),
    ("пластилин", "playdough", "school", "noun", "m"),
    ("бумага", "paper", "school", "noun", "f"),
    ("альбом", "drawing pad", "school", "noun", "m"),
    ("пенал", "pencil case", "school", "noun", "m"),
    ("доска", "board (whiteboard/chalkboard)", "school", "noun", "f"),
    ("парта", "school desk", "school", "noun", "f"),
    ("учительница", "teacher (f)", "school", "noun", "f"),
    ("одноклассница", "classmate (f)", "school", "noun", "f"),
    ("столовая", "cafeteria", "school", "noun", "f"),
    ("раздевалка", "cloakroom", "school", "noun", "f"),

    # ── TIER 11: Body (12) ──
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

    # ── TIER 12: Food & drink (16) ──
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

    # ── TIER 13: Home & objects (14) ──
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

    # ── TIER 14: Clothes (8) ──
    ("шапка", "hat", "clothes", "noun", "f"),
    ("куртка", "jacket", "clothes", "noun", "f"),
    ("ботинки", "shoes/boots", "clothes", "noun", "m"),
    ("штаны", "pants", "clothes", "noun", "m"),
    ("платье", "dress", "clothes", "noun", "n"),
    ("футболка", "t-shirt", "clothes", "noun", "f"),
    ("носки", "socks", "clothes", "noun", "m"),
    ("варежки", "mittens", "clothes", "noun", "f"),

    # ── TIER 15: Animals (15) ──
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

    # ── TIER 16: Nature & weather (10) ──
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

    # ── TIER 17: Colors (16) — base + Russian-specific shades ──
    ("красный", "red", "colors", "adj"),
    ("синий", "blue (deep/dark blue)", "colors", "adj"),
    ("голубой", "light blue (Russian distinguishes from синий!)", "colors", "adj"),
    ("зелёный", "green", "colors", "adj"),
    ("жёлтый", "yellow", "colors", "adj"),
    ("белый", "white", "colors", "adj"),
    ("чёрный", "black", "colors", "adj"),
    ("оранжевый", "orange", "colors", "adj"),
    ("розовый", "pink", "colors", "adj"),
    ("фиолетовый", "purple", "colors", "adj"),
    ("коричневый", "brown", "colors", "adj"),
    ("серый", "gray", "colors", "adj"),
    ("золотой", "gold", "colors", "adj"),
    ("серебряный", "silver", "colors", "adj"),
    ("тёмный", "dark", "colors", "adj"),
    ("светлый", "light (color)", "colors", "adj"),

    # ── TIER 18: Numbers (12) ──
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
]

# ── CONVERSATIONAL LEVEL (~372 words, extends basic) ──────────────
# Order: self-introduction → friendship → classroom → games → expansion.
# Promoted to basic: я, ты, где, что, как, кто.

_CONVERSATIONAL_WORDS = [
    # ── TIER 1: Self-introduction (10) — for meeting Russian classmates ──
    ("как тебя зовут?", "what's your name?", "social", "phrase"),
    ("сколько тебе лет?", "how old are you?", "social", "phrase"),
    ("мне почти шесть", "I'm almost six", "social", "phrase"),
    ("а тебе?", "and you?", "social", "phrase"),
    ("откуда ты?", "where are you from?", "social", "phrase"),
    ("мой папа русский", "my dad is Russian", "social", "phrase"),
    ("моя мама из Таиланда", "my mom is from Thailand", "social", "phrase"),
    ("я говорю по-английски", "I speak English", "social", "phrase"),
    ("я учу русский", "I'm learning Russian", "social", "phrase"),
    ("я ещё плохо говорю", "I don't speak well yet", "social", "phrase"),

    # ── TIER 2: Making friends (9) ──
    ("будем дружить?", "shall we be friends?", "social", "phrase"),
    ("ты моя подруга", "you're my friend", "social", "phrase"),
    ("сядешь со мной?", "will you sit with me?", "social", "phrase"),
    ("можно сесть рядом?", "can I sit next to you?", "social", "phrase"),
    ("это твоё место?", "is this your seat?", "social", "phrase"),
    ("какая твоя любимая игра?", "what's your favorite game?", "social", "phrase"),
    ("какой твой любимый цвет?", "what's your favorite color?", "social", "phrase"),
    ("мне нравится твоё платье", "I like your dress", "social", "phrase"),
    ("мне нравится твой рюкзак", "I like your backpack", "social", "phrase"),

    # ── TIER 3: More everyday phrases (15) ──
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

    # ── TIER 4: Classroom phrases (8) ──
    ("как это называется?", "what's this called?", "school_phrases", "phrase"),
    ("что значит это слово?", "what does this word mean?", "school_phrases", "phrase"),
    ("я не успела", "I didn't have time to finish", "school_phrases", "phrase"),
    ("можно выйти?", "may I leave the room?", "school_phrases", "phrase"),
    ("слушай внимательно", "listen carefully", "school_phrases", "phrase"),
    ("подожди меня", "wait for me", "school_phrases", "phrase"),
    ("повтори, пожалуйста", "please say it again", "school_phrases", "phrase"),
    ("я готова", "I'm ready", "school_phrases", "phrase"),

    # ── TIER 5: Lunch / cafeteria (5) ──
    ("что у тебя на обед?", "what do you have for lunch?", "social", "phrase"),
    ("хочешь попробовать?", "want to try (some)?", "social", "phrase"),
    ("это вкусно?", "is it tasty?", "social", "phrase"),
    ("приятного аппетита", "bon appétit", "phrases", "phrase"),
    ("я не люблю это", "I don't like this", "social", "phrase"),

    # ── TIER 6: Polite forms (4) ──
    ("здравствуйте", "hello (formal/plural)", "phrases", "phrase"),
    ("приятно познакомиться", "nice to meet you", "phrases", "phrase"),
    ("будьте здоровы", "bless you (after sneeze)", "phrases", "phrase"),
    ("на здоровье", "you're welcome (after a meal)", "phrases", "phrase"),

    # ── TIER 7: Family affection (5) — for grandparent calls ──
    ("бабуля", "grandma (affectionate)", "family", "noun", "f"),
    ("дедуля", "grandpa (affectionate)", "family", "noun", "m"),
    ("я тебя люблю", "I love you", "phrases", "phrase"),
    ("я скучаю", "I miss (you)", "phrases", "phrase"),
    ("расскажи сказку", "tell me a story", "phrases", "phrase"),

    # ── TIER 8: More family & people (10) ──
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

    # ── TIER 9: Conflict & kindness (5) ──
    ("не обижайся", "don't be upset", "social", "phrase"),
    ("я тебе помогу", "I'll help you", "social", "phrase"),
    ("спасибо, что помогла", "thanks for helping", "social", "phrase"),
    ("всё хорошо", "it's all fine", "social", "phrase"),
    ("не плачь", "don't cry", "social", "phrase"),

    # ── TIER 10: Games & playground (16) ──
    ("прятки", "hide and seek", "playground", "noun", "f"),
    ("догонялки", "tag (game)", "playground", "noun", "f"),
    ("классики", "hopscotch", "playground", "noun", "m"),
    ("скакалка", "jump rope", "playground", "noun", "f"),
    ("кубики", "blocks (toy)", "playground", "noun", "m"),
    ("кукла", "doll", "playground", "noun", "f"),
    ("пазл", "puzzle", "playground", "noun", "m"),
    ("качели", "swings", "playground", "noun", "f"),
    ("горка", "slide", "playground", "noun", "f"),
    ("песочница", "sandbox", "playground", "noun", "f"),
    ("ты водишь", "you're it (in tag)", "playground", "phrase"),
    ("моя очередь!", "my turn!", "playground", "phrase"),
    ("чур, я первая!", "dibs, I'm first!", "playground", "phrase"),
    ("это нечестно!", "that's not fair!", "playground", "phrase"),
    ("не толкайся", "don't push", "playground", "phrase"),
    ("прости, я нечаянно", "sorry, I didn't mean to", "playground", "phrase"),

    # ── TIER 11: More pronouns / question words (9) ──
    ("он", "he", "pronouns", "pron"),
    ("она", "she", "pronouns", "pron"),
    ("мы", "we", "pronouns", "pron"),
    ("они", "they", "pronouns", "pron"),
    ("когда", "when", "pronouns", "adv"),
    ("почему", "why", "pronouns", "adv"),
    ("сколько", "how much/many", "pronouns", "adv"),
    ("этот", "this", "pronouns", "pron"),
    ("тот", "that", "pronouns", "pron"),

    # ── TIER 12: More verbs (70) ──
    # Existing conv verbs (30)
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
    # Motion (8)
    ("зайти", "to drop in / step into", "verbs", "verb"),
    ("выйти", "to step out / exit", "verbs", "verb"),
    ("вернуться", "to return / come back", "verbs", "verb"),
    ("сесть", "to sit down (perf)", "verbs", "verb"),
    ("лечь", "to lie down (perf)", "verbs", "verb"),
    ("подняться", "to go up", "verbs", "verb"),
    ("спуститься", "to go down", "verbs", "verb"),
    ("остановиться", "to stop", "verbs", "verb"),
    # Communication (8)
    ("объяснить", "to explain", "verbs", "verb"),
    ("крикнуть", "to shout", "verbs", "verb"),
    ("шептать", "to whisper", "verbs", "verb"),
    ("целовать", "to kiss", "verbs", "verb"),
    ("здороваться", "to greet / say hello", "verbs", "verb"),
    ("прощаться", "to say goodbye", "verbs", "verb"),
    ("знакомиться", "to meet someone (get acquainted)", "verbs", "verb"),
    ("мириться", "to make up (after a fight)", "verbs", "verb"),
    # Cognitive (6)
    ("вспомнить", "to recall / remember", "verbs", "verb"),
    ("решать", "to solve", "verbs", "verb"),
    ("проверять", "to check", "verbs", "verb"),
    ("стараться", "to try hard", "verbs", "verb"),
    ("успеть", "to make it in time", "verbs", "verb"),
    ("выучить", "to learn (perf)", "verbs", "verb"),
    # Making / handling (5)
    ("строить", "to build", "verbs", "verb"),
    ("сломать", "to break", "verbs", "verb"),
    ("резать", "to cut", "verbs", "verb"),
    ("клеить", "to glue", "verbs", "verb"),
    ("собирать", "to assemble / gather", "verbs", "verb"),
    # Giving / getting (4)
    ("получить", "to receive", "verbs", "verb"),
    ("подарить", "to give as a gift", "verbs", "verb"),
    ("забрать", "to pick up / take away", "verbs", "verb"),
    ("оставить", "to leave behind", "verbs", "verb"),
    # Emotions (7)
    ("бояться", "to be afraid", "verbs", "verb"),
    ("радоваться", "to be glad", "verbs", "verb"),
    ("грустить", "to be sad", "verbs", "verb"),
    ("сердиться", "to be angry", "verbs", "verb"),
    ("удивляться", "to be surprised", "verbs", "verb"),
    ("обижаться", "to take offense", "verbs", "verb"),
    ("скучать", "to miss / be bored", "verbs", "verb"),
    # Sensory / care (2)
    ("чувствовать", "to feel", "verbs", "verb"),
    ("лечить", "to treat (medically)", "verbs", "verb"),

    # ── TIER 13: More adjectives (50) ──
    # Existing conv adj (20)
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
    # NEW conv adj — sensory (3)
    ("горький", "bitter", "adjectives", "adj"),
    ("острый", "spicy / sharp", "adjectives", "adj"),
    ("свежий", "fresh", "adjectives", "adj"),
    # Shape & dimension (4)
    ("квадратный", "square", "adjectives", "adj"),
    ("широкий", "wide", "adjectives", "adj"),
    ("узкий", "narrow", "adjectives", "adj"),
    ("глубокий", "deep", "adjectives", "adj"),
    # Personality / character (13)
    ("ленивый", "lazy", "adjectives", "adj"),
    ("любопытный", "curious", "adjectives", "adj"),
    ("честный", "honest", "adjectives", "adj"),
    ("вежливый", "polite", "adjectives", "adj"),
    ("послушный", "well-behaved", "adjectives", "adj"),
    ("упрямый", "stubborn", "adjectives", "adj"),
    ("трудолюбивый", "hardworking", "adjectives", "adj"),
    ("терпеливый", "patient", "adjectives", "adj"),
    ("щедрый", "generous", "adjectives", "adj"),
    ("жадный", "greedy", "adjectives", "adj"),
    ("внимательный", "attentive", "adjectives", "adj"),
    ("спокойный", "calm", "adjectives", "adj"),
    ("шумный", "noisy", "adjectives", "adj"),
    # Quality / state (10)
    ("интересный", "interesting", "adjectives", "adj"),
    ("скучный", "boring", "adjectives", "adj"),
    ("трудный", "difficult", "adjectives", "adj"),
    ("простой", "simple", "adjectives", "adj"),
    ("сложный", "complicated", "adjectives", "adj"),
    ("свободный", "free / available", "adjectives", "adj"),
    ("занятый", "busy", "adjectives", "adj"),
    ("одинаковый", "same / identical", "adjectives", "adj"),
    ("разный", "different", "adjectives", "adj"),
    ("настоящий", "real / genuine", "adjectives", "adj"),

    # ── TIER 14: Places (15) ──
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

    # ── TIER 15: Transport (8) ──
    ("машина", "car", "transport", "noun", "f"),
    ("автобус", "bus", "transport", "noun", "m"),
    ("поезд", "train", "transport", "noun", "m"),
    ("самолёт", "airplane", "transport", "noun", "m"),
    ("велосипед", "bicycle", "transport", "noun", "m"),
    ("корабль", "ship", "transport", "noun", "m"),
    ("метро", "metro/subway", "transport", "noun", "n"),
    ("такси", "taxi", "transport", "noun", "n"),

    # ── TIER 16: More home & objects (12) ──
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

    # ── TIER 17: More clothes (8) ──
    ("пальто", "coat", "clothes", "noun", "n"),
    ("рубашка", "shirt", "clothes", "noun", "f"),
    ("юбка", "skirt", "clothes", "noun", "f"),
    ("шарф", "scarf", "clothes", "noun", "m"),
    ("перчатки", "gloves", "clothes", "noun", "f"),
    ("очки", "glasses", "clothes", "noun", "m"),
    ("сумка", "bag", "clothes", "noun", "f"),
    ("зонт", "umbrella", "clothes", "noun", "m"),

    # ── TIER 18: More body (6) ──
    ("волосы", "hair", "body", "noun", "m"),
    ("лицо", "face", "body", "noun", "n"),
    ("шея", "neck", "body", "noun", "f"),
    ("плечо", "shoulder", "body", "noun", "n"),
    ("колено", "knee", "body", "noun", "n"),
    ("кожа", "skin", "body", "noun", "f"),

    # ── TIER 19: More animals (12) ──
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

    # ── TIER 20: More food (14) ──
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

    # ── TIER 21: More nature (10) ──
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

    # ── TIER 22: Time / daily life (12) ──
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

    # ── TIER 23: Days, months, seasons (12) ──
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

    # ── TIER 24: Emotions & states (12) ──
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

    # ── TIER 25: More school (12) ──
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

    # ── TIER 26: More numbers (8) ──
    ("двадцать", "twenty", "numbers", "num"),
    ("тридцать", "thirty", "numbers", "num"),
    ("сорок", "forty", "numbers", "num"),
    ("пятьдесят", "fifty", "numbers", "num"),
    ("первый", "first", "numbers", "adj"),
    ("второй", "second", "numbers", "adj"),
    ("третий", "third", "numbers", "adj"),
    ("последний", "last", "numbers", "adj"),

    # ── TIER 27: Prepositions & connectors (15) ──
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
    """Get words for a given level, ordered by importance.

    'basic' returns ~283 starter words. The first ~100 are the daily-survival
    set: greetings, foundational grammar, needs/feelings, school survival,
    and adult-to-kid commands. Topical vocabulary (animals, food, etc.) follows.

    'conversational' returns ~372 additional words: self-introduction,
    friendship, longer classroom phrases, polite forms, games, and a richer
    vocabulary of verbs and adjectives.

    'all' returns all ~655 words (basic + conversational).
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
