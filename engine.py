from __future__ import annotations

import base64
import json
import os
import re
from typing import Any
from urllib.parse import quote_plus

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional at runtime
    OpenAI = None


MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

RUSSIAN_TERM_MAP = {
    "скулит": "whining",
    "лает": "barking",
    "рычит": "growling",
    "воет": "howling",
    "грызет": "chewing",
    "кусает": "biting",
    "разрушает": "destroying",
    "один": "alone",
    "одна": "alone",
    "дома один": "home alone",
    "гости": "guests",
    "поводок": "leash",
    "гулять": "walk",
    "машина": "car",
    "поездка": "travel",
    "клетка": "crate",
    "ночью": "night",
    "лоток": "litter box",
    "писает": "urinating",
    "не может пописать": "cannot urinate",
    "тужится": "straining to urinate",
    "кровь": "blood",
    "рвота": "vomiting",
    "понос": "diarrhea",
    "боль": "pain",
    "болит": "pain",
    "хромает": "limping",
    "дрожит": "trembling",
    "судороги": "seizures",
    "упал": "collapse",
    "падает": "collapse",
    "не ест": "not eating",
    "не пьет": "not drinking",
    "прячется": "hiding",
    "царапает": "scratching",
    "метит": "marking",
    "тревога": "anxiety",
    "тревожность": "anxiety",
}

WHEN_LABELS = {
    "en": {
        "home_alone": "home-alone moments",
        "guests": "when people come over",
        "walks": "on walks or near the front door",
        "car": "during car rides",
        "night": "at night",
        "anytime": "across the day",
        "litter_box": "around the litter box",
        "mealtime": "around food or high-value items",
        "new_home": "since a recent change",
    },
    "ru": {
        "home_alone": "когда остается один дома",
        "guests": "когда приходят люди",
        "walks": "на прогулках или у двери",
        "car": "в машине",
        "night": "ночью",
        "anytime": "в течение дня",
        "litter_box": "вокруг лотка",
        "mealtime": "возле еды или ценных вещей",
        "new_home": "после недавних перемен",
    },
}

INTENSITY_LABELS = {
    "en": {"low": "mild", "medium": "moderate", "high": "high"},
    "ru": {"low": "мягкая", "medium": "средняя", "high": "высокая"},
}

DURATION_LABELS = {
    "en": {
        "sudden": "sudden change",
        "days": "last few days",
        "weeks": "last few weeks",
        "months": "ongoing for a while",
    },
    "ru": {
        "sudden": "резкое изменение",
        "days": "последние дни",
        "weeks": "последние недели",
        "months": "давно продолжается",
    },
}

CONDITION_LABELS = {
    "en": {
        "recent_adoption": "recent adoption",
        "rescue_history": "rescue or unknown history",
        "senior_pet": "senior pet",
        "pain_or_mobility": "pain or mobility concerns",
        "noise_sensitivity": "noise sensitivity",
        "multi_pet_home": "multi-pet home",
    },
    "ru": {
        "recent_adoption": "недавнее появление в доме",
        "rescue_history": "питомец из приюта или с неизвестной историей",
        "senior_pet": "пожилой питомец",
        "pain_or_mobility": "есть боль или сложности с подвижностью",
        "noise_sensitivity": "чувствительность к шуму",
        "multi_pet_home": "в доме несколько питомцев",
    },
}

BADGE_LABELS = {
    "en": {
        "safe": "Light Coaching",
        "caution": "Needs Structure",
        "priority": "Priority Support",
        "avoid": "Vet-First",
    },
    "ru": {
        "safe": "Спокойный коучинг",
        "caution": "Нужна структура",
        "priority": "Нужна поддержка",
        "avoid": "Сначала к ветеринару",
    },
}

CONFIDENCE_LABELS = {
    "en": {1: "Starting point", 2: "Moderate confidence", 3: "High confidence"},
    "ru": {1: "Стартовая оценка", 2: "Средняя уверенность", 3: "Высокая уверенность"},
}

PRODUCT_LIBRARY = {
    "lick_mat": {
        "title": {"en": "Lick mat", "ru": "Лизательный коврик"},
        "why": {
            "en": "Useful for short calm reps, departure practice, and decompression.",
            "ru": "Помогает в спокойных коротких упражнениях, тренировке ухода хозяина и расслаблении.",
        },
        "query": {"dog": "dog lick mat", "cat": "cat lick mat"},
    },
    "snuffle_mat": {
        "title": {"en": "Snuffle mat", "ru": "Нюхательный коврик"},
        "why": {
            "en": "Turns part of the meal into a slow nose job instead of restless pacing.",
            "ru": "Превращает часть кормления в спокойную работу носом вместо беспокойного хождения.",
        },
        "query": {"dog": "dog snuffle mat", "cat": "cat snuffle mat"},
    },
    "front_clip_harness": {
        "title": {"en": "Front-clip harness", "ru": "Шлейка с передним креплением"},
        "why": {
            "en": "Helps lower pulling pressure while you teach calmer walk mechanics.",
            "ru": "Снижает силу рывков, пока вы обучаете более спокойной прогулке.",
        },
        "query": {"dog": "front clip dog harness", "cat": "escape proof cat harness"},
    },
    "long_line": {
        "title": {"en": "Long line", "ru": "Длинный поводок"},
        "why": {
            "en": "Good for decompression walks and distance from triggers.",
            "ru": "Подходит для спокойных прогулок и увеличения дистанции от триггеров.",
        },
        "query": {"dog": "long line dog leash", "cat": "long line pet leash"},
    },
    "treat_pouch": {
        "title": {"en": "Treat pouch", "ru": "Поясная сумка для лакомств"},
        "why": {
            "en": "Makes fast reinforcement easier when you catch the calm moment.",
            "ru": "Позволяет быстро подкреплять спокойное поведение в нужный момент.",
        },
        "query": {"dog": "dog treat pouch", "cat": "pet treat pouch"},
    },
    "crate_cover": {
        "title": {"en": "Crate cover", "ru": "Чехол для клетки"},
        "why": {
            "en": "Can soften visual stimulation if the crate already feels safe enough.",
            "ru": "Может уменьшить визуальную нагрузку, если сама клетка уже стала безопасным местом.",
        },
        "query": {"dog": "dog crate cover", "cat": "pet crate cover"},
    },
    "stuffed_toy": {
        "title": {"en": "Stuffable enrichment toy", "ru": "Игрушка для наполнения едой"},
        "why": {
            "en": "Gives chewing and licking an appropriate outlet during hard moments.",
            "ru": "Дает подходящий выход жеванию и облизыванию в напряженные моменты.",
        },
        "query": {"dog": "stuffable dog toy", "cat": "food puzzle cat toy"},
    },
    "baby_gate": {
        "title": {"en": "Baby gate", "ru": "Защитная калитка"},
        "why": {
            "en": "Creates distance without turning every setup into a full isolation event.",
            "ru": "Создает дистанцию без полной изоляции и помогает управлять ситуацией спокойнее.",
        },
        "query": {"dog": "baby gate for dogs", "cat": "pet gate indoor"},
    },
    "chew_bundle": {
        "title": {"en": "Chew rotation", "ru": "Набор жевательных вещей"},
        "why": {
            "en": "Helpful when chewing is part of stress release or puppy/adolescent energy.",
            "ru": "Полезно, когда жевание связано со снятием стресса или возрастной энергией.",
        },
        "query": {"dog": "dog chew toy bundle", "cat": "cat chew toy pack"},
    },
    "seat_belt_harness": {
        "title": {"en": "Travel harness or secure carrier", "ru": "Дорожная шлейка или надежная переноска"},
        "why": {
            "en": "Better stability often lowers panic in the car.",
            "ru": "Лучшая фиксация часто снижает тревогу в машине.",
        },
        "query": {"dog": "dog car harness", "cat": "cat travel carrier"},
    },
    "white_noise": {
        "title": {"en": "White noise machine", "ru": "Генератор белого шума"},
        "why": {
            "en": "Useful for sound-sensitive pets and bedtime settling.",
            "ru": "Полезен для питомцев, чувствительных к шуму, и для вечернего успокоения.",
        },
        "query": {"dog": "white noise machine pet", "cat": "white noise machine pet"},
    },
    "camera": {
        "title": {"en": "Pet camera", "ru": "Камера для питомца"},
        "why": {
            "en": "Shows the exact second the behavior starts so the plan can be more precise.",
            "ru": "Помогает увидеть момент старта проблемы и точнее настроить план.",
        },
        "query": {"dog": "pet camera two way audio", "cat": "pet camera indoor"},
    },
    "cat_tree": {
        "title": {"en": "Tall cat tree", "ru": "Высокое кошачье дерево"},
        "why": {
            "en": "Vertical space helps many cats feel safer before they feel social.",
            "ru": "Вертикальное пространство помогает кошкам чувствовать себя в безопасности до того, как они станут более социальными.",
        },
        "query": {"dog": "small pet perch", "cat": "tall cat tree"},
    },
    "vertical_scratcher": {
        "title": {"en": "Vertical scratcher", "ru": "Вертикальная когтеточка"},
        "why": {
            "en": "Gives scratching a legal outlet close to the spots already being targeted.",
            "ru": "Дает легальную точку для царапания рядом с теми местами, которые уже выбраны питомцем.",
        },
        "query": {"dog": "pet scratch pad", "cat": "vertical cat scratcher"},
    },
    "extra_litter_box": {
        "title": {"en": "Extra litter box", "ru": "Дополнительный лоток"},
        "why": {
            "en": "For cats, more easy-to-reach boxes often lowers conflict fast.",
            "ru": "Для кошек дополнительный доступный лоток часто быстро снижает напряжение.",
        },
        "query": {"dog": "pet potty tray", "cat": "cat litter box large"},
    },
    "unscented_litter": {
        "title": {"en": "Unscented litter", "ru": "Лоточный наполнитель без запаха"},
        "why": {
            "en": "A simple litter change can help if the current box setup feels aversive.",
            "ru": "Иногда достаточно сменить наполнитель, если текущий вариант неприятен кошке.",
        },
        "query": {"dog": "pet litter tray", "cat": "unscented clumping cat litter"},
    },
    "enzymatic_cleaner": {
        "title": {"en": "Enzymatic cleaner", "ru": "Энзимный очиститель"},
        "why": {
            "en": "Helps remove residual odor so the same spot is less likely to attract repeats.",
            "ru": "Помогает убрать остаточный запах и уменьшить шанс повторения в том же месте.",
        },
        "query": {"dog": "enzymatic pet cleaner", "cat": "enzymatic pet cleaner"},
    },
    "covered_bed": {
        "title": {"en": "Covered retreat bed", "ru": "Закрытый лежак-убежище"},
        "why": {
            "en": "A semi-hidden safe spot can help shy pets recover faster after stress.",
            "ru": "Полузакрытое безопасное место помогает пугливым питомцам быстрее восстанавливаться после стресса.",
        },
        "query": {"dog": "covered dog bed calming", "cat": "covered cat bed"},
    },
    "pheromone_diffuser": {
        "title": {"en": "Pheromone diffuser", "ru": "Феромонный диффузор"},
        "why": {
            "en": "Can support a calmer baseline, especially during transitions or tension at home.",
            "ru": "Может поддерживать более спокойный фон, особенно во время перемен и домашнего напряжения.",
        },
        "query": {"dog": "dog calming diffuser", "cat": "cat pheromone diffuser"},
    },
}

