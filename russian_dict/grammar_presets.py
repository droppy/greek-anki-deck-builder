"""Hand-written content for grammar concept cards.

These cards explain foundational Russian grammar (gender, adjective agreement,
verb conjugation, plurals) for an English-speaking child. They are pre-filled
rather than API-generated because grammar explanations need to be precise and
the SVG diagrams need to communicate the pattern clearly.

Keys must match RussianWord.key (lowercase, stripped) for the entries in
vocabulary.py with pos="grammar".

The generator skips API calls for any word with pos="grammar" and writes the
preset directly to the cache.
"""

# Color palette used across grammar SVGs (consistent gender coding):
#   Masculine (он):  #1565C0 (deep blue)   bg #BBDEFB
#   Feminine  (она): #C2185B (pink)         bg #F8BBD0
#   Neuter    (оно): #F57F17 (amber)        bg #FFF59D
#   Plural    (они): #2E7D32 (green)        bg #C8E6C9


_C1 = """<svg viewBox='0 0 400 280' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='280' fill='#FAFAFA'/>
  <text x='200' y='30' text-anchor='middle' font-size='20' font-weight='bold' fill='#333'>Every Russian noun is HE, SHE, or IT</text>
  <rect x='20' y='55' width='110' height='200' rx='12' fill='#BBDEFB' stroke='#1565C0' stroke-width='3'/>
  <text x='75' y='85' text-anchor='middle' font-size='28' font-weight='bold' fill='#0D47A1'>ОН</text>
  <text x='75' y='95' text-anchor='middle' font-size='12' fill='#0D47A1'>(he)</text>
  <text x='75' y='160' text-anchor='middle' font-size='60'>👦</text>
  <text x='75' y='220' text-anchor='middle' font-size='20' font-weight='bold' fill='#0D47A1'>стол</text>
  <text x='75' y='243' text-anchor='middle' font-size='13' fill='#0D47A1'>(table)</text>
  <rect x='145' y='55' width='110' height='200' rx='12' fill='#F8BBD0' stroke='#C2185B' stroke-width='3'/>
  <text x='200' y='85' text-anchor='middle' font-size='28' font-weight='bold' fill='#880E4F'>ОНА</text>
  <text x='200' y='95' text-anchor='middle' font-size='12' fill='#880E4F'>(she)</text>
  <text x='200' y='160' text-anchor='middle' font-size='60'>👩</text>
  <text x='200' y='220' text-anchor='middle' font-size='20' font-weight='bold' fill='#880E4F'>мама</text>
  <text x='200' y='243' text-anchor='middle' font-size='13' fill='#880E4F'>(mom)</text>
  <rect x='270' y='55' width='110' height='200' rx='12' fill='#FFF59D' stroke='#F57F17' stroke-width='3'/>
  <text x='325' y='85' text-anchor='middle' font-size='28' font-weight='bold' fill='#E65100'>ОНО</text>
  <text x='325' y='95' text-anchor='middle' font-size='12' fill='#E65100'>(it)</text>
  <text x='325' y='160' text-anchor='middle' font-size='60'>🌟</text>
  <text x='325' y='220' text-anchor='middle' font-size='20' font-weight='bold' fill='#E65100'>окно</text>
  <text x='325' y='243' text-anchor='middle' font-size='13' fill='#E65100'>(window)</text>
</svg>"""

_C2 = """<svg viewBox='0 0 400 280' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='280' fill='#FAFAFA'/>
  <text x='200' y='28' text-anchor='middle' font-size='18' font-weight='bold' fill='#333'>Look at the LAST LETTER</text>
  <rect x='20' y='50' width='110' height='210' rx='12' fill='#BBDEFB' stroke='#1565C0' stroke-width='3'/>
  <text x='75' y='80' text-anchor='middle' font-size='22' font-weight='bold' fill='#0D47A1'>МУЖ</text>
  <text x='75' y='98' text-anchor='middle' font-size='12' fill='#0D47A1'>(masculine)</text>
  <text x='75' y='140' text-anchor='middle' font-size='42' font-weight='bold' fill='#0D47A1'>-▢</text>
  <text x='75' y='170' text-anchor='middle' font-size='11' fill='#0D47A1'>ends in consonant</text>
  <text x='75' y='205' text-anchor='middle' font-size='17' font-weight='bold' fill='#0D47A1'>сто<tspan fill='#D32F2F'>л</tspan></text>
  <text x='75' y='230' text-anchor='middle' font-size='17' font-weight='bold' fill='#0D47A1'>дом, кот</text>
  <rect x='145' y='50' width='110' height='210' rx='12' fill='#F8BBD0' stroke='#C2185B' stroke-width='3'/>
  <text x='200' y='80' text-anchor='middle' font-size='22' font-weight='bold' fill='#880E4F'>ЖЕН</text>
  <text x='200' y='98' text-anchor='middle' font-size='12' fill='#880E4F'>(feminine)</text>
  <text x='200' y='140' text-anchor='middle' font-size='42' font-weight='bold' fill='#880E4F'>-а / -я</text>
  <text x='200' y='170' text-anchor='middle' font-size='11' fill='#880E4F'>ends in -а or -я</text>
  <text x='200' y='205' text-anchor='middle' font-size='17' font-weight='bold' fill='#880E4F'>мам<tspan fill='#D32F2F'>а</tspan></text>
  <text x='200' y='230' text-anchor='middle' font-size='17' font-weight='bold' fill='#880E4F'>книга, рука</text>
  <rect x='270' y='50' width='110' height='210' rx='12' fill='#FFF59D' stroke='#F57F17' stroke-width='3'/>
  <text x='325' y='80' text-anchor='middle' font-size='22' font-weight='bold' fill='#E65100'>СРЕД</text>
  <text x='325' y='98' text-anchor='middle' font-size='12' fill='#E65100'>(neuter)</text>
  <text x='325' y='140' text-anchor='middle' font-size='42' font-weight='bold' fill='#E65100'>-о / -е</text>
  <text x='325' y='170' text-anchor='middle' font-size='11' fill='#E65100'>ends in -о or -е</text>
  <text x='325' y='205' text-anchor='middle' font-size='17' font-weight='bold' fill='#E65100'>окн<tspan fill='#D32F2F'>о</tspan></text>
  <text x='325' y='230' text-anchor='middle' font-size='17' font-weight='bold' fill='#E65100'>море, яйцо</text>
</svg>"""