ISSUE_LIBRARY = {
    "not_sure": {
        "species": ["dog", "cat"],
        "label": {"en": "Not sure yet", "ru": "Пока не уверен"},
        "pattern": {"en": "Behavior pattern needs narrowing", "ru": "Нужно уточнить поведенческий паттерн"},
        "summary": {
            "en": "This sounds real, but it is still broad. The fastest win is to shrink the moment, observe what happens right before it, and stop treating it like a character flaw.",
            "ru": "Проблема звучит реально, но пока слишком широко. Самый быстрый шаг — сузить момент, посмотреть, что происходит прямо перед ним, и не считать это «характером».",
        },
        "drivers": {
            "en": [
                "The behavior may be part stress, part habit, and part unmet outlet.",
                "Without a clear trigger, pets often look stubborn when they are actually overloaded.",
            ],
            "ru": [
                "Поведение может быть смесью стресса, привычки и нехватки подходящего выхода энергии.",
                "Когда триггер неясен, питомец выглядит упрямым, хотя на деле он просто перегружен.",
            ],
        },
        "today": {
            "en": [
                "Notice what happens in the 60 seconds right before the problem starts.",
                "Reduce the difficulty of that moment instead of repeating the same failing setup.",
                "Reward the first calmer choice, even if it lasts only a second or two.",
            ],
            "ru": [
                "Заметь, что происходит за 60 секунд до старта проблемы.",
                "Сделай этот момент проще вместо повторения той же неудачной ситуации.",
                "Подкрепляй первый более спокойный выбор, даже если он длится всего секунду-две.",
            ],
        },
        "week": {
            "en": [
                "Track time, trigger, intensity, and recovery for one week.",
                "Look for a repeatable pattern before changing too many things at once.",
                "Keep routines predictable so stress has fewer surprise spikes.",
            ],
            "ru": [
                "В течение недели отмечай время, триггер, силу реакции и скорость восстановления.",
                "Сначала найди повторяющийся паттерн, а не меняй сразу все подряд.",
                "Сделай рутину предсказуемой, чтобы было меньше резких всплесков стресса.",
            ],
        },
        "vet": {
            "en": [
                "Get veterinary input if the change is sudden, intense, or paired with appetite, sleep, or mobility changes.",
            ],
            "ru": [
                "Подключай ветеринара, если изменение резкое, сильное или сопровождается изменением аппетита, сна или подвижности.",
            ],
        },
        "toolkit": {"dog": ["snuffle_mat", "camera", "white_noise"], "cat": ["cat_tree", "covered_bed", "pheromone_diffuser"]},
    },
    "general_anxiety": {
        "species": ["dog", "cat"],
        "label": {"en": "General anxiety", "ru": "Общая тревожность"},
        "pattern": {"en": "General stress load", "ru": "Общий повышенный стресс"},
        "summary": {
            "en": "This looks less like disobedience and more like a nervous system that stays switched on too easily.",
            "ru": "Это больше похоже не на непослушание, а на нервную систему, которая слишком легко остается в режиме напряжения.",
        },
        "drivers": {
            "en": [
                "Unclear routines and constant stimulation can keep arousal elevated.",
                "Stress often stacks: noise, lack of rest, change, and anticipation all add up.",
            ],
            "ru": [
                "Непонятная рутина и постоянная стимуляция могут держать уровень возбуждения слишком высоким.",
                "Стресс часто складывается из нескольких слоев: шум, недосып, перемены и ожидание.",
            ],
        },
        "today": {
            "en": [
                "Lower novelty for the next 24 hours and make the day more predictable.",
                "Use short sniffing, licking, or foraging tasks instead of more excitement.",
                "Protect one quiet recovery block with no drilling or pressure.",
            ],
            "ru": [
                "На ближайшие сутки снизь количество нового и сделай день более предсказуемым.",
                "Используй короткие задания на нюхание, облизывание или поиск еды вместо лишнего возбуждения.",
                "Дай один спокойный блок восстановления без давления и тренировочной суеты.",
            ],
        },
        "week": {
            "en": [
                "Keep wake-up, meals, walks, and rest windows on a steadier schedule.",
                "Measure progress by faster recovery, not by instant perfection.",
                "Build calm in tiny reps before asking for hard social situations.",
            ],
            "ru": [
                "Сделай более стабильными подъем, еду, прогулки и периоды отдыха.",
                "Оцени прогресс по более быстрому восстановлению, а не по мгновенному идеалу.",
                "Сначала тренируй спокойствие маленькими подходами, а потом уже сложные социальные ситуации.",
            ],
        },
        "vet": {
            "en": [
                "Talk to your vet if anxiety suddenly intensified or started alongside pain, GI upset, or sleep disruption.",
            ],
            "ru": [
                "Обсуди с ветеринаром, если тревожность резко усилилась или совпала с болью, ЖКТ-проблемами или нарушением сна.",
            ],
        },
        "toolkit": {"dog": ["lick_mat", "snuffle_mat", "white_noise"], "cat": ["covered_bed", "cat_tree", "pheromone_diffuser"]},
    },
    "separation_anxiety": {
        "species": ["dog", "cat"],
        "label": {"en": "Separation anxiety", "ru": "Тревога разлуки"},
        "pattern": {"en": "Separation distress", "ru": "Тревога разлуки"},
        "summary": {
            "en": "This looks like absence-related distress. The goal is to make departures smaller and more boring, not to force the pet to “just deal with it.”",
            "ru": "Это похоже на стресс, связанный с отсутствием человека. Цель — сделать уходы короче и скучнее, а не заставлять питомца «терпеть».",
        },
        "drivers": {
            "en": [
                "Departure cues can become a trigger long before the human actually leaves.",
                "Once panic starts, the learning part shuts down and the pet practices distress instead.",
            ],
            "ru": [
                "Триггером могут стать уже сами сигналы ухода еще до реального выхода человека.",
                "Когда начинается паника, обучение выключается, и питомец только закрепляет тревогу.",
            ],
        },
        "today": {
            "en": [
                "Break your leaving routine into tiny pieces and practice the earliest cues calmly.",
                "Keep absences below the point where full panic starts whenever possible.",
                "Use a calm food project only if the pet can actually stay under threshold with it.",
            ],
            "ru": [
                "Разбей рутину ухода на маленькие части и отдельно потренируй самые ранние сигналы спокойно.",
                "По возможности не доводи отсутствие до уровня полной паники.",
                "Используй спокойный пищевой проект только если он действительно помогает питомцу оставаться ниже порога.",
            ],
        },
        "week": {
            "en": [
                "Practice very short departures many times rather than a few hard absences.",
                "Track the first signs of stress so you know the real starting point.",
                "Aim for a smoother departure arc before adding duration.",
            ],
            "ru": [
                "Тренируй много очень коротких уходов вместо нескольких тяжелых длинных отсутствий.",
                "Отмечай самый первый признак стресса, чтобы понимать реальную стартовую точку.",
                "Сначала добейся более гладкого ухода, а уже потом добавляй длительность.",
            ],
        },
        "vet": {
            "en": [
                "Consider a vet or credentialed behavior professional if panic escalates fast, self-injury appears, or progress stalls.",
            ],
            "ru": [
                "Подключай ветеринара или квалифицированного специалиста по поведению, если паника быстро нарастает, появляется самоповреждение или нет прогресса.",
            ],
        },
        "toolkit": {"dog": ["lick_mat", "camera", "white_noise"], "cat": ["covered_bed", "pheromone_diffuser", "camera"]},
    },
    "barking_reactivity": {
        "species": ["dog"],
        "label": {"en": "Barking or reactivity", "ru": "Лай и реактивность"},
        "pattern": {"en": "Trigger-based arousal", "ru": "Реакция на триггеры"},
        "summary": {
            "en": "This looks like a threshold problem, not a respect problem. Distance and better timing usually help more than correction.",
            "ru": "Это больше похоже на проблему порога, а не на «неуважение». Дистанция и хороший тайминг обычно помогают лучше, чем коррекция.",
        },
        "drivers": {
            "en": [
                "The trigger may be arriving too fast or too close for the pet to stay thoughtful.",
                "Repeated blowups can build an expectation of conflict before the trigger even appears.",
            ],
            "ru": [
                "Триггер может оказываться слишком близко или слишком резко, чтобы питомец мог оставаться в спокойном обучаемом состоянии.",
                "Повторяющиеся срывы формируют ожидание конфликта еще до появления триггера.",
            ],
        },
        "today": {
            "en": [
                "Give more distance from the trigger than you think you need.",
                "Reinforce orientation back to you before the barking spiral starts.",
                "Use shorter outings if that keeps the dog under threshold.",
            ],
            "ru": [
                "Давай больше дистанции до триггера, чем кажется нужным.",
                "Подкрепляй поворот внимания к тебе до того, как лай успеет раскрутиться.",
                "Если так проще держать собаку ниже порога, сокращай прогулки.",
            ],
        },
        "week": {
            "en": [
                "Choose easier routes and repeat successful distances before making things harder.",
                "Count recoveries, not explosions alone.",
                "Pair predictable triggers with calm food or movement patterns before they get too close.",
            ],
            "ru": [
                "Выбирай более легкие маршруты и повторяй удачные дистанции до усложнения.",
                "Считай не только срывы, но и скорость восстановления.",
                "Связывай предсказуемые триггеры со спокойными паттернами еды или движения до слишком близкого подхода.",
            ],
        },
        "vet": {
            "en": [
                "Seek professional help faster if growling, lunging, or bite risk is climbing.",
            ],
            "ru": [
                "Быстрее подключай специалиста, если растут рычание, выпады или риск укуса.",
            ],
        },
        "toolkit": {"dog": ["front_clip_harness", "long_line", "treat_pouch"]},
    },
    "leash_pulling": {
        "species": ["dog"],
        "label": {"en": "Leash pulling", "ru": "Тянет поводок"},
        "pattern": {"en": "Over-aroused walking pattern", "ru": "Перевозбужденный паттерн прогулки"},
        "summary": {
            "en": "This usually improves when the walk becomes clearer and more decompression-focused, not when every step becomes a battle.",
            "ru": "Обычно это улучшается, когда прогулка становится понятнее и спокойнее, а не когда каждый шаг превращается в борьбу.",
        },
        "drivers": {
            "en": [
                "Fast forward motion can become its own reward and make pulling self-reinforcing.",
                "If the dog starts the walk already excited, loose leash skills disappear quickly.",
            ],
            "ru": [
                "Быстрое движение вперед само по себе становится наградой и закрепляет натяжение.",
                "Если собака выходит на прогулку уже перевозбужденной, навык свободного поводка быстро пропадает.",
            ],
        },
        "today": {
            "en": [
                "Start with one calmer decompression minute before asking for precision.",
                "Reward the leash slack moment, not the perfect heel picture.",
                "Shorten the session if frustration rises for both of you.",
            ],
            "ru": [
                "Начинай с минуты спокойной декомпрессии перед более точной работой.",
                "Подкрепляй момент свободного поводка, а не идеальную картинку рядом.",
                "Сокращай прогулку, если фрустрация растет у обоих.",
            ],
        },
        "week": {
            "en": [
                "Train in easier environments before expecting the skill on stimulating routes.",
                "Use more sniff breaks so the dog is not fighting the walk the whole time.",
                "Measure progress in more loose steps, not perfect whole walks.",
            ],
            "ru": [
                "Сначала тренируйся в простых местах, а потом уже ожидай навык на сложных маршрутах.",
                "Добавляй больше пауз на нюхание, чтобы собака не боролась с прогулкой все время.",
                "Измеряй прогресс по количеству свободных шагов, а не по идеальной прогулке целиком.",
            ],
        },
        "vet": {
            "en": [
                "If pulling changed suddenly, check for pain, harness fit, and paw discomfort before assuming a training issue.",
            ],
            "ru": [
                "Если натяжение началось резко, сначала проверь боль, посадку шлейки и дискомфорт в лапах, а не считай это только вопросом тренировки.",
            ],
        },
        "toolkit": {"dog": ["front_clip_harness", "long_line", "treat_pouch"]},
    },
    "crate_resistance": {
        "species": ["dog"],
        "label": {"en": "Crate resistance", "ru": "Сопротивление клетке"},
        "pattern": {"en": "Confinement stress", "ru": "Стресс из-за ограничения пространства"},
        "summary": {
            "en": "The crate should feel like a good prediction, not just a place where hard feelings happen.",
            "ru": "Клетка должна предсказывать что-то хорошее, а не быть местом, где регулярно случается стресс.",
        },
        "drivers": {
            "en": [
                "If the crate mostly predicts isolation or frustration, resistance grows quickly.",
                "Some dogs need more gradual entry and shorter duration than people expect.",
            ],
            "ru": [
                "Если клетка в основном предсказывает изоляцию или фрустрацию, сопротивление быстро усиливается.",
                "Некоторым собакам нужен более плавный вход и гораздо меньшая длительность, чем кажется людям.",
            ],
        },
        "today": {
            "en": [
                "Feed or scatter easy wins near the crate before asking for full entry.",
                "Practice tiny in-and-out reps with the door open first.",
                "Do not jump straight to long closed-door sessions if the picture is already emotional.",
            ],
            "ru": [
                "Давай еду или простые подкрепления рядом с клеткой до просьбы зайти полностью.",
                "Сначала делай очень короткие заходы и выходы с открытой дверцей.",
                "Не переходи сразу к долгим закрытым сессиям, если картинка уже эмоциональная.",
            ],
        },
        "week": {
            "en": [
                "Build entry, settle, and duration as separate pieces.",
                "Repeat success at the easy level before changing two variables at once.",
                "Keep at least some crate reps unrelated to you leaving.",
            ],
            "ru": [
                "Собирай вход, расслабление и длительность как отдельные части.",
                "Повторяй успех на легком уровне, прежде чем менять сразу два параметра.",
                "Пусть часть занятий с клеткой вообще не связана с твоим уходом.",
            ],
        },
        "vet": {
            "en": [
                "If vocalizing is extreme, the crate causes injury, or panic ramps fast, get behavior support instead of pushing through.",
            ],
            "ru": [
                "Если вокализация сильная, есть риск травмы в клетке или паника быстро растет, подключай поведенческую помощь вместо продавливания.",
            ],
        },
        "toolkit": {"dog": ["crate_cover", "stuffed_toy", "baby_gate"]},
    },
    "chewing_biting": {
        "species": ["dog", "cat"],
        "label": {"en": "Chewing or biting", "ru": "Грызет или кусает"},
        "pattern": {"en": "Outlet and arousal mismatch", "ru": "Не хватает подходящего выхода энергии"},
        "summary": {
            "en": "This often improves when the pet gets a better legal outlet and the hard moments are managed earlier.",
            "ru": "Часто это улучшается, когда у питомца появляется лучший легальный выход энергии, а сложные моменты управляются раньше.",
        },
        "drivers": {
            "en": [
                "Chewing and mouthing can rise with stress, teething, boredom, or overtiredness.",
                "If the environment keeps presenting tempting targets, rehearsal stays strong.",
            ],
            "ru": [
                "Жевание и кусание усиливаются из-за стресса, смены зубов, скуки или переутомления.",
                "Если среда постоянно подбрасывает соблазнительные цели, привычка только закрепляется.",
            ],
        },
        "today": {
            "en": [
                "Block access to the highest-value problem items for now.",
                "Offer an easier legal chew or toy before the usual hot moments.",
                "Redirect early and calmly instead of waiting for full chaos.",
            ],
            "ru": [
                "Пока закрой доступ к самым проблемным предметам.",
                "Предлагай разрешенный жевательный предмет заранее, до привычных горячих моментов.",
                "Перенаправляй спокойно и рано, а не когда уже начался хаос.",
            ],
        },
        "week": {
            "en": [
                "Rotate legal outlets so they stay interesting.",
                "Notice patterns: tired, overexcited, alone, or after play can all mean different plans.",
                "Reward disengagement from forbidden items whenever you catch it.",
            ],
            "ru": [
                "Чередуй разрешенные предметы, чтобы они не наскучивали.",
                "Смотри на паттерны: усталость, перевозбуждение, одиночество или момент после игры требуют разных решений.",
                "Подкрепляй любое самостоятельное отвлечение от запретных вещей, когда успеваешь его заметить.",
            ],
        },
        "vet": {
            "en": [
                "Get vet input if mouthing or biting rose suddenly with pain signs, GI issues, or major sleep changes.",
            ],
            "ru": [
                "Иди к ветеринару, если кусание резко усилилось на фоне боли, ЖКТ-проблем или сильных изменений сна.",
            ],
        },
        "toolkit": {"dog": ["chew_bundle", "stuffed_toy", "baby_gate"], "cat": ["vertical_scratcher", "cat_tree", "covered_bed"]},
    },
    "car_travel": {
        "species": ["dog", "cat"],
        "label": {"en": "Car or travel stress", "ru": "Тревога в машине или поездке"},
        "pattern": {"en": "Travel stress response", "ru": "Стресс от поездки"},
        "summary": {
            "en": "Travel stress usually improves when motion, confinement, and prediction are trained in smaller pieces.",
            "ru": "Стресс от поездок обычно уменьшается, когда движение, ограничение и предсказуемость тренируются маленькими частями.",
        },
        "drivers": {
            "en": [
                "Some pets react to motion itself, others to the setup around getting into the car.",
                "If the car mostly predicts difficult destinations, resistance often starts before movement.",
            ],
            "ru": [
                "Одни питомцы реагируют на само движение, другие — уже на подготовку и посадку в машину.",
                "Если машина в основном предсказывает неприятные поездки, сопротивление начинается еще до движения.",
            ],
        },
        "today": {
            "en": [
                "Practice sitting in the parked car without going anywhere.",
                "Shorten the setup so the pet enters, settles, and exits before stress spikes.",
                "Use secure support rather than loose movement in the vehicle.",
            ],
            "ru": [
                "Потренируйся просто сидеть в припаркованной машине без поездки.",
                "Сократи упражнение так, чтобы питомец успел зайти, успокоиться и выйти до пика стресса.",
                "Используй надежную фиксацию, а не свободное перемещение в салоне.",
            ],
        },
        "week": {
            "en": [
                "Train entry, stillness, engine-on, and short movement as separate layers.",
                "Finish on easy reps instead of only doing full hard drives.",
                "Watch whether nausea, fear, or frustration seems to be the bigger piece.",
            ],
            "ru": [
                "Раздели вход, спокойное сидение, включенный двигатель и короткое движение на отдельные слои.",
                "Заканчивай на легких повторах, а не только на полноценных тяжелых поездках.",
                "Понаблюдай, что сильнее: тошнота, страх или фрустрация.",
            ],
        },
        "vet": {
            "en": [
                "If drooling, vomiting, or panic are severe, ask your vet about motion sickness and supportive medication options.",
            ],
            "ru": [
                "Если сильны слюнотечение, рвота или паника, обсуди с ветеринаром укачивание и возможную поддерживающую медикаментозную помощь.",
            ],
        },
        "toolkit": {"dog": ["seat_belt_harness", "covered_bed", "white_noise"], "cat": ["seat_belt_harness", "covered_bed", "pheromone_diffuser"]},
    },
    "night_restlessness": {
        "species": ["dog", "cat"],
        "label": {"en": "Night restlessness", "ru": "Ночное беспокойство"},
        "pattern": {"en": "Night settling difficulty", "ru": "Сложности с успокоением ночью"},
        "summary": {
            "en": "Night issues often come from the whole day picture: too little recovery, too much late stimulation, or a medical piece that needs ruling out.",
            "ru": "Ночные проблемы часто идут от общей картины дня: мало восстановления, слишком много стимуляции вечером или медицинский фактор, который нужно исключить.",
        },
        "drivers": {
            "en": [
                "Overtired pets can look more wired, not more sleepy.",
                "Late activity, hunger, sound sensitivity, or discomfort can all show up most clearly at night.",
            ],
            "ru": [
                "Переутомленный питомец часто выглядит не сонным, а еще более заведенным.",
                "Поздняя активность, голод, чувствительность к звукам или дискомфорт часто сильнее проявляются именно ночью.",
            ],
        },
        "today": {
            "en": [
                "Protect a calmer last hour before bedtime.",
                "Use a low-key enrichment or food task earlier in the evening, not right at lights out.",
                "Make the sleeping setup easier, darker, and quieter tonight.",
            ],
            "ru": [
                "Сделай последний час перед сном спокойнее.",
                "Дай тихое задание или спокойную еду раньше вечером, а не прямо перед выключением света.",
                "Сделай место для сна проще, темнее и тише уже сегодня.",
            ],
        },
        "week": {
            "en": [
                "Look at the whole daily rhythm: naps, movement, meals, and late stimulation.",
                "Keep bedtime cues consistent so the nervous system gets a predictable shutdown signal.",
                "Track whether the issue is waking, pacing, vocalizing, or early-morning start time.",
            ],
            "ru": [
                "Посмотри на весь дневной ритм: сон, движение, еду и позднюю стимуляцию.",
                "Сделай сигналы ко сну стабильными, чтобы нервная система получала понятный сигнал на завершение дня.",
                "Отмечай, в чем именно проблема: пробуждение, хождение, вокализация или слишком ранний подъем.",
            ],
        },
        "vet": {
            "en": [
                "Talk to your vet sooner if night changes are sudden, the pet seems painful, or a senior pet starts pacing or vocalizing more.",
            ],
            "ru": [
                "Быстрее говори с ветеринаром, если ночные изменения начались резко, питомцу больно или пожилой питомец стал больше ходить и вокализировать ночью.",
            ],
        },
        "toolkit": {"dog": ["white_noise", "covered_bed", "lick_mat"], "cat": ["white_noise", "covered_bed", "cat_tree"]},
    },
    "new_pet_adjustment": {
        "species": ["dog", "cat"],
        "label": {"en": "New pet adjustment", "ru": "Адаптация нового питомца"},
        "pattern": {"en": "Transition stress", "ru": "Стресс адаптации"},
        "summary": {
            "en": "A new home often looks messy before it looks settled. The main job is safety, predictability, and gentle information gathering.",
            "ru": "Новый дом почти всегда сначала выглядит хаотично, а уже потом стабильным. Главная задача — безопасность, предсказуемость и мягкий сбор информации.",
        },
        "drivers": {
            "en": [
                "The pet is still learning what the home, humans, and routines mean.",
                "Too much freedom or too much pressure too early can both slow adjustment.",
            ],
            "ru": [
                "Питомец все еще понимает, что означают новый дом, люди и рутина.",
                "Слишком много свободы или слишком много давления слишком рано одинаково тормозят адаптацию.",
            ],
        },
        "today": {
            "en": [
                "Shrink the world and keep only the easiest successful spaces open.",
                "Use steady meal, potty, play, and rest anchors today.",
                "Let observation matter more than performance for now.",
            ],
            "ru": [
                "Уменьши пространство и оставь открытыми только самые простые и успешные зоны.",
                "Сделай сегодня стабильными точки опоры: еда, туалет, игра и отдых.",
                "Пока наблюдение важнее, чем «идеальное поведение».",
            ],
        },
        "week": {
            "en": [
                "Expand freedom slowly as the pet starts making calmer choices.",
                "Keep social and training asks short and easy.",
                "Track which rooms, times, and people feel easiest versus hardest.",
            ],
            "ru": [
                "Расширяй свободу постепенно, когда питомец начнет делать более спокойные выборы.",
                "Делай социальные и тренировочные запросы короткими и легкими.",
                "Отмечай, какие комнаты, время и люди даются легче, а какие тяжелее.",
            ],
        },
        "vet": {
            "en": [
                "Get vet support if appetite, sleep, or elimination is not stabilizing or if the pet seems shut down for days.",
            ],
            "ru": [
                "Подключай ветеринара, если не выравниваются аппетит, сон или туалет, либо питомец остается «выключенным» много дней.",
            ],
        },
        "toolkit": {"dog": ["baby_gate", "covered_bed", "lick_mat"], "cat": ["covered_bed", "cat_tree", "pheromone_diffuser"]},
    },
    "cat_litter_box": {
        "species": ["cat"],
        "label": {"en": "Litter box issues", "ru": "Проблемы с лотком"},
        "pattern": {"en": "Litter setup conflict", "ru": "Конфликт вокруг лотка"},
        "summary": {
            "en": "With litter box issues, behavior and medical questions overlap more than people think, so we stay calmer but we also move faster.",
            "ru": "При проблемах с лотком поведение и медицинские причины пересекаются сильнее, чем кажется, поэтому здесь мы действуем спокойнее, но быстрее.",
        },
        "drivers": {
            "en": [
                "Location, box style, litter feel, cleanliness, and household tension all matter.",
                "Cats often avoid a setup before they fully reject it, so subtle changes count.",
            ],
            "ru": [
                "Важны место, тип лотка, фактура наполнителя, чистота и напряжение в доме.",
                "Кошки часто начинают избегать систему раньше, чем полностью отказываются от нее, поэтому даже мелкие изменения значимы.",
            ],
        },
        "today": {
            "en": [
                "Add an extra easy-to-reach box today if possible.",
                "Scoop more often and avoid strong scents or harsh cleaners on the box itself.",
                "Keep conflict away from litter areas and do not punish accidents.",
            ],
            "ru": [
                "По возможности добавь сегодня еще один доступный лоток.",
                "Убирай чаще и избегай резких запахов или агрессивной чистки самого лотка.",
                "Убери конфликт из зоны лотка и не наказывай за промахи.",
            ],
        },
        "week": {
            "en": [
                "Test one setup change at a time so you can see what helps.",
                "Track exact location, timing, and posture of accidents if they continue.",
                "Watch for patterns with other pets, noise, or blocked access.",
            ],
            "ru": [
                "Меняй только один параметр за раз, чтобы понимать, что реально помогает.",
                "Если проблема сохраняется, отмечай точное место, время и позу во время промахов.",
                "Следи за связью с другими питомцами, шумом или трудным доступом.",
            ],
        },
        "vet": {
            "en": [
                "Any straining, tiny frequent trips, blood, pain, or sudden box avoidance deserves same-day veterinary attention.",
            ],
            "ru": [
                "Любое сильное натуживание, частые маленькие попытки, кровь, боль или резкий отказ от лотка требуют ветеринара в тот же день.",
            ],
        },
        "toolkit": {"cat": ["extra_litter_box", "unscented_litter", "enzymatic_cleaner"]},
    },
    "cat_scratching": {
        "species": ["cat"],
        "label": {"en": "Furniture scratching", "ru": "Царапает мебель"},
        "pattern": {"en": "Scratching outlet mismatch", "ru": "Неудачный выбор места для царапания"},
        "summary": {
            "en": "Scratching is normal cat behavior. The fix is usually placement, surface, and timing, not making the cat stop scratching entirely.",
            "ru": "Царапание — нормальное кошачье поведение. Обычно нужно исправить место, поверхность и тайминг, а не пытаться полностью запретить царапание.",
        },
        "drivers": {
            "en": [
                "Cats scratch for body care, stretching, marking, and emotional regulation.",
                "If the legal scratcher is in the wrong place or feels wrong, the sofa wins.",
            ],
            "ru": [
                "Кошки царапают ради ухода за телом, растяжки, маркировки и эмоциональной разрядки.",
                "Если разрешенная когтеточка стоит не там или ощущается не так, диван побеждает.",
            ],
        },
        "today": {
            "en": [
                "Put a scratcher directly next to the current target spot.",
                "Test both vertical and horizontal options if you are not sure which surface the cat prefers.",
                "Reward the first scratch on the legal item right away.",
            ],
            "ru": [
                "Поставь когтеточку прямо рядом с текущей любимой целью.",
                "Попробуй и вертикальный, и горизонтальный вариант, если пока неясно, какая поверхность нравится больше.",
                "Сразу подкрепляй первый контакт с разрешенной когтеточкой.",
            ],
        },
        "week": {
            "en": [
                "Notice when scratching happens: after waking, after stress, or in social moments.",
                "Make the legal option more obvious before the cat reaches the old target.",
                "Protect the old spot temporarily while the new habit builds.",
            ],
            "ru": [
                "Замечай, когда именно это происходит: после сна, после стресса или в социальные моменты.",
                "Сделай разрешенный вариант более заметным до того, как кошка подойдет к старой цели.",
                "Временно защити старое место, пока формируется новая привычка.",
            ],
        },
        "vet": {
            "en": [
                "If scratching is paired with overgrooming, pain, or major stress signs, look wider than a simple furniture issue.",
            ],
            "ru": [
                "Если царапание сочетается с чрезмерным вылизыванием, болью или сильным стрессом, смотри шире, чем просто проблема мебели.",
            ],
        },
        "toolkit": {"cat": ["vertical_scratcher", "cat_tree", "pheromone_diffuser"]},
    },
    "cat_hiding": {
        "species": ["cat"],
        "label": {"en": "Cat hiding or withdrawal", "ru": "Кошка прячется"},
        "pattern": {"en": "Withdrawal and safety seeking", "ru": "Уход в укрытие и поиск безопасности"},
        "summary": {
            "en": "Hiding is often a safety strategy. The plan is to make the environment safer before asking the cat to be social.",
            "ru": "Прятаться — часто стратегия безопасности. План здесь в том, чтобы сначала сделать среду безопаснее, а уже потом ждать социальной открытости.",
        },
        "drivers": {
            "en": [
                "Cats may hide because the environment feels loud, exposed, unpredictable, or socially heavy.",
                "A withdrawn cat often needs more control, not more pressure.",
            ],
            "ru": [
                "Кошка может прятаться, если среда ощущается шумной, открытой, непредсказуемой или социально тяжелой.",
                "Замкнутой кошке обычно нужно больше контроля, а не больше давления.",
            ],
        },
        "today": {
            "en": [
                "Create safe vertical and covered options near, not inside, the scariest zones.",
                "Let food and interaction come to the edge of safety, not beyond it.",
                "Use a softer voice, slower body language, and fewer reaches tonight.",
            ],
            "ru": [
                "Сделай безопасные вертикальные и закрытые точки рядом, но не внутри самых пугающих зон.",
                "Пусть еда и взаимодействие доходят только до границы чувства безопасности, не дальше.",
                "Используй более мягкий голос, медленные движения и меньше попыток тянуться к кошке.",
            ],
        },
        "week": {
            "en": [
                "Measure progress by shorter hiding time and more curiosity at the edge.",
                "Keep key resources spread out so the cat is not forced through conflict.",
                "Let routine arrivals predict safety and quiet consistency.",
            ],
            "ru": [
                "Оцени прогресс по более короткому времени прятанья и большей любопытности у границы.",
                "Разнеси ключевые ресурсы так, чтобы кошка не была вынуждена проходить через конфликт.",
                "Пусть твое появление в рутине предсказывает безопасность и спокойную стабильность.",
            ],
        },
        "vet": {
            "en": [
                "If the cat is hiding more suddenly, not eating, or seems painful, rule out medical causes early.",
            ],
            "ru": [
                "Если кошка стала резко больше прятаться, не ест или выглядит болезненной, рано исключай медицинские причины.",
            ],
        },
        "toolkit": {"cat": ["covered_bed", "cat_tree", "pheromone_diffuser"]},
    },
}