_C3 = """<svg viewBox='0 0 400 280' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='280' fill='#FAFAFA'/>
  <text x='200' y='28' text-anchor='middle' font-size='18' font-weight='bold' fill='#333'>BIG dresses up to match the noun</text>
  <rect x='15' y='50' width='90' height='210' rx='10' fill='#BBDEFB' stroke='#1565C0' stroke-width='2'/>
  <text x='60' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#0D47A1'>ОН</text>
  <text x='60' y='128' text-anchor='middle' font-size='42'>🏠</text>
  <text x='60' y='170' text-anchor='middle' font-size='15' font-weight='bold' fill='#0D47A1'>больш<tspan fill='#D32F2F'>ой</tspan></text>
  <text x='60' y='195' text-anchor='middle' font-size='13' fill='#0D47A1'>дом</text>
  <text x='60' y='235' text-anchor='middle' font-size='10' fill='#0D47A1'>(big house)</text>
  <rect x='112' y='50' width='90' height='210' rx='10' fill='#F8BBD0' stroke='#C2185B' stroke-width='2'/>
  <text x='157' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#880E4F'>ОНА</text>
  <text x='157' y='128' text-anchor='middle' font-size='42'>🐕</text>
  <text x='157' y='170' text-anchor='middle' font-size='15' font-weight='bold' fill='#880E4F'>больш<tspan fill='#D32F2F'>ая</tspan></text>
  <text x='157' y='195' text-anchor='middle' font-size='13' fill='#880E4F'>собака</text>
  <text x='157' y='235' text-anchor='middle' font-size='10' fill='#880E4F'>(big dog)</text>
  <rect x='209' y='50' width='90' height='210' rx='10' fill='#FFF59D' stroke='#F57F17' stroke-width='2'/>
  <text x='254' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#E65100'>ОНО</text>
  <text x='254' y='128' text-anchor='middle' font-size='42'>🪟</text>
  <text x='254' y='170' text-anchor='middle' font-size='15' font-weight='bold' fill='#E65100'>больш<tspan fill='#D32F2F'>ое</tspan></text>
  <text x='254' y='195' text-anchor='middle' font-size='13' fill='#E65100'>окно</text>
  <text x='254' y='235' text-anchor='middle' font-size='10' fill='#E65100'>(big window)</text>
  <rect x='306' y='50' width='90' height='210' rx='10' fill='#C8E6C9' stroke='#2E7D32' stroke-width='2'/>
  <text x='351' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#1B5E20'>ОНИ</text>
  <text x='351' y='128' text-anchor='middle' font-size='42'>👫</text>
  <text x='351' y='170' text-anchor='middle' font-size='15' font-weight='bold' fill='#1B5E20'>больш<tspan fill='#D32F2F'>ие</tspan></text>
  <text x='351' y='195' text-anchor='middle' font-size='13' fill='#1B5E20'>друзья</text>
  <text x='351' y='235' text-anchor='middle' font-size='10' fill='#1B5E20'>(big friends)</text>
</svg>"""