RED_FLAG_RULES = [
    {
        "terms": ["cannot urinate", "straining to urinate", "blocked", "urinating blood"],
        "en": "Possible urinary blockage or painful urination.",
        "ru": "Возможна закупорка мочевыводящих путей или болезненное мочеиспускание.",
    },
    {
        "terms": ["blood", "collapse", "seizures", "trouble breathing"],
        "en": "Medical red flags show up in the description.",
        "ru": "В описании есть медицинские красные флаги.",
    },
    {
        "terms": ["pain", "limping", "vomiting", "diarrhea", "not eating", "not drinking"],
        "en": "A pain or illness component may be driving the behavior change.",
        "ru": "Изменение поведения может быть связано с болью или заболеванием.",
    },
]


def has_openai_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY")) and OpenAI is not None


def _language_code(language: str | None) -> str:
    return "ru" if str(language or "").lower().startswith("ru") else "en"


def _localized(mapping: Any, language: str) -> Any:
    if isinstance(mapping, dict) and language in mapping:
        return mapping[language]
    return mapping


def _normalize_text(text: str) -> str:
    normalized = (text or "").lower()
    for russian, english in RUSSIAN_TERM_MAP.items():
        normalized = normalized.replace(russian, english)
    return re.sub(r"\s+", " ", normalized).strip()