_C4 = """<svg viewBox='0 0 400 280' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='280' fill='#FAFAFA'/>
  <text x='200' y='28' text-anchor='middle' font-size='18' font-weight='bold' fill='#333'>RED — same idea, watch the -ый!</text>
  <rect x='15' y='50' width='90' height='210' rx='10' fill='#BBDEFB' stroke='#1565C0' stroke-width='2'/>
  <text x='60' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#0D47A1'>ОН</text>
  <circle cx='60' cy='130' r='28' fill='#E53935'/>
  <text x='60' y='175' text-anchor='middle' font-size='15' font-weight='bold' fill='#0D47A1'>красн<tspan fill='#D32F2F'>ый</tspan></text>
  <text x='60' y='198' text-anchor='middle' font-size='13' fill='#0D47A1'>мяч</text>
  <text x='60' y='235' text-anchor='middle' font-size='10' fill='#0D47A1'>(red ball)</text>
  <rect x='112' y='50' width='90' height='210' rx='10' fill='#F8BBD0' stroke='#C2185B' stroke-width='2'/>
  <text x='157' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#880E4F'>ОНА</text>
  <rect x='130' y='110' width='54' height='40' rx='6' fill='#E53935'/>
  <circle cx='140' cy='155' r='5' fill='#222'/>
  <circle cx='174' cy='155' r='5' fill='#222'/>
  <text x='157' y='175' text-anchor='middle' font-size='15' font-weight='bold' fill='#880E4F'>красн<tspan fill='#D32F2F'>ая</tspan></text>
  <text x='157' y='198' text-anchor='middle' font-size='13' fill='#880E4F'>машина</text>
  <text x='157' y='235' text-anchor='middle' font-size='10' fill='#880E4F'>(red car)</text>
  <rect x='209' y='50' width='90' height='210' rx='10' fill='#FFF59D' stroke='#F57F17' stroke-width='2'/>
  <text x='254' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#E65100'>ОНО</text>
  <ellipse cx='254' cy='130' rx='22' ry='26' fill='#E53935'/>
  <path d='M 252 105 Q 256 95 263 100' stroke='#5D4037' stroke-width='3' fill='none'/>
  <text x='254' y='175' text-anchor='middle' font-size='15' font-weight='bold' fill='#E65100'>красн<tspan fill='#D32F2F'>ое</tspan></text>
  <text x='254' y='198' text-anchor='middle' font-size='13' fill='#E65100'>яблоко</text>
  <text x='254' y='235' text-anchor='middle' font-size='10' fill='#E65100'>(red apple)</text>
  <rect x='306' y='50' width='90' height='210' rx='10' fill='#C8E6C9' stroke='#2E7D32' stroke-width='2'/>
  <text x='351' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#1B5E20'>ОНИ</text>
  <text x='335' y='140' font-size='28'>🌹</text>
  <text x='355' y='140' font-size='28'>🌹</text>
  <text x='351' y='175' text-anchor='middle' font-size='15' font-weight='bold' fill='#1B5E20'>красн<tspan fill='#D32F2F'>ые</tspan></text>
  <text x='351' y='198' text-anchor='middle' font-size='13' fill='#1B5E20'>цветы</text>
  <text x='351' y='235' text-anchor='middle' font-size='10' fill='#1B5E20'>(red flowers)</text>
</svg>"""

_C5 = """<svg viewBox='0 0 400 280' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='280' fill='#FAFAFA'/>
  <text x='200' y='28' text-anchor='middle' font-size='17' font-weight='bold' fill='#333'>GOOD — after ш/ж/ч/щ, write И not Ы</text>
  <rect x='15' y='50' width='90' height='210' rx='10' fill='#BBDEFB' stroke='#1565C0' stroke-width='2'/>
  <text x='60' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#0D47A1'>ОН</text>
  <text x='60' y='130' text-anchor='middle' font-size='42'>👨</text>
  <text x='60' y='170' text-anchor='middle' font-size='14' font-weight='bold' fill='#0D47A1'>хорош<tspan fill='#D32F2F'>ий</tspan></text>
  <text x='60' y='195' text-anchor='middle' font-size='13' fill='#0D47A1'>папа</text>
  <text x='60' y='235' text-anchor='middle' font-size='10' fill='#0D47A1'>(good dad)</text>
  <rect x='112' y='50' width='90' height='210' rx='10' fill='#F8BBD0' stroke='#C2185B' stroke-width='2'/>
  <text x='157' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#880E4F'>ОНА</text>
  <text x='157' y='130' text-anchor='middle' font-size='42'>👩</text>
  <text x='157' y='170' text-anchor='middle' font-size='14' font-weight='bold' fill='#880E4F'>хорош<tspan fill='#D32F2F'>ая</tspan></text>
  <text x='157' y='195' text-anchor='middle' font-size='13' fill='#880E4F'>мама</text>
  <text x='157' y='235' text-anchor='middle' font-size='10' fill='#880E4F'>(good mom)</text>
  <rect x='209' y='50' width='90' height='210' rx='10' fill='#FFF59D' stroke='#F57F17' stroke-width='2'/>
  <text x='254' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#E65100'>ОНО</text>
  <text x='254' y='130' text-anchor='middle' font-size='42'>🌅</text>
  <text x='254' y='170' text-anchor='middle' font-size='14' font-weight='bold' fill='#E65100'>хорош<tspan fill='#D32F2F'>ее</tspan></text>
  <text x='254' y='195' text-anchor='middle' font-size='13' fill='#E65100'>утро</text>
  <text x='254' y='235' text-anchor='middle' font-size='10' fill='#E65100'>(good morning)</text>
  <rect x='306' y='50' width='90' height='210' rx='10' fill='#C8E6C9' stroke='#2E7D32' stroke-width='2'/>
  <text x='351' y='78' text-anchor='middle' font-size='14' font-weight='bold' fill='#1B5E20'>ОНИ</text>
  <text x='351' y='130' text-anchor='middle' font-size='42'>👨‍👩‍👧</text>
  <text x='351' y='170' text-anchor='middle' font-size='14' font-weight='bold' fill='#1B5E20'>хорош<tspan fill='#D32F2F'>ие</tspan></text>
  <text x='351' y='195' text-anchor='middle' font-size='13' fill='#1B5E20'>дети</text>
  <text x='351' y='235' text-anchor='middle' font-size='10' fill='#1B5E20'>(good kids)</text>
</svg>"""

_C6 = """<svg viewBox='0 0 400 280' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='280' fill='#FAFAFA'/>
  <text x='200' y='28' text-anchor='middle' font-size='18' font-weight='bold' fill='#333'>MY — also dresses up for its noun</text>
  <text x='200' y='48' text-anchor='middle' font-size='28'>💖</text>
  <rect x='15' y='65' width='90' height='195' rx='10' fill='#BBDEFB' stroke='#1565C0' stroke-width='2'/>
  <text x='60' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#0D47A1'>ОН</text>
  <text x='60' y='150' text-anchor='middle' font-size='38' font-weight='bold' fill='#1565C0'>м<tspan fill='#D32F2F'>ой</tspan></text>
  <text x='60' y='195' text-anchor='middle' font-size='13' fill='#0D47A1'>мой папа</text>
  <text x='60' y='225' text-anchor='middle' font-size='11' fill='#0D47A1'>(my dad)</text>
  <rect x='112' y='65' width='90' height='195' rx='10' fill='#F8BBD0' stroke='#C2185B' stroke-width='2'/>
  <text x='157' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#880E4F'>ОНА</text>
  <text x='157' y='150' text-anchor='middle' font-size='38' font-weight='bold' fill='#C2185B'>м<tspan fill='#D32F2F'>оя</tspan></text>
  <text x='157' y='195' text-anchor='middle' font-size='13' fill='#880E4F'>моя мама</text>
  <text x='157' y='225' text-anchor='middle' font-size='11' fill='#880E4F'>(my mom)</text>
  <rect x='209' y='65' width='90' height='195' rx='10' fill='#FFF59D' stroke='#F57F17' stroke-width='2'/>
  <text x='254' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#E65100'>ОНО</text>
  <text x='254' y='150' text-anchor='middle' font-size='38' font-weight='bold' fill='#F57F17'>м<tspan fill='#D32F2F'>оё</tspan></text>
  <text x='254' y='195' text-anchor='middle' font-size='13' fill='#E65100'>моё имя</text>
  <text x='254' y='225' text-anchor='middle' font-size='11' fill='#E65100'>(my name)</text>
  <rect x='306' y='65' width='90' height='195' rx='10' fill='#C8E6C9' stroke='#2E7D32' stroke-width='2'/>
  <text x='351' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#1B5E20'>ОНИ</text>
  <text x='351' y='150' text-anchor='middle' font-size='38' font-weight='bold' fill='#2E7D32'>м<tspan fill='#D32F2F'>ои</tspan></text>
  <text x='351' y='195' text-anchor='middle' font-size='13' fill='#1B5E20'>мои друзья</text>
  <text x='351' y='225' text-anchor='middle' font-size='11' fill='#1B5E20'>(my friends)</text>
</svg>"""

_C7 = """<svg viewBox='0 0 400 280' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='280' fill='#FAFAFA'/>
  <text x='200' y='28' text-anchor='middle' font-size='18' font-weight='bold' fill='#333'>YOUR — same 4 endings as МОЙ</text>
  <text x='200' y='52' text-anchor='middle' font-size='14' fill='#666'>swap М→Т: мой→твой, моя→твоя...</text>
  <rect x='15' y='65' width='90' height='195' rx='10' fill='#BBDEFB' stroke='#1565C0' stroke-width='2'/>
  <text x='60' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#0D47A1'>ОН</text>
  <text x='60' y='150' text-anchor='middle' font-size='38' font-weight='bold' fill='#1565C0'>тв<tspan fill='#D32F2F'>ой</tspan></text>
  <text x='60' y='195' text-anchor='middle' font-size='13' fill='#0D47A1'>твой брат</text>
  <text x='60' y='225' text-anchor='middle' font-size='11' fill='#0D47A1'>(your brother)</text>
  <rect x='112' y='65' width='90' height='195' rx='10' fill='#F8BBD0' stroke='#C2185B' stroke-width='2'/>
  <text x='157' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#880E4F'>ОНА</text>
  <text x='157' y='150' text-anchor='middle' font-size='38' font-weight='bold' fill='#C2185B'>тв<tspan fill='#D32F2F'>оя</tspan></text>
  <text x='157' y='195' text-anchor='middle' font-size='13' fill='#880E4F'>твоя книга</text>
  <text x='157' y='225' text-anchor='middle' font-size='11' fill='#880E4F'>(your book)</text>
  <rect x='209' y='65' width='90' height='195' rx='10' fill='#FFF59D' stroke='#F57F17' stroke-width='2'/>
  <text x='254' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#E65100'>ОНО</text>
  <text x='254' y='150' text-anchor='middle' font-size='38' font-weight='bold' fill='#F57F17'>тв<tspan fill='#D32F2F'>оё</tspan></text>
  <text x='254' y='195' text-anchor='middle' font-size='13' fill='#E65100'>твоё место</text>
  <text x='254' y='225' text-anchor='middle' font-size='11' fill='#E65100'>(your seat)</text>
  <rect x='306' y='65' width='90' height='195' rx='10' fill='#C8E6C9' stroke='#2E7D32' stroke-width='2'/>
  <text x='351' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#1B5E20'>ОНИ</text>
  <text x='351' y='150' text-anchor='middle' font-size='38' font-weight='bold' fill='#2E7D32'>тв<tspan fill='#D32F2F'>ои</tspan></text>
  <text x='351' y='195' text-anchor='middle' font-size='13' fill='#1B5E20'>твои родители</text>
  <text x='351' y='225' text-anchor='middle' font-size='11' fill='#1B5E20'>(your parents)</text>
</svg>"""