def _extract_json_object(raw_text: str) -> dict[str, Any] | None:
    if not raw_text:
        return None
    match = re.search(r"\{.*\}", raw_text, flags=re.S)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _pet_name_or_default(pet_name: str | None, language: str) -> str:
    clean = (pet_name or "").strip()
    if clean:
        return clean
    return "питомец" if language == "ru" else "your pet"


def _issue_definition(issue_key: str, species: str) -> dict[str, Any]:
    issue = ISSUE_LIBRARY.get(issue_key) or ISSUE_LIBRARY["not_sure"]
    if species not in issue.get("species", []):
        return ISSUE_LIBRARY["not_sure"]
    return issue


def issue_display_label(issue_key: str, species: str, language: str = "en") -> str:
    issue = _issue_definition(issue_key, species)
    return str(_localized(issue["label"], _language_code(language)))


def behavior_issue_choices(species: str, language: str = "en") -> list[tuple[str, str]]:
    lang = _language_code(language)
    options: list[tuple[str, str]] = []
    for key, issue in ISSUE_LIBRARY.items():
        if species in issue.get("species", []):
            options.append((key, str(_localized(issue["label"], lang))))
    return options


def _search_url(store: str, query: str) -> str:
    encoded = quote_plus(query)
    if store == "chewy":
        return f"https://www.chewy.com/s?query={encoded}"
    return f"https://www.amazon.com/s?k={encoded}"