_C8 = """<svg viewBox='0 0 400 280' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='280' fill='#FAFAFA'/>
  <text x='200' y='28' text-anchor='middle' font-size='18' font-weight='bold' fill='#333'>THIS — pointing changes by gender too</text>
  <text x='200' y='50' text-anchor='middle' font-size='24'>👉</text>
  <rect x='15' y='65' width='90' height='195' rx='10' fill='#BBDEFB' stroke='#1565C0' stroke-width='2'/>
  <text x='60' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#0D47A1'>ОН</text>
  <text x='60' y='150' text-anchor='middle' font-size='34' font-weight='bold' fill='#1565C0'>эт<tspan fill='#D32F2F'>от</tspan></text>
  <text x='60' y='195' text-anchor='middle' font-size='13' fill='#0D47A1'>этот стул</text>
  <text x='60' y='225' text-anchor='middle' font-size='11' fill='#0D47A1'>(this chair)</text>
  <rect x='112' y='65' width='90' height='195' rx='10' fill='#F8BBD0' stroke='#C2185B' stroke-width='2'/>
  <text x='157' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#880E4F'>ОНА</text>
  <text x='157' y='150' text-anchor='middle' font-size='34' font-weight='bold' fill='#C2185B'>эт<tspan fill='#D32F2F'>а</tspan></text>
  <text x='157' y='195' text-anchor='middle' font-size='13' fill='#880E4F'>эта парта</text>
  <text x='157' y='225' text-anchor='middle' font-size='11' fill='#880E4F'>(this desk)</text>
  <rect x='209' y='65' width='90' height='195' rx='10' fill='#FFF59D' stroke='#F57F17' stroke-width='2'/>
  <text x='254' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#E65100'>ОНО</text>
  <text x='254' y='150' text-anchor='middle' font-size='34' font-weight='bold' fill='#F57F17'>эт<tspan fill='#D32F2F'>о</tspan></text>
  <text x='254' y='195' text-anchor='middle' font-size='13' fill='#E65100'>это место</text>
  <text x='254' y='225' text-anchor='middle' font-size='11' fill='#E65100'>(this seat)</text>
  <rect x='306' y='65' width='90' height='195' rx='10' fill='#C8E6C9' stroke='#2E7D32' stroke-width='2'/>
  <text x='351' y='90' text-anchor='middle' font-size='14' font-weight='bold' fill='#1B5E20'>ОНИ</text>
  <text x='351' y='150' text-anchor='middle' font-size='34' font-weight='bold' fill='#2E7D32'>эт<tspan fill='#D32F2F'>и</tspan></text>
  <text x='351' y='195' text-anchor='middle' font-size='13' fill='#1B5E20'>эти карандаши</text>
  <text x='351' y='225' text-anchor='middle' font-size='11' fill='#1B5E20'>(these pencils)</text>
</svg>"""

_C9 = """<svg viewBox='0 0 400 320' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='320' fill='#FAFAFA'/>
  <text x='200' y='25' text-anchor='middle' font-size='18' font-weight='bold' fill='#333'>хотеть — verb changes by WHO wants</text>
  <text x='200' y='45' text-anchor='middle' font-size='13' fill='#666'>One verb, six different endings</text>
  <rect x='15' y='60' width='115' height='75' rx='8' fill='#E3F2FD' stroke='#1976D2' stroke-width='2'/>
  <text x='30' y='95' font-size='15' font-weight='bold' fill='#0D47A1'>я</text>
  <text x='72' y='95' font-size='17' font-weight='bold' fill='#D32F2F'>хочу</text>
  <text x='72' y='120' text-anchor='middle' font-size='10' fill='#0D47A1'>(I want)</text>
  <rect x='142' y='60' width='115' height='75' rx='8' fill='#FCE4EC' stroke='#C2185B' stroke-width='2'/>
  <text x='157' y='95' font-size='15' font-weight='bold' fill='#880E4F'>ты</text>
  <text x='205' y='95' font-size='17' font-weight='bold' fill='#D32F2F'>хочешь</text>
  <text x='199' y='120' text-anchor='middle' font-size='10' fill='#880E4F'>(you want)</text>
  <rect x='269' y='60' width='115' height='75' rx='8' fill='#FFF8E1' stroke='#F57F17' stroke-width='2'/>
  <text x='284' y='95' font-size='15' font-weight='bold' fill='#E65100'>он/она</text>
  <text x='340' y='95' font-size='17' font-weight='bold' fill='#D32F2F'>хочет</text>
  <text x='326' y='120' text-anchor='middle' font-size='10' fill='#E65100'>(he/she wants)</text>
  <rect x='15' y='150' width='115' height='75' rx='8' fill='#E8F5E9' stroke='#388E3C' stroke-width='2'/>
  <text x='30' y='185' font-size='15' font-weight='bold' fill='#1B5E20'>мы</text>
  <text x='80' y='185' font-size='17' font-weight='bold' fill='#D32F2F'>хотим</text>
  <text x='72' y='210' text-anchor='middle' font-size='10' fill='#1B5E20'>(we want)</text>
  <rect x='142' y='150' width='115' height='75' rx='8' fill='#F3E5F5' stroke='#7B1FA2' stroke-width='2'/>
  <text x='157' y='185' font-size='15' font-weight='bold' fill='#4A148C'>вы</text>
  <text x='200' y='185' font-size='17' font-weight='bold' fill='#D32F2F'>хотите</text>
  <text x='199' y='210' text-anchor='middle' font-size='10' fill='#4A148C'>(you all want)</text>
  <rect x='269' y='150' width='115' height='75' rx='8' fill='#FFEBEE' stroke='#D32F2F' stroke-width='2'/>
  <text x='284' y='185' font-size='15' font-weight='bold' fill='#B71C1C'>они</text>
  <text x='335' y='185' font-size='17' font-weight='bold' fill='#D32F2F'>хотят</text>
  <text x='326' y='210' text-anchor='middle' font-size='10' fill='#B71C1C'>(they want)</text>
  <text x='200' y='260' text-anchor='middle' font-size='14' fill='#333'>Example: <tspan font-weight='bold'>Я хочу пить.</tspan></text>
  <text x='200' y='282' text-anchor='middle' font-size='13' fill='#666'>I want a drink.</text>
  <text x='200' y='305' text-anchor='middle' font-size='12' fill='#666' font-style='italic'>Memorize like a song: я-ты-он-мы-вы-они</text>
</svg>"""

_C10 = """<svg viewBox='0 0 400 320' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='320' fill='#FAFAFA'/>
  <text x='200' y='25' text-anchor='middle' font-size='18' font-weight='bold' fill='#333'>есть (to eat) — same idea</text>
  <text x='200' y='45' text-anchor='middle' font-size='13' fill='#666'>Six endings — practice with food!</text>
  <rect x='15' y='60' width='115' height='75' rx='8' fill='#E3F2FD' stroke='#1976D2' stroke-width='2'/>
  <text x='30' y='95' font-size='15' font-weight='bold' fill='#0D47A1'>я</text>
  <text x='80' y='95' font-size='18' font-weight='bold' fill='#D32F2F'>ем</text>
  <text x='110' y='100' font-size='22'>🍎</text>
  <text x='72' y='120' text-anchor='middle' font-size='10' fill='#0D47A1'>(I eat)</text>
  <rect x='142' y='60' width='115' height='75' rx='8' fill='#FCE4EC' stroke='#C2185B' stroke-width='2'/>
  <text x='157' y='95' font-size='15' font-weight='bold' fill='#880E4F'>ты</text>
  <text x='200' y='95' font-size='18' font-weight='bold' fill='#D32F2F'>ешь</text>
  <text x='235' y='100' font-size='22'>🍌</text>
  <text x='199' y='120' text-anchor='middle' font-size='10' fill='#880E4F'>(you eat)</text>
  <rect x='269' y='60' width='115' height='75' rx='8' fill='#FFF8E1' stroke='#F57F17' stroke-width='2'/>
  <text x='284' y='95' font-size='15' font-weight='bold' fill='#E65100'>он/она</text>
  <text x='338' y='95' font-size='18' font-weight='bold' fill='#D32F2F'>ест</text>
  <text x='365' y='100' font-size='22'>🍞</text>
  <text x='326' y='120' text-anchor='middle' font-size='10' fill='#E65100'>(he/she eats)</text>
  <rect x='15' y='150' width='115' height='75' rx='8' fill='#E8F5E9' stroke='#388E3C' stroke-width='2'/>
  <text x='30' y='185' font-size='15' font-weight='bold' fill='#1B5E20'>мы</text>
  <text x='80' y='185' font-size='18' font-weight='bold' fill='#D32F2F'>едим</text>
  <text x='115' y='190' font-size='22'>🍕</text>
  <text x='72' y='210' text-anchor='middle' font-size='10' fill='#1B5E20'>(we eat)</text>
  <rect x='142' y='150' width='115' height='75' rx='8' fill='#F3E5F5' stroke='#7B1FA2' stroke-width='2'/>
  <text x='157' y='185' font-size='15' font-weight='bold' fill='#4A148C'>вы</text>
  <text x='200' y='185' font-size='18' font-weight='bold' fill='#D32F2F'>едите</text>
  <text x='245' y='190' font-size='22'>🥕</text>
  <text x='199' y='210' text-anchor='middle' font-size='10' fill='#4A148C'>(you all eat)</text>
  <rect x='269' y='150' width='115' height='75' rx='8' fill='#FFEBEE' stroke='#D32F2F' stroke-width='2'/>
  <text x='284' y='185' font-size='15' font-weight='bold' fill='#B71C1C'>они</text>
  <text x='335' y='185' font-size='18' font-weight='bold' fill='#D32F2F'>едят</text>
  <text x='370' y='190' font-size='22'>🍰</text>
  <text x='326' y='210' text-anchor='middle' font-size='10' fill='#B71C1C'>(they eat)</text>
  <text x='200' y='260' text-anchor='middle' font-size='14' fill='#333'>Example: <tspan font-weight='bold'>Я ем кашу.</tspan></text>
  <text x='200' y='282' text-anchor='middle' font-size='13' fill='#666'>I eat porridge.</text>
  <text x='200' y='305' text-anchor='middle' font-size='12' fill='#666' font-style='italic'>Most verbs: -у/-ю, -ешь, -ет, -ем, -ете, -ут/-ют</text>
</svg>"""