def _build_toolkit(tool_keys: list[str], species: str, language: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for key in tool_keys:
        product = PRODUCT_LIBRARY.get(key)
        if not product:
            continue
        query_map = product.get("query", {})
        query = query_map.get(species) or query_map.get("dog") or query_map.get("cat") or key
        items.append(
            {
                "title": str(_localized(product["title"], language)),
                "body": str(_localized(product["why"], language)),
                "chewy_url": _search_url("chewy", query),
                "amazon_url": _search_url("amazon", query),
            }
        )
    return items


def _image_summary_text(image_context: dict[str, str], language: str) -> str:
    pieces = [
        image_context.get("scene", ""),
        image_context.get("setup", ""),
        image_context.get("friction", ""),
        image_context.get("adjustment", ""),
    ]
    pieces = [piece.strip() for piece in pieces if piece and piece.strip()]
    if not pieces:
        return ""
    separator = " " if language == "en" else " "
    return separator.join(pieces)


def _detect_red_flags(normalized_text: str, issue_key: str, duration: str, intensity: str, conditions: list[str]) -> list[str]:
    flags: list[str] = []
    lang = "en"
    for rule in RED_FLAG_RULES:
        if any(term in normalized_text for term in rule["terms"]):
            flags.append(rule[lang])
    if issue_key == "cat_litter_box" and duration == "sudden":
        flags.append("Possible urinary or pain-related change with litter behavior.")
    if intensity == "high" and ("senior_pet" in conditions or "pain_or_mobility" in conditions) and duration == "sudden":
        flags.append("High-intensity sudden change in a senior or painful pet needs medical rule-out.")
    return flags


def _translate_red_flags(flags: list[str], language: str) -> list[str]:
    if language == "en":
        return flags
    translated: list[str] = []
    for flag in flags:
        translated.append(
            {
                "Possible urinary or pain-related change with litter behavior.": "Поведение вокруг лотка может быть связано с болью или проблемой мочеиспускания.",
                "High-intensity sudden change in a senior or painful pet needs medical rule-out.": "Резкое сильное изменение у пожилого питомца или питомца с болью нужно сначала исключать по медицине.",
            }.get(flag, flag)
        )
    return translated


def extract_behavior_context_from_image(
    image_bytes: bytes,
    mime_type: str | None,
    language: str = "en",
) -> dict[str, str] | None:
    if not has_openai_key():
        return None

    client = OpenAI()
    lang = _language_code(language)
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    prompt = (
        "You are reading a photo of a pet setup for a pet behavior coaching app. "
        "Return strict JSON with keys: scene, setup, friction, adjustment. "
        "Each value should be a short sentence. Focus on environment clues, not medical diagnosis. "
        f"Write the sentences in {'Russian' if lang == 'ru' else 'English'}."
    )

    try:
        response = client.responses.create(
            model=MODEL_NAME,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:{mime_type or 'image/png'};base64,{image_b64}"},
                    ],
                }
            ],
        )
        raw_text = getattr(response, "output_text", "") or ""
        parsed = _extract_json_object(raw_text) or {}
        scene = str(parsed.get("scene", "")).strip()
        setup = str(parsed.get("setup", "")).strip()
        friction = str(parsed.get("friction", "")).strip()
        adjustment = str(parsed.get("adjustment", "")).strip()
        if not any([scene, setup, friction, adjustment]):
            return None
        return {
            "scene": scene,
            "setup": setup,
            "friction": friction,
            "adjustment": adjustment,
            "summary": _image_summary_text(
                {"scene": scene, "setup": setup, "friction": friction, "adjustment": adjustment},
                lang,
            ),
        }
    except Exception:
        return None


def _confidence_bucket(description: str, issue_key: str, image_context: dict[str, str] | None) -> int:
    score = 1
    if len((description or "").strip()) > 40:
        score += 1
    if issue_key != "not_sure":
        score += 1
    if image_context and image_context.get("summary"):
        score += 1
    return 3 if score >= 4 else 2 if score >= 2 else 1


def _dynamic_driver_notes(
    when_happens: str,
    conditions: list[str],
    triggers: str,
    language: str,
) -> list[str]:
    notes: list[str] = []
    trigger_text = (triggers or "").strip()
    if when_happens == "home_alone":
        notes.append(
            "Early departure cues may be the real start of the problem."
            if language == "en"
            else "Настоящий старт проблемы может начинаться уже на ранних сигналах ухода."
        )
    if when_happens == "guests":
        notes.append(
            "The social picture may be too fast or too crowded."
            if language == "en"
            else "Социальная картина может быть слишком быстрой или слишком плотной."
        )
    if when_happens == "walks":
        notes.append(
            "Outdoor distance and pace may matter more than more repetition."
            if language == "en"
            else "На улице дистанция и темп могут быть важнее, чем лишние повторы."
        )
    if "noise_sensitivity" in conditions:
        notes.append(
            "Noise sensitivity can keep recovery slow even after the trigger is gone."
            if language == "en"
            else "Чувствительность к шуму может замедлять восстановление даже после исчезновения триггера."
        )
    if "multi_pet_home" in conditions:
        notes.append(
            "Resource access and tension with other pets may be part of the picture."
            if language == "en"
            else "Часть проблемы может быть связана с доступом к ресурсам и напряжением между питомцами."
        )
    if "recent_adoption" in conditions or "rescue_history" in conditions:
        notes.append(
            "Transition history can make threshold building slower than expected."
            if language == "en"
            else "История адаптации может делать выстраивание устойчивости медленнее, чем ожидается."
        )
    if trigger_text:
        notes.append(
            (
                f"Known triggers already mentioned: {trigger_text}."
                if language == "en"
                else f"Уже отмеченные триггеры: {trigger_text}."
            )
        )
    return notes