_C11 = """<svg viewBox='0 0 400 280' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='280' fill='#FAFAFA'/>
  <text x='200' y='28' text-anchor='middle' font-size='18' font-weight='bold' fill='#333'>Past tense knows YOUR gender!</text>
  <text x='200' y='50' text-anchor='middle' font-size='13' fill='#666'>Boys say -л · Girls say -ла</text>
  <rect x='30' y='75' width='160' height='180' rx='14' fill='#BBDEFB' stroke='#1565C0' stroke-width='3'/>
  <text x='110' y='115' text-anchor='middle' font-size='70'>👦</text>
  <text x='110' y='160' text-anchor='middle' font-size='15' font-weight='bold' fill='#0D47A1'>Boy says:</text>
  <rect x='45' y='175' width='130' height='50' rx='10' fill='white' stroke='#1565C0' stroke-width='2'/>
  <text x='110' y='208' text-anchor='middle' font-size='22' font-weight='bold' fill='#0D47A1'>я сказа<tspan fill='#D32F2F'>л</tspan></text>
  <text x='110' y='245' text-anchor='middle' font-size='12' fill='#0D47A1'>"I said" (boy)</text>
  <rect x='210' y='75' width='160' height='180' rx='14' fill='#F8BBD0' stroke='#C2185B' stroke-width='3'/>
  <text x='290' y='115' text-anchor='middle' font-size='70'>👧</text>
  <text x='290' y='160' text-anchor='middle' font-size='15' font-weight='bold' fill='#880E4F'>Girl says:</text>
  <rect x='225' y='175' width='130' height='50' rx='10' fill='white' stroke='#C2185B' stroke-width='2'/>
  <text x='290' y='208' text-anchor='middle' font-size='22' font-weight='bold' fill='#880E4F'>я сказа<tspan fill='#D32F2F'>ла</tspan></text>
  <text x='290' y='245' text-anchor='middle' font-size='12' fill='#880E4F'>"I said" (girl)</text>
</svg>"""

_C12 = """<svg viewBox='0 0 400 280' xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='400' height='280' fill='#FAFAFA'/>
  <text x='200' y='25' text-anchor='middle' font-size='18' font-weight='bold' fill='#333'>How plurals form: ONE → MANY</text>
  <text x='40' y='65' font-size='14' fill='#666'>1️⃣</text>
  <text x='200' y='65' text-anchor='middle' font-size='14' fill='#666'>→</text>
  <text x='340' y='65' text-anchor='middle' font-size='14' fill='#666'>many</text>
  <rect x='15' y='75' width='370' height='42' rx='8' fill='#BBDEFB' stroke='#1565C0' stroke-width='2'/>
  <text x='30' y='102' font-size='17' font-weight='bold' fill='#0D47A1'>стол</text>
  <text x='200' y='102' text-anchor='middle' font-size='17' fill='#666'>→</text>
  <text x='370' y='102' text-anchor='end' font-size='17' font-weight='bold' fill='#0D47A1'>стол<tspan fill='#D32F2F'>ы</tspan></text>
  <text x='30' y='115' font-size='9' fill='#666'>(table)</text>
  <text x='370' y='115' text-anchor='end' font-size='9' fill='#666'>(tables) · -ы</text>
  <rect x='15' y='128' width='370' height='42' rx='8' fill='#F8BBD0' stroke='#C2185B' stroke-width='2'/>
  <text x='30' y='155' font-size='17' font-weight='bold' fill='#880E4F'>книга</text>
  <text x='200' y='155' text-anchor='middle' font-size='17' fill='#666'>→</text>
  <text x='370' y='155' text-anchor='end' font-size='17' font-weight='bold' fill='#880E4F'>книг<tspan fill='#D32F2F'>и</tspan></text>
  <text x='30' y='168' font-size='9' fill='#666'>(book)</text>
  <text x='370' y='168' text-anchor='end' font-size='9' fill='#666'>(books) · -и</text>
  <rect x='15' y='181' width='370' height='42' rx='8' fill='#FFF59D' stroke='#F57F17' stroke-width='2'/>
  <text x='30' y='208' font-size='17' font-weight='bold' fill='#E65100'>окно</text>
  <text x='200' y='208' text-anchor='middle' font-size='17' fill='#666'>→</text>
  <text x='370' y='208' text-anchor='end' font-size='17' font-weight='bold' fill='#E65100'>окн<tspan fill='#D32F2F'>а</tspan></text>
  <text x='30' y='221' font-size='9' fill='#666'>(window)</text>
  <text x='370' y='221' text-anchor='end' font-size='9' fill='#666'>(windows) · -о→-а</text>
  <rect x='15' y='234' width='370' height='38' rx='8' fill='#C8E6C9' stroke='#2E7D32' stroke-width='2'/>
  <text x='30' y='258' font-size='15' font-weight='bold' fill='#1B5E20'>дом</text>
  <text x='200' y='258' text-anchor='middle' font-size='15' fill='#666'>→</text>
  <text x='370' y='258' text-anchor='end' font-size='15' font-weight='bold' fill='#1B5E20'>дом<tspan fill='#D32F2F'>а</tspan></text>
  <text x='30' y='268' font-size='8' fill='#666'>(house)</text>
  <text x='370' y='268' text-anchor='end' font-size='8' fill='#666'>(houses) — exception!</text>
</svg>"""