def _dynamic_today_steps(
    intensity: str,
    when_happens: str,
    conditions: list[str],
    language: str,
) -> list[str]:
    steps: list[str] = []
    if intensity == "high":
        steps.append(
            "Make today easier than usual. Prevent a full rehearsal if you can."
            if language == "en"
            else "Сделай сегодняшний день легче обычного. По возможности не допускай полного повторения проблемы."
        )
    if when_happens == "night":
        steps.append(
            "Keep the late evening lower-stimulation and more predictable."
            if language == "en"
            else "Сделай поздний вечер менее стимулирующим и более предсказуемым."
        )
    if when_happens == "car":
        steps.append(
            "Practice around the vehicle without turning every rep into a full trip."
            if language == "en"
            else "Потренируйся рядом с машиной, не превращая каждый повтор в полноценную поездку."
        )
    if "pain_or_mobility" in conditions or "senior_pet" in conditions:
        steps.append(
            "Watch closely for stiffness, hesitation, or pain-linked changes during the hard moment."
            if language == "en"
            else "Внимательно смотри на скованность, заминки и признаки боли в сложный момент."
        )
    return steps


def _dynamic_week_steps(duration: str, language: str) -> list[str]:
    if duration == "months":
        return [
            "Expect steadier progress from structure and repetition than from one big trick."
            if language == "en"
            else "Ожидай более ровный прогресс от структуры и повторения, а не от одного большого приема."
        ]
    if duration == "sudden":
        return [
            "Because this changed suddenly, log any appetite, sleep, bathroom, or movement changes too."
            if language == "en"
            else "Раз изменение началось резко, отмечай еще аппетит, сон, туалет и изменения движения."
        ]
    return []


def _vet_first_plan(language: str) -> tuple[list[str], list[str], list[str]]:
    if language == "ru":
        return (
            [
                "Пока не усложняй тренировки и не провоцируй проблемную ситуацию специально.",
                "Собери короткую заметку: когда началось, что изменилось, есть ли боль, еда, туалет, сон.",
                "Если есть выраженные симптомы или невозможность помочиться, действуй как в срочной ситуации.",
            ],
            [
                "Сначала исключи медицинскую причину, а уже потом строй полноценный поведенческий план.",
                "После проверки у врача вернись к более мягкой поведенческой структуре и логам наблюдений.",
            ],
            [
                "Если есть кровь, боль, сильное натуживание, коллапс, судороги, сильная одышка или резкое ухудшение — нужна быстрая помощь.",
            ],
        )
    return (
        [
            "Pause hard training setups and do not intentionally trigger the full problem today.",
            "Write down when this started, what changed, and whether appetite, sleep, bathroom habits, or mobility changed too.",
            "Treat inability to urinate or severe medical signs as urgent.",
        ],
        [
            "Rule out the medical piece first, then rebuild a gentler behavior plan from there.",
            "After medical rule-out, return to short low-pressure reps and clearer observation notes.",
        ],
        [
            "Blood, pain, severe straining, collapse, seizures, breathing trouble, or sudden rapid decline deserve urgent help.",
        ],
    )


def analyze_behavior(
    *,
    pet_name: str,
    species: str,
    age_years: float,
    weight_lb: float,
    breed: str,
    triggers: str,
    conditions: list[str],
    issue_key: str,
    description: str,
    when_happens: str,
    intensity: str,
    duration: str,
    already_tried: str,
    image_context: dict[str, str] | None = None,
    language: str = "en",
) -> dict[str, Any]:
    lang = _language_code(language)
    issue = _issue_definition(issue_key, species)
    pet_display = _pet_name_or_default(pet_name, lang)
    normalized_text = _normalize_text(" ".join(filter(None, [description, already_tried, triggers, breed])))
    red_flags = _detect_red_flags(normalized_text, issue_key, duration, intensity, conditions)

    drivers = list(_localized(issue["drivers"], lang))
    drivers.extend(_dynamic_driver_notes(when_happens, conditions, triggers, lang))

    today_steps = list(_localized(issue["today"], lang))
    today_steps.extend(_dynamic_today_steps(intensity, when_happens, conditions, lang))

    week_plan = list(_localized(issue["week"], lang))
    week_plan.extend(_dynamic_week_steps(duration, lang))

    vet_flags = list(_localized(issue["vet"], lang))
    if image_context and image_context.get("adjustment"):
        today_steps.append(str(image_context["adjustment"]).strip())

    detected_signals = [
        issue_display_label(issue_key, species, lang),
        _localized(WHEN_LABELS, lang).get(when_happens, when_happens),
        _localized(INTENSITY_LABELS, lang).get(intensity, intensity),
        _localized(DURATION_LABELS, lang).get(duration, duration),
    ]
    detected_signals.extend(_localized(CONDITION_LABELS, lang).get(item, item) for item in conditions)

    severity_score = 0
    severity_score += 2 if intensity == "high" else 1 if intensity == "medium" else 0
    severity_score += 1 if duration in {"weeks", "months"} else 0
    severity_score += 1 if issue_key in {"separation_anxiety", "barking_reactivity", "cat_litter_box"} else 0
    severity_score += 1 if any(item in conditions for item in ("noise_sensitivity", "multi_pet_home", "recent_adoption")) else 0

    if red_flags:
        verdict = "avoid"
        badge_label = BADGE_LABELS[lang]["avoid"]
        result_title = (
            "Medical or pain rule-out comes first"
            if lang == "en"
            else "Сначала исключаем медицину и боль"
        )
        summary = (
            f"{pet_display.capitalize()} may be showing a behavior problem with a medical layer underneath. "
            "This is the point to slow down training pressure and rule out pain, urinary issues, or illness first."
            if lang == "en"
            else f"У {pet_display} поведенческая картина может идти вместе с медицинской причиной. "
            "На этом этапе лучше снизить тренировочное давление и сначала исключить боль, проблемы с мочеиспусканием или болезнь."
        )
        today_steps, week_plan, urgent_vet = _vet_first_plan(lang)
        vet_flags = _translate_red_flags(red_flags, lang) + urgent_vet
        toolkit_items = _build_toolkit(issue.get("toolkit", {}).get(species, []), species, lang)[:2]
        confidence_bucket = _confidence_bucket(description, issue_key, image_context)
    else:
        if severity_score >= 4:
            verdict = "caution"
            badge_label = BADGE_LABELS[lang]["priority"]
        elif severity_score >= 2:
            verdict = "caution"
            badge_label = BADGE_LABELS[lang]["caution"]
        else:
            verdict = "safe"
            badge_label = BADGE_LABELS[lang]["safe"]

        result_title = str(_localized(issue["pattern"], lang))
        summary = (
            f"For {pet_display}, this most closely fits {str(_localized(issue['label'], lang)).lower()}. "
            + str(_localized(issue["summary"], lang))
            if lang == "en"
            else f"Для {pet_display} это больше всего похоже на сценарий «{str(_localized(issue['label'], lang)).lower()}». "
            + str(_localized(issue["summary"], lang))
        )
        if already_tried.strip():
            summary += (
                " The good next move is not to try harder, but to make the setup clearer."
                if lang == "en"
                else " Следующий хороший шаг — не давить сильнее, а сделать саму ситуацию понятнее."
            )
        confidence_bucket = _confidence_bucket(description, issue_key, image_context)
        toolkit_keys = issue.get("toolkit", {}).get(species, [])
        toolkit_items = _build_toolkit(toolkit_keys, species, lang)

    if image_context and image_context.get("summary"):
        detected_signals.append(
            "Photo setup reviewed" if lang == "en" else "Фото окружения разобрано"
        )

    return {
        "verdict": verdict,
        "badge_label": badge_label,
        "result_title": result_title,
        "summary": summary,
        "drivers_title": "What may be driving it" if lang == "en" else "Что может это усиливать",
        "drivers": drivers,
        "today_title": "What to try today" if lang == "en" else "Что попробовать сегодня",
        "today_steps": today_steps,
        "week_title": "7-day plan" if lang == "en" else "План на 7 дней",
        "week_plan": week_plan,
        "vet_title": "When to call your vet or trainer" if lang == "en" else "Когда звать ветеринара или тренера",
        "vet_flags": vet_flags,
        "toolkit_title": "Helpful setup ideas" if lang == "en" else "Полезные вещи и настройки",
        "toolkit_items": toolkit_items,
        "image_summary": image_context.get("summary", "") if image_context else "",
        "issue_label": issue_display_label(issue_key, species, lang),
        "confidence": CONFIDENCE_LABELS[lang][confidence_bucket],
        "detected_signals": [signal for signal in detected_signals if signal],
        "presentation_mode": "behavior_coach",
        "pet_name": pet_display,
    }


def answer_follow_up(question: str, analysis: dict[str, Any], language: str = "en") -> str:
    lang = _language_code(language)
    normalized = _normalize_text(question)

    if has_openai_key():
        client = OpenAI()
        prompt = (
            "You are a calm pet behavior coach. Answer the user's follow-up using only the supplied context. "
            "Do not diagnose. Keep it practical and brief. "
            f"Write in {'Russian' if lang == 'ru' else 'English'}.\n\n"
            f"Context: {json.dumps(analysis, ensure_ascii=False)}\n"
            f"Question: {question}"
        )
        try:
            response = client.responses.create(model=MODEL_NAME, input=prompt)
            output = getattr(response, "output_text", "") or ""
            if output.strip():
                return output.strip()
        except Exception:
            pass

    if any(word in normalized for word in ["vet", "trainer", "врач", "вет", "тренер"]):
        prefix = "Watch for this: " if lang == "en" else "Смотри вот за чем: "
        return prefix + " ".join(analysis.get("vet_flags", [])[:2])
    if any(word in normalized for word in ["today", "start", "сегодня", "начать", "с чего"]):
        prefix = "Start here: " if lang == "en" else "Начни вот с этого: "
        return prefix + " ".join(analysis.get("today_steps", [])[:2])
    if any(word in normalized for word in ["week", "progress", "сколько", "когда", "прогресс", "недел"]):
        prefix = "For the next week: " if lang == "en" else "На ближайшую неделю: "
        return prefix + " ".join(analysis.get("week_plan", [])[:2])
    if any(word in normalized for word in ["buy", "tool", "product", "что купить", "вещ", "товар"]):
        toolkit = analysis.get("toolkit_items", [])
        if toolkit:
            titles = ", ".join(item["title"] for item in toolkit[:3])
            return (
                f"I would start with: {titles}."
                if lang == "en"
                else f"Я бы начал с этого: {titles}."
            )

    return (
        f"The short version: {analysis.get('summary', '')} Start with {analysis.get('today_steps', ['one calmer easier rep'])[0]}"
        if lang == "en"
        else f"Коротко: {analysis.get('summary', '')} Начни с этого: {analysis.get('today_steps', ['одного более спокойного повтора'])[0]}"
    )


def get_routine_guide(profile: dict[str, Any], language: str = "en") -> dict[str, Any]:
    lang = _language_code(language)
    species = profile.get("species", "dog")
    age_years = float(profile.get("age_years") or 0)
    conditions = profile.get("conditions", []) or []
    triggers = (profile.get("triggers") or "").strip()

    if species == "cat":
        sections = [
            {
                "title": "Morning reset" if lang == "en" else "Утро",
                "items": [
                    "Start with a short play-hunt-eat sequence."
                    if lang == "en"
                    else "Начинай утро с короткой цепочки игра-охота-еда.",
                    "Check litter boxes before the house gets busy."
                    if lang == "en"
                    else "Проверь лотки до того, как дом станет шумным.",
                ],
            },
            {
                "title": "Daytime stability" if lang == "en" else "День",
                "items": [
                    "Keep vertical space and quiet retreat spots available."
                    if lang == "en"
                    else "Держи доступными вертикальные точки и тихие места для укрытия.",
                    "Scatter calm interaction through the day instead of one big social push."
                    if lang == "en"
                    else "Распредели спокойный контакт по дню вместо одного большого социального напора.",
                ],
            },
            {
                "title": "Evening settle" if lang == "en" else "Вечер",
                "items": [
                    "Use a final low-key play burst before dinner or bedtime."
                    if lang == "en"
                    else "Используй последнюю спокойную игровую вспышку перед ужином или сном.",
                    "Protect a quiet wind-down hour."
                    if lang == "en"
                    else "Сохрани тихий час на завершение дня.",
                ],
            },
        ]
    else:
        sections = [
            {
                "title": "Morning reset" if lang == "en" else "Утро",
                "items": [
                    "Start with sniffing and calm movement before asking for precision."
                    if lang == "en"
                    else "Начинай день с нюхания и спокойного движения до точных задач.",
                    "Use one easy win early so the day starts successful."
                    if lang == "en"
                    else "Дай одну простую успешную задачу в начале дня.",
                ],
            },
            {
                "title": "Midday outlet" if lang == "en" else "День",
                "items": [
                    "Mix decompression with one short training rep, not a marathon session."
                    if lang == "en"
                    else "Смешивай декомпрессию с одним коротким повтором обучения, а не с марафоном.",
                    "Offer a legal chew, lick, or forage task before restless hours."
                    if lang == "en"
                    else "Предлагай разрешенное жевание, облизывание или поиск еды до беспокойных часов.",
                ],
            },
            {
                "title": "Evening settle" if lang == "en" else "Вечер",
                "items": [
                    "Lower stimulation in the last hour and keep the pattern predictable."
                    if lang == "en"
                    else "Снижай стимуляцию в последний час и делай рутину предсказуемой.",
                    "Measure success by easier settling, not by complete stillness."
                    if lang == "en"
                    else "Смотри на более легкое успокоение, а не на полную неподвижность.",
                ],
            },
        ]

    weekly_focus = [
        "Track what happens right before the behavior and how long recovery takes."
        if lang == "en"
        else "Отмечай, что происходит прямо перед поведением и сколько длится восстановление.",
        "Change one variable at a time so the pattern stays readable."
        if lang == "en"
        else "Меняй по одному параметру за раз, чтобы паттерн оставался понятным.",
    ]

    if age_years >= 8 or "senior_pet" in conditions:
        weekly_focus.append(
            "Because this is a senior pet, watch for pain, stiffness, sleep shifts, and sudden confusion."
            if lang == "en"
            else "Так как питомец пожилой, следи за болью, скованностью, изменением сна и внезапной спутанностью."
        )
    if "noise_sensitivity" in conditions:
        weekly_focus.append(
            "Build in quieter recovery windows after noisy parts of the day."
            if lang == "en"
            else "После шумных частей дня закладывай более тихие окна для восстановления."
        )
    if "multi_pet_home" in conditions:
        weekly_focus.append(
            "Check whether tension rises around doors, food, beds, or owner attention."
            if lang == "en"
            else "Проверь, не растет ли напряжение возле дверей, еды, лежанок или внимания хозяина."
        )
    if triggers:
        weekly_focus.append(
            f"Known triggers to design around: {triggers}."
            if lang == "en"
            else f"Триггеры, которые уже стоит учитывать в плане: {triggers}."
        )

    return {
        "title": "Routine plan" if lang == "en" else "Рутинный план",
        "summary": (
            "Use this as a calmer baseline and then layer issue-specific coaching on top."
            if lang == "en"
            else "Используй это как спокойную базу, а сверху уже добавляй точечный поведенческий план."
        ),
        "sections": sections,
        "weekly_title": "Weekly focus" if lang == "en" else "Фокус недели",
        "weekly_focus": weekly_focus,
    }