GRAMMAR_PRESETS = {
    "он, она, оно": {
        "translation": "he / she / it 👨👩🌟 — every Russian noun is one of these, even objects!",
        "example_ru": "Стол — он. Мама — она. Окно — оно.",
        "example_en": "Table — he. Mom — she. Window — it.",
        "mnemonic": "Russian sees every word as a person: a boy-word, a girl-word, or an it-word.",
        "svg": _C1,
    },
    "род существительных": {
        "translation": "How to GUESS the gender of a Russian noun: just look at the LAST LETTER. 🔍",
        "example_ru": "стол → consonant → ОН. мама → -а → ОНА. окно → -о → ОНО.",
        "example_en": "Last letter is the secret: hard ending = he, A-sound = she, O/E = it.",
        "mnemonic": "Three quick rules: ends-in-consonant ⇒ м (он), ends-in-а/-я ⇒ ж (она), ends-in-о/-е ⇒ ср (оно).",
        "svg": _C2,
    },
    "большой / большая / большое / большие": {
        "translation": "BIG — adjective ending CHANGES to match its noun: -ой / -ая / -ое / -ие 🏠🐕🪟👫",
        "example_ru": "Большой дом, большая собака, большое окно, большие друзья.",
        "example_en": "Big house, big dog, big window, big friends.",
        "mnemonic": "Adjectives 'dress up' to match the noun. Same word, four outfits!",
        "svg": _C3,
    },
    "красный / красная / красное / красные": {
        "translation": "RED — same idea: -ый (m) / -ая (f) / -ое (n) / -ые (pl). Watch — most adjectives use -ый, not -ой!",
        "example_ru": "Красный мяч, красная машина, красное яблоко, красные цветы.",
        "example_en": "Red ball, red car, red apple, red flowers.",
        "mnemonic": "-ой is only for STRESSED endings (большОЙ). Most adjectives quietly use -ый.",
        "svg": _C4,
    },
    "хороший / хорошая / хорошее / хорошие": {
        "translation": "GOOD — same gender pattern, but a SPELLING twist: after ш/ж/ч/щ, write И not Ы. 👨👩🌅",
        "example_ru": "Хороший папа, хорошая мама, хорошее утро, хорошие дети.",
        "example_en": "Good dad, good mom, good morning, good kids.",
        "mnemonic": "Hush-letters (ш ж ч щ) hate Ы — they always grab И instead. Easier to say!",
        "svg": _C5,
    },
    "мой / моя / моё / мои": {
        "translation": "MY 💖 — also dresses up: мой папа, моя мама, моё имя, мои друзья.",
        "example_ru": "Это мой друг, моя подруга, моё место, мои родители.",
        "example_en": "This is my friend (boy), my friend (girl), my seat, my parents.",
        "mnemonic": "Even 'my' has to match — same -ой / -оя / -оё / -ои rhythm.",
        "svg": _C6,
    },
    "твой / твоя / твоё / твои": {
        "translation": "YOUR (to a friend) 👉 — same four endings as МОЙ. Just swap М→Т.",
        "example_ru": "Твой карандаш, твоя книга, твоё место, твои родители.",
        "example_en": "Your pencil, your book, your seat, your parents.",
        "mnemonic": "M for me, T for you. Endings stay the same.",
        "svg": _C7,
    },
    "этот / эта / это / эти": {
        "translation": "THIS — pointing words match noun gender: этот стул, эта парта, это окно, эти карандаши.",
        "example_ru": "Этот мальчик, эта девочка, это окно, эти дети.",
        "example_en": "This boy, this girl, this window, these kids.",
        "mnemonic": "Note: 'это' alone (without a noun) means 'this is...' — like 'это мама' = 'this is mom'.",
        "svg": _C8,
    },
    "я хочу, ты хочешь, он хочет": {
        "translation": "хотеть (to want) — verb CHANGES by who's doing it. Six 'who's, six endings.",
        "example_ru": "Я хочу пить. Ты хочешь играть? Мама хочет спать. Дети хотят конфету.",
        "example_en": "I want a drink. Do you want to play? Mom wants to sleep. Kids want candy.",
        "mnemonic": "Memorize like a song: я-ты-он-мы-вы-они. Every Russian verb has these 6 forms.",
        "svg": _C9,
    },
    "я ем, ты ешь, он ест": {
        "translation": "есть (to eat) 🍎 — same idea: 6 endings for 6 'who's. Practice with food words!",
        "example_ru": "Я ем кашу. Ты ешь суп. Папа ест хлеб. Мы едим вместе.",
        "example_en": "I eat porridge. You eat soup. Dad eats bread. We eat together.",
        "mnemonic": "Most verbs follow this pattern: -у/-ю, -ешь, -ет, -ем, -ете, -ут/-ют.",
        "svg": _C10,
    },
    "я сказал / я сказала": {
        "translation": "Past tense KNOWS your gender! 👦 says -л, 👧 says -ла. Important — boys and girls speak differently in past!",
        "example_ru": "Я сказала маме (girl). Я сказал папе (boy). Мама сказала пока. Брат упал.",
        "example_en": "I told mom (girl). I told dad (boy). Mom said bye. Brother fell.",
        "mnemonic": "Past tense endings: -л (he), -ла (she), -ло (it), -ли (they). Pick by who DID it.",
        "svg": _C11,
    },
    "столы, книги, окна, дома": {
        "translation": "PLURALS: most masc/fem add -ы or -и; neuter changes -о → -а. A few like 'дом → дома' use -а too.",
        "example_ru": "Один стол — много столов. Одна книга — много книг. Одно окно — много окон.",
        "example_en": "One table — many tables. One book — many books. One window — many windows.",
        "mnemonic": "Default plural is -ы/-и. Neuter -о flips to -а. 'Дом → дома' is a friendly exception.",
        "svg": _C12,
    },
}
