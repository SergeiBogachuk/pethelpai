from __future__ import annotations

import base64
import os
import re
from typing import Any

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional at runtime
    OpenAI = None


MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

RUSSIAN_TERM_MAP = {
    "шоколад": "chocolate",
    "какао": "cocoa",
    "ксилит": "xylitol",
    "сахарозаменитель": "sugar free sweetener",
    "жвачка": "gum",
    "виноград": "grapes",
    "изюм": "raisins",
    "лук": "onion",
    "чеснок": "garlic",
    "зеленый лук": "chives",
    "макадамия": "macadamia nuts",
    "алкоголь": "alcohol",
    "пиво": "beer",
    "вино": "wine",
    "кофе": "coffee",
    "чай": "tea",
    "кофеин": "caffeine",
    "тесто": "dough",
    "дрожжевое тесто": "yeast dough",
    "каннабис": "cannabis",
    "марихуана": "marijuana",
    "тгк": "thc",
    "обезболивающее": "pain medicine",
    "ибупрофен": "ibuprofen",
    "тайленол": "tylenol",
    "адвил": "advil",
    "кость": "bone",
    "кости": "bones",
    "початок": "corn cob",
    "косточка": "fruit pit",
    "пицца": "pizza",
    "бургер": "burger",
    "картошка фри": "fries",
    "мороженое": "ice cream",
    "сыр": "cheese",
    "яйцо": "egg",
    "яйца": "eggs",
    "вареное яйцо": "boiled egg",
    "омлет": "scrambled egg",
    "йогурт": "yogurt",
    "печенье": "cookie",
    "торт": "cake",
    "пончик": "donut",
    "конфета": "candy",
    "острый": "spicy",
    "острая еда": "spicy food",
    "сырое мясо": "raw meat",
    "сырая рыба": "raw fish",
    "сырое яйцо": "raw egg",
    "авокадо": "avocado",
    "арахисовая паста": "peanut butter",
    "курица": "chicken",
    "индейка": "turkey",
    "тыква": "pumpkin",
    "рис": "rice",
    "морковь": "carrot",
    "огурец": "cucumber",
    "черника": "blueberries",
    "голубика": "blueberries",
    "корм": "pet food",
    "лакомство": "treat",
    "лакомства": "treats",
}

LABEL_TRANSLATIONS_RU = {
    "Chocolate": "Шоколад",
    "Xylitol or sugar-free sweetener": "Ксилит или сахарозаменитель",
    "Grapes or raisins": "Виноград или изюм",
    "Onion, garlic, or chives": "Лук, чеснок или шнитт-лук",
    "Macadamia nuts": "Орехи макадамия",
    "Alcohol": "Алкоголь",
    "Caffeine": "Кофеин",
    "Raw dough or yeast dough": "Сырое или дрожжевое тесто",
    "THC or cannabis edible": "Каннабис или THC-продукт",
    "Human pain medicine": "Человеческое обезболивающее",
    "Cooked bones or bone fragments": "Вареные кости или костные осколки",
    "Corn cob or fruit pit": "Кукурузный початок или фруктовая косточка",
    "Fatty or fried food": "Жирная или жареная еда",
    "Dairy-heavy food": "Много молочных продуктов",
    "Salty or heavily seasoned food": "Соленая или сильно приправленная еда",
    "Sugary dessert": "Сладкий десерт",
    "Spicy food": "Острая еда",
    "Raw meat, fish, or egg": "Сырое мясо, рыба или яйцо",
    "Avocado flesh": "Мякоть авокадо",
    "Peanut butter": "Арахисовая паста",
    "Plain cooked chicken": "Простая приготовленная курица",
    "Plain cooked turkey": "Простая приготовленная индейка",
    "Plain cooked egg": "Простое приготовленное яйцо",
    "Plain pumpkin": "Простая тыква",
    "Plain white rice": "Простой белый рис",
    "Carrots or cucumber": "Морковь или огурец",
    "Blueberries": "Черника или голубика",
    "Commercial pet food or treats": "Готовый корм или лакомства для питомцев",
}

REASON_TRANSLATIONS_RU = {
    "Chocolate can affect the heart and nervous system.": "Шоколад может влиять на сердце и нервную систему.",
    "Xylitol can cause a dangerous blood sugar drop and liver injury in dogs.": "Ксилит может вызвать опасное падение сахара и повреждение печени у собак.",
    "Grapes and raisins can cause severe kidney injury in some pets.": "Виноград и изюм могут вызывать тяжелое поражение почек у некоторых питомцев.",
    "These ingredients can damage red blood cells and trigger anemia.": "Эти ингредиенты могут повреждать эритроциты и вызывать анемию.",
    "Macadamias can cause weakness, tremors, and walking changes in dogs.": "Макадамия может вызывать слабость, тремор и нарушение походки у собак.",
    "Alcohol can rapidly depress the nervous system.": "Алкоголь может быстро угнетать нервную систему.",
    "Caffeine can overstimulate the heart and nervous system.": "Кофеин может чрезмерно стимулировать сердце и нервную систему.",
    "Dough can expand in the stomach and also create alcohol as it ferments.": "Тесто может увеличиваться в желудке и выделять алкоголь при брожении.",
    "Cannabis edibles can cause dangerous neurologic signs in pets.": "Продукты с каннабисом могут вызывать опасные неврологические симптомы у питомцев.",
    "Many human pain relievers are dangerous or toxic for pets.": "Многие человеческие обезболивающие опасны или токсичны для питомцев.",
    "Cooked bones can splinter and cause choking or internal injury.": "Вареные кости могут раскалываться и вызывать удушье или внутренние травмы.",
    "Large hard items can lodge in the stomach or intestines.": "Крупные твердые предметы могут застрять в желудке или кишечнике.",
    "Rich foods can trigger stomach upset and sometimes pancreatitis.": "Жирная и богатая еда может вызывать расстройство желудка и иногда панкреатит.",
    "Many pets do not digest dairy well and can develop GI upset.": "Многие питомцы плохо переваривают молочные продукты и могут получить расстройство ЖКТ.",
    "A lot of salt and seasoning can upset the stomach and stress sensitive pets.": "Избыток соли и приправ может раздражать желудок и хуже переноситься чувствительными питомцами.",
    "Sugary desserts add little value and often hide richer or unsafe ingredients.": "Сладкие десерты не несут пользы и часто содержат более тяжелые или небезопасные ингредиенты.",
    "Spicy foods can irritate the stomach and mouth.": "Острая еда может раздражать желудок и ротовую полость.",
    "Raw foods can carry bacteria or parasites, especially for vulnerable pets.": "Сырые продукты могут содержать бактерии или паразитов, особенно опасные для уязвимых питомцев.",
    "Small amounts of plain avocado flesh are not always an emergency, but it is rich and can upset the stomach.": "Небольшое количество чистой мякоти авокадо не всегда экстренная ситуация, но продукт жирный и может раздражать желудок.",
    "Peanut butter may be okay, but the ingredient label must be checked for xylitol and excess sugar.": "Арахисовая паста иногда допустима, но нужно проверить состав на ксилит и избыток сахара.",
    "Plain cooked chicken is often tolerated well in small portions.": "Простая приготовленная курица часто переносится хорошо в небольших порциях.",
    "Lean unseasoned turkey is usually a safer protein choice.": "Нежирная индейка без приправ обычно безопаснее как белковый вариант.",
    "Plain cooked egg can work as a small protein add-on when it is fully cooked and unseasoned.": "Простое полностью приготовленное яйцо без приправ может подойти как небольшая белковая добавка.",
    "Plain pumpkin is commonly used in small amounts for gentle digestion support.": "Простая тыква часто используется в небольших количествах для мягкой поддержки пищеварения.",
    "Plain rice is bland and usually low risk in modest portions.": "Простой рис мягкий для желудка и обычно имеет низкий риск в умеренных порциях.",
    "These are low-fat snack options when served plain and bite-sized.": "Это нежирные варианты перекуса, если давать их без добавок и маленькими кусочками.",
    "Blueberries are usually fine in small amounts for many pets.": "Голубика обычно допустима в небольших количествах для многих питомцев.",
    "Commercial pet foods are made for pets and are generally the safer baseline choice.": "Готовые корма и лакомства для питомцев обычно безопаснее как базовый вариант.",
    "A history of pancreatitis makes rich or greasy foods more risky.": "При панкреатите в анамнезе жирная и тяжелая еда становится более рискованной.",
    "Kidney disease is a reason to be stricter with salty or heavily seasoned foods.": "При заболевании почек стоит строже относиться к соленой и сильно приправленной еде.",
    "For diabetic pets, sugary foods are a poor fit even when they are not classic toxins.": "Для питомцев с диабетом сладкая еда нежелательна, даже если это не классический токсин.",
    "The amount matters. Bigger portions create more risk than a tiny lick or crumb.": "Количество имеет значение. Большая порция несет больше риска, чем маленький lick или крошка.",
    "Current symptoms already include emergency warning signs.": "Среди текущих симптомов уже есть тревожные экстренные признаки.",
    "Current symptoms raise the level of concern above a routine treat question.": "Текущие симптомы делают ситуацию более серьезной, чем обычный вопрос про угощение.",
}

SYMPTOM_TRANSLATIONS_RU = {
    "vomiting": "рвота",
    "restlessness": "беспокойство",
    "rapid heart rate": "частый пульс",
    "tremors": "тремор",
    "weakness": "слабость",
    "collapse": "коллапс",
    "seizures": "судороги",
    "lethargy": "вялость",
    "poor appetite": "плохой аппетит",
    "increased thirst": "сильная жажда",
    "pale gums": "бледные десны",
    "fast breathing": "частое дыхание",
    "stiffness": "скованность",
    "stumbling": "шаткость",
    "slow breathing": "замедленное дыхание",
    "agitation": "возбуждение",
    "panting": "частое дыхание с открытым ртом",
    "bloating": "вздутие",
    "retching": "позывы на рвоту",
    "pain": "боль",
    "dribbling urine": "подтекание мочи",
    "stomach pain": "боль в животе",
    "abdominal pain": "боль в животе",
    "gagging": "рвотные позывы",
    "trouble swallowing": "трудности с глотанием",
    "diarrhea": "диарея",
    "gas": "газы",
    "stomach discomfort": "дискомфорт в животе",
    "thirst": "жажда",
    "drooling": "слюнотечение",
    "pawing at mouth": "трение лапой по морде",
    "fever": "температура",
}

ALTERNATIVE_TRANSLATIONS_RU = {
    "plain cooked chicken or turkey": "простая приготовленная курица или индейка",
    "a small spoon of plain pumpkin": "небольшая ложка простой тыквы",
    "commercial cat treats with simple ingredients": "готовые кошачьи лакомства с простым составом",
    "carrot slices or cucumber pieces": "кусочки моркови или огурца",
    "commercial dog treats with short ingredient lists": "готовые собачьи лакомства с коротким составом",
}

VALUE_TRANSLATIONS_RU = {
    "Lick or crumb": "лизок или крошка",
    "Small bite": "маленький кусочек",
    "Moderate portion": "средняя порция",
    "Large portion": "большая порция",
    "Within 30 minutes": "в течение 30 минут",
    "30 minutes to 2 hours": "от 30 минут до 2 часов",
    "2 to 6 hours ago": "2–6 часов назад",
    "More than 6 hours ago": "больше 6 часов назад",
}

HIGH_RISK_RULES = [
    {
        "label": "Chocolate",
        "keywords": ["chocolate", "cocoa", "cacao", "brownie", "chocolate chip", "nutella"],
        "species": ["dog", "cat"],
        "category": "toxin",
        "why": "Chocolate can affect the heart and nervous system.",
        "watch_for": ["vomiting", "restlessness", "rapid heart rate", "tremors"],
    },
    {
        "label": "Xylitol or sugar-free sweetener",
        "keywords": [
            "xylitol",
            "birch sugar",
            "sugar free gum",
            "sugar free candy",
            "sugarless gum",
            "sugarless candy",
        ],
        "species": ["dog"],
        "category": "toxin",
        "why": "Xylitol can cause a dangerous blood sugar drop and liver injury in dogs.",
        "watch_for": ["weakness", "vomiting", "collapse", "seizures"],
    },
    {
        "label": "Grapes or raisins",
        "keywords": ["grape", "grapes", "raisin", "raisins", "currant", "currants"],
        "species": ["dog", "cat"],
        "category": "toxin",
        "why": "Grapes and raisins can cause severe kidney injury in some pets.",
        "watch_for": ["vomiting", "lethargy", "poor appetite", "increased thirst"],
    },
    {
        "label": "Onion, garlic, or chives",
        "keywords": [
            "onion",
            "onion powder",
            "garlic",
            "garlic powder",
            "chive",
            "chives",
            "leek",
            "shallot",
        ],
        "species": ["dog", "cat"],
        "category": "toxin",
        "why": "These ingredients can damage red blood cells and trigger anemia.",
        "watch_for": ["vomiting", "weakness", "pale gums", "fast breathing"],
    },
    {
        "label": "Macadamia nuts",
        "keywords": ["macadamia", "macadamia nuts"],
        "species": ["dog"],
        "category": "toxin",
        "why": "Macadamias can cause weakness, tremors, and walking changes in dogs.",
        "watch_for": ["weakness", "tremors", "vomiting", "stiffness"],
    },
    {
        "label": "Alcohol",
        "keywords": ["alcohol", "beer", "wine", "vodka", "whiskey", "rum", "liqueur"],
        "species": ["dog", "cat"],
        "category": "toxin",
        "why": "Alcohol can rapidly depress the nervous system.",
        "watch_for": ["stumbling", "vomiting", "slow breathing", "collapse"],
    },
    {
        "label": "Caffeine",
        "keywords": ["coffee", "espresso", "caffeine", "energy drink", "tea", "matcha"],
        "species": ["dog", "cat"],
        "category": "toxin",
        "why": "Caffeine can overstimulate the heart and nervous system.",
        "watch_for": ["agitation", "rapid heart rate", "tremors", "panting"],
    },
    {
        "label": "Raw dough or yeast dough",
        "keywords": ["raw dough", "yeast dough", "pizza dough", "bread dough"],
        "species": ["dog", "cat"],
        "category": "toxin",
        "why": "Dough can expand in the stomach and also create alcohol as it ferments.",
        "watch_for": ["bloating", "retching", "pain", "weakness"],
    },
    {
        "label": "THC or cannabis edible",
        "keywords": ["cannabis", "marijuana", "thc", "edible", "weed gummy"],
        "species": ["dog", "cat"],
        "category": "toxin",
        "why": "Cannabis edibles can cause dangerous neurologic signs in pets.",
        "watch_for": ["stumbling", "dribbling urine", "lethargy", "tremors"],
    },
    {
        "label": "Human pain medicine",
        "keywords": ["ibuprofen", "acetaminophen", "tylenol", "advil", "naproxen", "aleve"],
        "species": ["dog", "cat"],
        "category": "toxin",
        "why": "Many human pain relievers are dangerous or toxic for pets.",
        "watch_for": ["vomiting", "stomach pain", "pale gums", "weakness"],
    },
    {
        "label": "Cooked bones or bone fragments",
        "keywords": ["cooked bone", "chicken bone", "turkey bone", "rib bone", "bone fragments"],
        "species": ["dog", "cat"],
        "category": "obstruction",
        "why": "Cooked bones can splinter and cause choking or internal injury.",
        "watch_for": ["gagging", "retching", "abdominal pain", "trouble swallowing"],
    },
    {
        "label": "Corn cob or fruit pit",
        "keywords": ["corn cob", "peach pit", "plum pit", "avocado pit", "cherry pit"],
        "species": ["dog", "cat"],
        "category": "obstruction",
        "why": "Large hard items can lodge in the stomach or intestines.",
        "watch_for": ["retching", "vomiting", "bloating", "pain"],
    },
]

CAUTION_RULES = [
    {
        "label": "Fatty or fried food",
        "keywords": [
            "bacon",
            "sausage",
            "fried chicken",
            "pizza",
            "burger",
            "fries",
            "gravy",
            "grease",
            "butter",
            "fat trimmings",
        ],
        "species": ["dog", "cat"],
        "category": "fatty",
        "why": "Rich foods can trigger stomach upset and sometimes pancreatitis.",
        "watch_for": ["vomiting", "diarrhea", "abdominal pain", "lethargy"],
    },
    {
        "label": "Dairy-heavy food",
        "keywords": ["milk", "ice cream", "cream", "cheese", "whipped cream", "yogurt"],
        "species": ["dog", "cat"],
        "category": "dairy",
        "why": "Many pets do not digest dairy well and can develop GI upset.",
        "watch_for": ["gas", "vomiting", "diarrhea", "stomach discomfort"],
    },
    {
        "label": "Salty or heavily seasoned food",
        "keywords": [
            "chips",
            "jerky",
            "ramen seasoning",
            "seasoning mix",
            "soy sauce",
            "salty",
            "seasoned fries",
        ],
        "species": ["dog", "cat"],
        "category": "salty",
        "why": "A lot of salt and seasoning can upset the stomach and stress sensitive pets.",
        "watch_for": ["vomiting", "thirst", "restlessness", "diarrhea"],
    },
    {
        "label": "Sugary dessert",
        "keywords": ["cookie", "cake", "donut", "frosting", "candy", "marshmallow", "syrup"],
        "species": ["dog", "cat"],
        "category": "sweet",
        "why": "Sugary desserts add little value and often hide richer or unsafe ingredients.",
        "watch_for": ["vomiting", "diarrhea", "restlessness", "poor appetite"],
    },
    {
        "label": "Spicy food",
        "keywords": ["hot sauce", "jalapeno", "buffalo sauce", "spicy", "chili", "taco seasoning"],
        "species": ["dog", "cat"],
        "category": "spicy",
        "why": "Spicy foods can irritate the stomach and mouth.",
        "watch_for": ["drooling", "vomiting", "diarrhea", "pawing at mouth"],
    },
    {
        "label": "Raw meat, fish, or egg",
        "keywords": ["raw egg", "raw meat", "raw fish", "sushi", "tartare", "ceviche"],
        "species": ["dog", "cat"],
        "category": "raw",
        "why": "Raw foods can carry bacteria or parasites, especially for vulnerable pets.",
        "watch_for": ["vomiting", "diarrhea", "fever", "poor appetite"],
    },
    {
        "label": "Avocado flesh",
        "keywords": ["avocado", "guacamole"],
        "species": ["dog", "cat"],
        "category": "fatty",
        "why": "Small amounts of plain avocado flesh are not always an emergency, but it is rich and can upset the stomach.",
        "watch_for": ["vomiting", "diarrhea", "abdominal pain", "poor appetite"],
    },
    {
        "label": "Peanut butter",
        "keywords": ["peanut butter"],
        "species": ["dog", "cat"],
        "category": "label_check",
        "why": "Peanut butter may be okay, but the ingredient label must be checked for xylitol and excess sugar.",
        "watch_for": ["vomiting", "weakness", "diarrhea", "restlessness"],
    },
]

SAFE_RULES = [
    {
        "label": "Plain cooked chicken",
        "keywords": ["plain chicken", "boiled chicken", "unseasoned chicken", "cooked chicken breast"],
        "species": ["dog", "cat"],
        "why": "Plain cooked chicken is often tolerated well in small portions.",
    },
    {
        "label": "Plain cooked turkey",
        "keywords": ["plain turkey", "unseasoned turkey", "cooked turkey breast"],
        "species": ["dog", "cat"],
        "why": "Lean unseasoned turkey is usually a safer protein choice.",
    },
    {
        "label": "Plain cooked egg",
        "keywords": ["plain egg", "boiled egg", "cooked egg", "scrambled egg", "hard boiled egg"],
        "species": ["dog", "cat"],
        "why": "Plain cooked egg can work as a small protein add-on when it is fully cooked and unseasoned.",
    },
    {
        "label": "Plain pumpkin",
        "keywords": ["plain pumpkin", "pumpkin puree", "100 pumpkin"],
        "species": ["dog", "cat"],
        "why": "Plain pumpkin is commonly used in small amounts for gentle digestion support.",
    },
    {
        "label": "Plain white rice",
        "keywords": ["plain rice", "white rice", "boiled rice"],
        "species": ["dog", "cat"],
        "why": "Plain rice is bland and usually low risk in modest portions.",
    },
    {
        "label": "Carrots or cucumber",
        "keywords": ["carrot", "carrots", "cucumber", "cucumbers"],
        "species": ["dog", "cat"],
        "why": "These are low-fat snack options when served plain and bite-sized.",
    },
    {
        "label": "Blueberries",
        "keywords": ["blueberry", "blueberries"],
        "species": ["dog", "cat"],
        "why": "Blueberries are usually fine in small amounts for many pets.",
    },
    {
        "label": "Commercial pet food or treats",
        "keywords": ["dog food", "cat food", "dog treat", "cat treat", "kibble"],
        "species": ["dog", "cat"],
        "why": "Commercial pet foods are made for pets and are generally the safer baseline choice.",
    },
]

SEVERE_SYMPTOMS = {
    "trouble breathing",
    "collapse",
    "seizure",
    "seizures",
    "bloated abdomen",
    "can not keep water down",
}

MODERATE_SYMPTOMS = {
    "vomiting",
    "diarrhea",
    "drooling",
    "lethargy",
    "tremors",
    "stumbling",
    "poor appetite",
    "restlessness",
    "pale gums",
}


def has_openai_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY")) and OpenAI is not None


def _language_code(language: str = "en") -> str:
    return "ru" if str(language or "").lower().startswith("ru") else "en"


def _normalize_text(value: str) -> str:
    clean = re.sub(r"[^a-zа-яё0-9]+", " ", (value or "").lower())
    return re.sub(r"\s+", " ", clean).strip()


def _augment_multilingual_text(value: str) -> str:
    lowered = (value or "").lower()
    additions: list[str] = []

    for source, target in RUSSIAN_TERM_MAP.items():
        if source in lowered:
            additions.append(target)

    if additions:
        return f"{value} {' '.join(additions)}"
    return value


def _localize_label(label: str, language: str = "en") -> str:
    if _language_code(language) == "ru":
        return LABEL_TRANSLATIONS_RU.get(label, label)
    return label


def _localize_reason(reason: str, language: str = "en") -> str:
    if _language_code(language) != "ru":
        return reason
    return REASON_TRANSLATIONS_RU.get(reason, reason)


def _localize_symptom(symptom: str, language: str = "en") -> str:
    if _language_code(language) != "ru":
        return symptom
    return SYMPTOM_TRANSLATIONS_RU.get(symptom.lower(), symptom)


def _localize_alternative(item: str, language: str = "en") -> str:
    if _language_code(language) != "ru":
        return item
    return ALTERNATIVE_TRANSLATIONS_RU.get(item, item)


def _localize_value(value: str, language: str = "en") -> str:
    if _language_code(language) != "ru":
        return value
    return VALUE_TRANSLATIONS_RU.get(value, value)


def _contains_any(text: str, tokens: list[str]) -> bool:
    return any(token in text for token in tokens)


def _keyword_present(text: str, keyword: str) -> bool:
    normalized_keyword = _normalize_text(keyword)
    if not normalized_keyword:
        return False

    pattern = r"\b" + r"\s+".join(re.escape(token) for token in normalized_keyword.split()) + r"\b"
    return re.search(pattern, text) is not None


def _find_rule_matches(text: str, species: str, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []

    for rule in rules:
        if species not in rule["species"]:
            continue

        matched_keywords = [
            keyword for keyword in rule.get("keywords", []) if _keyword_present(text, keyword)
        ]
        if matched_keywords:
            enriched_rule = dict(rule)
            enriched_rule["matched_keywords"] = matched_keywords
            matches.append(enriched_rule)

    return matches


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_items: list[str] = []
    for item in items:
        cleaned = item.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            unique_items.append(cleaned)
    return unique_items


def _join_labels(items: list[str], language: str = "en") -> str:
    language = _language_code(language)
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {'и' if language == 'ru' else 'and'} {items[1]}"
    return f"{', '.join(items[:-1])}, {'и' if language == 'ru' else 'and'} {items[-1]}"


def _coerce_message_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text = item.get("text", "")
                    if text:
                        chunks.append(str(text).strip())
                continue

            item_type = getattr(item, "type", "")
            if item_type == "text":
                text_value = getattr(item, "text", "")
                if text_value:
                    chunks.append(str(text_value).strip())
        return "\n".join(chunks).strip()

    return ""


def extract_food_context_from_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    language: str = "en",
) -> dict[str, str | bool]:
    response_language = "Russian" if _language_code(language) == "ru" else "English"
    if not has_openai_key():
        return {
            "ok": False,
            "summary": "",
            "error": (
                "Добавьте OPENAI_API_KEY, чтобы включить AI-анализ изображения."
                if _language_code(language) == "ru"
                else "Add OPENAI_API_KEY to enable AI image understanding."
            ),
        }

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    encoded = base64.b64encode(image_bytes).decode("ascii")

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You analyze pet food risk from photos. Identify the likely food or product shown, visible "
                        "ingredients or preparation clues, the estimated visible portion, an approximate calorie "
                        "range for the visible portion if possible, and hidden risk cues like chocolate, grapes, "
                        "onion, garlic, xylitol, caffeine, alcohol, bones, or spicy sauces. Be concise, factual, "
                        "and clearly say when something is only an estimate."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"Respond in {response_language} using exactly 5 short lines.\n"
                                "Line 1: Likely item\n"
                                "Line 2: Visible ingredients or preparation\n"
                                "Line 3: Estimated visible portion\n"
                                "Line 4: Estimated calories for the visible portion\n"
                                "Line 5: Pet risk cues for dogs or cats"
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
                        },
                    ],
                },
            ],
        )
        content = _coerce_message_text(response.choices[0].message.content)
        return {"ok": True, "summary": content, "error": ""}
    except Exception as error:  # pragma: no cover - runtime integration only
        return {"ok": False, "summary": "", "error": str(error)}


def _condition_adjustments(
    conditions: set[str], caution_matches: list[dict[str, Any]]
) -> tuple[list[str], int]:
    reasons: list[str] = []
    score_boost = 0
    caution_categories = {match["category"] for match in caution_matches}

    if "pancreatitis" in conditions and "fatty" in caution_categories:
        reasons.append("A history of pancreatitis makes rich or greasy foods more risky.")
        score_boost = max(score_boost, 1)

    if "kidney disease" in conditions and "salty" in caution_categories:
        reasons.append("Kidney disease is a reason to be stricter with salty or heavily seasoned foods.")
        score_boost = max(score_boost, 1)

    if "diabetes" in conditions and "sweet" in caution_categories:
        reasons.append("For diabetic pets, sugary foods are a poor fit even when they are not classic toxins.")
        score_boost = max(score_boost, 1)

    return reasons, score_boost


def _allergy_adjustments(allergy_text: str, normalized_text: str) -> list[str]:
    reasons: list[str] = []
    allergies = [item.strip() for item in re.split(r"[,/]", allergy_text or "") if item.strip()]
    for allergy in allergies:
        if _keyword_present(normalized_text, allergy):
            reasons.append(f"The description appears to include {allergy}, which matches this pet's allergy list.")
    return reasons


def _make_summary(
    verdict: str,
    pet_name: str,
    species: str,
    amount_label: str,
    already_ate: bool,
    match_labels: list[str],
    unknown_item: bool,
    language: str = "en",
) -> str:
    if _language_code(language) == "ru":
        species_word = "собаки" if species == "dog" else "кошки"
        amount_text = _localize_value(amount_label, language).lower()
        match_text = _join_labels([_localize_label(label, language) for label in match_labels], language)

        if verdict == "Avoid":
            if match_text:
                return (
                    f"{pet_name} лучше не давать это. Я вижу риски, связанные с: {match_text}. "
                    f"{'Так как питомец уже это съел, лучше срочно связаться с ветеринаром.' if already_ate else 'Для питомца это плохой выбор в качестве угощения.'}"
                )
            return (
                f"{pet_name} сейчас лучше избегать этого продукта. По сочетанию признаков ситуация "
                f"выглядит серьезнее обычного вопроса про перекус."
            )

        if verdict == "Caution":
            if unknown_item:
                return (
                    f"По одному только описанию я не могу уверенно назвать продукт безопасным. "
                    f"Если {pet_name} уже съел {amount_text}, стоит быть особенно осторожным и наблюдать."
                )
            return (
                f"Это не выглядит как автоматическая экстренная ситуация, но для {species_word} нужна осторожность. "
                f"{'Раз часть уже съедена, особенно важны количество и симптомы.' if already_ate else 'Крошечный кусочек переносится иначе, чем полноценная порция.'}"
            )

        if already_ate:
            return (
                f"По описанию это выглядит относительно низкорисковым для {pet_name}, особенно если количество "
                f"было небольшим и еда была без приправ."
            )
        return f"Для {pet_name} это выглядит относительно безопасным вариантом, если продукт простой и порция маленькая."

    species_word = "dog" if species == "dog" else "cat"
    amount_text = _localize_value(amount_label, language).lower()
    match_text = _join_labels(match_labels, language)

    if verdict == "Avoid":
        if match_text:
            return (
                f"{pet_name} should skip this. I found risk cues for {match_text}. "
                f"{'Because some was already eaten, this needs urgent veterinary guidance.' if already_ate else 'This is not a good treat choice for a pet.'}"
            )
        return (
            f"{pet_name} should avoid this right now. The combination of symptoms or context makes this "
            f"more urgent than a routine snack question."
        )

    if verdict == "Caution":
        if unknown_item:
            return (
                f"I cannot confidently call this pet-safe from the description alone. "
                f"If {pet_name} already had a {amount_text}, use extra caution and watch closely."
            )
        return (
            f"This is not an automatic emergency, but it deserves caution for a {species_word}. "
            f"{'Since some was already eaten, portion size and symptoms matter.' if already_ate else 'A tiny amount may be tolerated better than a full serving.'}"
        )

    if already_ate:
        return (
            f"This looks relatively low risk for {pet_name} based on the description, especially if the amount "
            f"was only a {amount_text} and the food was plain."
        )
    return f"This looks like a relatively safe option for {pet_name} when served plain and in a small portion."


def _is_acute_case(already_ate: bool, severe_hits: list[str], moderate_hits: list[str]) -> bool:
    return already_ate or bool(severe_hits or moderate_hits)


def _coach_portion_hint(weight_lbs: float, caution_level: str, language: str = "en") -> str:
    if caution_level == "avoid":
        return (
            "Я бы не включал это в рацион и не строил вокруг него кормление."
            if _language_code(language) == "ru"
            else "I would not build this into the feeding routine at all."
        )

    if weight_lbs and weight_lbs < 15:
        safe_portion = "1-2 tiny bites"
        caution_portion = "one tiny taste at most"
        safe_portion_ru = "1-2 совсем маленьких кусочка"
        caution_portion_ru = "максимум один маленький вкус"
    elif weight_lbs and weight_lbs < 45:
        safe_portion = "2-4 bite-sized pieces"
        caution_portion = "1-2 bite-sized pieces"
        safe_portion_ru = "2-4 кусочка маленького размера"
        caution_portion_ru = "1-2 маленьких кусочка"
    else:
        safe_portion = "a few bite-sized pieces"
        caution_portion = "1-3 bite-sized pieces"
        safe_portion_ru = "несколько маленьких кусочков"
        caution_portion_ru = "1-3 небольших кусочка"

    if _language_code(language) == "ru":
        return (
            f"Если использовать это как добавку, держи порцию на уровне {safe_portion_ru}."
            if caution_level == "safe"
            else f"Если давать это вообще, то не больше чем {caution_portion_ru}."
        )
    return (
        f"If you use it as an add-on, keep it around {safe_portion}."
        if caution_level == "safe"
        else f"If you offer it at all, cap it around {caution_portion}."
    )


def _coach_copy(
    verdict: str,
    pet_name: str,
    match_labels: list[str],
    toxic_matches: list[dict[str, Any]],
    caution_matches: list[dict[str, Any]],
    weight_lbs: float,
    language: str = "en",
) -> dict[str, Any]:
    match_text = _join_labels([_localize_label(label, language) for label in match_labels], language)
    caution_categories = {match.get("category", "") for match in caution_matches}

    if verdict == "Safe":
        if _language_code(language) == "ru":
            summary = (
                f"Как диетологический разбор, это выглядит как неплохая небольшая добавка для {pet_name}, если продукт простой и без приправ."
            )
            reasons_title = "Почему это ок"
            actions_title = "Как я бы это давал"
            watch_title = "Если не зайдет"
            actions = [
                "Оставляй это как маленькое дополнение, а не как основу рациона.",
                _coach_portion_hint(weight_lbs, "safe", language),
                "Лучше всего давать это в простом виде: без соли, масла, чеснока и соусов.",
            ]
            display = "Хороший вариант"
            badge = "Можно в рацион"
        else:
            summary = f"As a diet read, this looks like a solid small add-on for {pet_name} when it is plain and unseasoned."
            reasons_title = "Why It Works"
            actions_title = "How I'd Use It"
            watch_title = "If It Doesn't Sit Well"
            actions = [
                "Keep this as a small add-on, not the foundation of the diet.",
                _coach_portion_hint(weight_lbs, "safe", language),
                "Best when it is plain: no salt, butter, garlic, or sauces.",
            ]
            display = "Good Add-On"
            badge = "Good Fit"
        return {
            "summary": summary,
            "display": display,
            "badge": badge,
            "actions_title": actions_title,
            "reasons_title": reasons_title,
            "watch_title": watch_title,
            "actions": actions,
        }

    if verdict == "Caution":
        dairy_or_rich = bool({"dairy", "fatty", "sweet", "salty", "spicy"} & caution_categories)
        if _language_code(language) == "ru":
            summary = (
                f"Как еда на каждый день, это слабый вариант для {pet_name}. Я бы оставил это только как редкое угощение, а не как регулярную часть рациона."
            )
            if dairy_or_rich:
                summary = (
                    f"Для повседневного рациона {pet_name} это скорее редкое угощение, чем хороший регулярный выбор. "
                    f"Такое лучше давать изредка и совсем понемногу."
                )
            reasons_title = "Почему я осторожен"
            actions_title = "Как я бы это использовал"
            watch_title = "Если желудок отреагирует"
            actions = [
                "Считай это редким угощением, а не нормальной частью рациона.",
                _coach_portion_hint(weight_lbs, "caution", language),
                "Если питомец чувствительный, маленький или с хроническими состояниями, лучше выбрать более простой вариант.",
            ]
            display = "Иногда можно"
            badge = "Редкое угощение"
        else:
            summary = f"As an everyday food choice, this is weak for {pet_name}. I would frame it as an occasional treat, not a routine part of the bowl."
            if dairy_or_rich:
                summary = f"For everyday feeding, this is more of an occasional treat than a smart repeat choice for {pet_name}. Keep it infrequent and very small."
            reasons_title = "Why I'm Cautious"
            actions_title = "How I'd Use It"
            watch_title = "If The Stomach Pushes Back"
            actions = [
                "Treat this as an occasional extra, not a normal part of the meal plan.",
                _coach_portion_hint(weight_lbs, "caution", language),
                "If your pet is sensitive, small, or has chronic conditions, choose a simpler option instead.",
            ]
            display = "Occasional Treat"
            badge = "Treat Only"
        return {
            "summary": summary,
            "display": display,
            "badge": badge,
            "actions_title": actions_title,
            "reasons_title": reasons_title,
            "watch_title": watch_title,
            "actions": actions,
        }

    if _language_code(language) == "ru":
        summary = (
            f"Как вариант питания я бы это пропустил. Для {pet_name} лучше взять более простой и предсказуемый продукт, чем строить кормление вокруг {match_text or 'этого продукта'}."
        )
        actions_title = "Что лучше сделать вместо этого"
        reasons_title = "Почему я бы пропустил"
        watch_title = "Если случайно попробует"
        actions = [
            "Не делай это частью рациона.",
            "Возьми более простой и безопасный для питомца вариант без спорных ингредиентов.",
            "Если питомец случайно это съест, переходи в экстренный режим.",
        ]
        display = "Лучше пропустить"
        badge = "Лучше не включать"
    else:
        summary = f"As a feeding choice, I would skip this. For {pet_name}, a simpler and more predictable option makes more sense than building around {match_text or 'this food'}."
        actions_title = "What I'd Do Instead"
        reasons_title = "Why I'd Skip It"
        watch_title = "If It Gets Eaten By Accident"
        actions = [
            "Do not make this part of the routine feeding plan.",
            "Choose a simpler pet-safe option without questionable add-ins.",
            "If your pet accidentally eats it later, switch to Emergency Mode.",
        ]
        display = "Skip This Food"
        badge = "Not A Fit"
    return {
        "summary": summary,
        "display": display,
        "badge": badge,
        "actions_title": actions_title,
        "reasons_title": reasons_title,
        "watch_title": watch_title,
        "actions": actions,
    }


def _safe_alternatives(species: str, language: str = "en") -> list[str]:
    if species == "cat":
        items = [
            "plain cooked chicken or turkey",
            "a small spoon of plain pumpkin",
            "commercial cat treats with simple ingredients",
        ]
        return [_localize_alternative(item, language) for item in items]
    items = [
        "plain cooked chicken or turkey",
        "carrot slices or cucumber pieces",
        "commercial dog treats with short ingredient lists",
    ]
    return [_localize_alternative(item, language) for item in items]


def _safe_swap_catalog(species: str) -> dict[str, list[dict[str, str]]]:
    if species == "cat":
        return {
            "general": [
                {
                    "title": "Freeze-dried chicken cat treats",
                    "query": "freeze dried chicken cat treats",
                    "why": "Single-ingredient treats are easier to audit for hidden seasonings or sweeteners.",
                },
                {
                    "title": "Limited-ingredient cat treats",
                    "query": "limited ingredient cat treats",
                    "why": "Short ingredient lists make it easier to avoid surprise fillers and problem ingredients.",
                },
                {
                    "title": "Simple lickable cat treats",
                    "query": "lickable cat treats limited ingredient",
                    "why": "A pet-formulated lickable treat is usually a calmer choice than human snacks.",
                },
            ],
            "low_fat": [
                {
                    "title": "Sensitive stomach cat treats",
                    "query": "sensitive stomach cat treats",
                    "why": "These are easier to use when rich or greasy human food is the problem.",
                },
                {
                    "title": "Freeze-dried chicken cat treats",
                    "query": "freeze dried chicken cat treats",
                    "why": "Lean, simple protein is usually a cleaner swap than fatty leftovers.",
                },
                {
                    "title": "Digestive support cat topper",
                    "query": "digestive support cat food topper",
                    "why": "A small pet-formulated topper can feel rewarding without the grease of table scraps.",
                },
            ],
            "simple_label": [
                {
                    "title": "Limited-ingredient cat treats",
                    "query": "limited ingredient cat treats",
                    "why": "When the risky part is hidden in the label, simpler is better.",
                },
                {
                    "title": "Single-protein cat treats",
                    "query": "single protein cat treats",
                    "why": "Single-protein products are easier to compare against allergy and sensitivity lists.",
                },
                {
                    "title": "Simple lickable cat treats",
                    "query": "lickable cat treats limited ingredient",
                    "why": "This keeps the reward feeling while reducing mystery ingredients.",
                },
            ],
            "bland": [
                {
                    "title": "Sensitive stomach cat wet food",
                    "query": "sensitive stomach cat wet food",
                    "why": "A gentler wet food option is often better than salty or spicy human food.",
                },
                {
                    "title": "Limited-ingredient cat treats",
                    "query": "limited ingredient cat treats",
                    "why": "Simple treats help avoid extra spices, sodium, and sauces.",
                },
                {
                    "title": "Simple lickable cat treats",
                    "query": "lickable cat treats limited ingredient",
                    "why": "These are easier to portion than random kitchen scraps.",
                },
            ],
            "low_sugar": [
                {
                    "title": "Protein-first cat treats",
                    "query": "high protein cat treats limited ingredient",
                    "why": "Protein-forward treats are a better direction than dessert-type foods.",
                },
                {
                    "title": "Freeze-dried chicken cat treats",
                    "query": "freeze dried chicken cat treats",
                    "why": "A straightforward protein treat is cleaner than sugary human food.",
                },
                {
                    "title": "Limited-ingredient cat treats",
                    "query": "limited ingredient cat treats",
                    "why": "Short labels help you avoid syrupy fillers and extras.",
                },
            ],
            "low_sodium": [
                {
                    "title": "Low sodium cat food topper",
                    "query": "low sodium cat food topper",
                    "why": "This is a better direction than salty chips, sauces, or deli-style leftovers.",
                },
                {
                    "title": "Freeze-dried chicken cat treats",
                    "query": "freeze dried chicken cat treats",
                    "why": "Plain protein treats are usually simpler than seasoned human foods.",
                },
                {
                    "title": "Limited-ingredient cat treats",
                    "query": "limited ingredient cat treats",
                    "why": "Fewer ingredients usually means fewer hidden salts and flavorings.",
                },
            ],
            "soft_small": [
                {
                    "title": "Soft cat treats",
                    "query": "soft cat treats limited ingredient",
                    "why": "Soft, bite-sized treats are easier than risky hard objects or bones.",
                },
                {
                    "title": "Simple lickable cat treats",
                    "query": "lickable cat treats limited ingredient",
                    "why": "Lickable treats remove the risk of splintering or hard chunks.",
                },
                {
                    "title": "Small-bite cat treats",
                    "query": "small bite cat treats",
                    "why": "Small treats help with portion control and reduce choking-style concerns.",
                },
            ],
            "cooked_gentle": [
                {
                    "title": "Sensitive stomach cat wet food",
                    "query": "sensitive stomach cat wet food",
                    "why": "A cooked, pet-formulated option is safer than raw human food.",
                },
                {
                    "title": "Digestive support cat topper",
                    "query": "digestive support cat food topper",
                    "why": "This can add excitement without jumping into raw or risky add-ons.",
                },
                {
                    "title": "Limited-ingredient cat treats",
                    "query": "limited ingredient cat treats",
                    "why": "Keeps the ingredient list short and predictable.",
                },
            ],
        }

    return {
        "general": [
            {
                "title": "Limited-ingredient dog biscuits",
                "query": "limited ingredient dog biscuits",
                "why": "Simple labels are easier to trust than random human food ingredients.",
            },
            {
                "title": "Freeze-dried chicken dog treats",
                "query": "freeze dried chicken dog treats",
                "why": "Single-ingredient protein treats reduce hidden oils, onions, and sweeteners.",
            },
            {
                "title": "Pumpkin dog treats",
                "query": "pumpkin dog treats limited ingredient",
                "why": "Pumpkin-style treats are a gentler swap than rich table scraps.",
            },
        ],
        "low_fat": [
            {
                "title": "Low-fat dog treats",
                "query": "low fat dog treats",
                "why": "These are a better direction when greasy or fried food is the issue.",
            },
            {
                "title": "Freeze-dried chicken dog treats",
                "query": "freeze dried chicken dog treats",
                "why": "Lean protein is usually cleaner than pizza, bacon, or buttery leftovers.",
            },
            {
                "title": "Digestive support dog treats",
                "query": "digestive support dog treats",
                "why": "This gives a reward moment without the rich fat load of table scraps.",
            },
        ],
        "simple_label": [
            {
                "title": "Limited-ingredient dog biscuits",
                "query": "limited ingredient dog biscuits",
                "why": "Short ingredient lists make hidden xylitol, garlic, or other add-ins easier to avoid.",
            },
            {
                "title": "Single-protein dog treats",
                "query": "single protein dog treats",
                "why": "One clear protein is easier to check against allergies or sensitivities.",
            },
            {
                "title": "Freeze-dried chicken dog treats",
                "query": "freeze dried chicken dog treats",
                "why": "A simple protein treat is cleaner than label-heavy human snacks.",
            },
        ],
        "bland": [
            {
                "title": "Digestive support dog treats",
                "query": "digestive support dog treats",
                "why": "These are a better fit than salty, spicy, or heavily seasoned food.",
            },
            {
                "title": "Pumpkin dog treats",
                "query": "pumpkin dog treats limited ingredient",
                "why": "Pumpkin-style treats are usually gentler than fries, chips, or saucy leftovers.",
            },
            {
                "title": "Limited-ingredient dog treats",
                "query": "limited ingredient dog treats",
                "why": "A shorter label helps keep the flavorings and seasonings under control.",
            },
        ],
        "low_sugar": [
            {
                "title": "Low-sugar dog treats",
                "query": "low sugar dog treats",
                "why": "Dessert-style human food is a bad trade when a dog-safe treat can do the same job.",
            },
            {
                "title": "Single-protein dog treats",
                "query": "single protein dog treats",
                "why": "Protein-first treats avoid the syrup, frosting, and sugar problem entirely.",
            },
            {
                "title": "Freeze-dried chicken dog treats",
                "query": "freeze dried chicken dog treats",
                "why": "One simple ingredient is easier than cookies, donuts, or candy-type foods.",
            },
        ],
        "low_sodium": [
            {
                "title": "Low sodium dog treats",
                "query": "low sodium dog treats",
                "why": "A better choice when the risky food is salty, cured, or heavily seasoned.",
            },
            {
                "title": "Limited-ingredient dog biscuits",
                "query": "limited ingredient dog biscuits",
                "why": "Short labels help you dodge extra salt and flavor boosters.",
            },
            {
                "title": "Freeze-dried chicken dog treats",
                "query": "freeze dried chicken dog treats",
                "why": "Plain protein is usually cleaner than chips, jerky, or deli-style scraps.",
            },
        ],
        "soft_small": [
            {
                "title": "Soft training treats for dogs",
                "query": "soft training treats for dogs",
                "why": "Soft, bite-sized treats are safer than hard bones or risky chunks.",
            },
            {
                "title": "Limited-ingredient soft dog treats",
                "query": "limited ingredient soft dog treats",
                "why": "This keeps the reward small, soft, and easier to portion.",
            },
            {
                "title": "Small-bite dog treats",
                "query": "small bite dog treats",
                "why": "Tiny portion sizes are easier to manage after a risky food question.",
            },
        ],
        "cooked_gentle": [
            {
                "title": "Digestive support dog topper",
                "query": "digestive support dog food topper",
                "why": "A pet-formulated topper is safer than raw or restaurant-style add-ons.",
            },
            {
                "title": "Limited-ingredient dog treats",
                "query": "limited ingredient dog treats",
                "why": "A shorter, cooked ingredient list is easier to trust than raw foods.",
            },
            {
                "title": "Freeze-dried chicken dog treats",
                "query": "freeze dried chicken dog treats",
                "why": "A simple protein swap is cleaner than raw meat or mixed leftovers.",
            },
        ],
    }


def _safe_swap_focus(
    verdict: str,
    toxic_matches: list[dict[str, Any]],
    caution_matches: list[dict[str, Any]],
    conditions: set[str],
    allergy_text: str,
) -> str:
    if "pancreatitis" in conditions:
        return "low_fat"
    if "kidney disease" in conditions:
        return "low_sodium"
    if "diabetes" in conditions:
        return "low_sugar"
    if "sensitive stomach" in conditions:
        return "bland"
    if allergy_text.strip():
        return "simple_label"

    toxic_categories = {match.get("category", "") for match in toxic_matches}
    caution_categories = {match.get("category", "") for match in caution_matches}

    if "obstruction" in toxic_categories:
        return "soft_small"
    if "toxin" in toxic_categories:
        return "simple_label"
    if "fatty" in caution_categories:
        return "low_fat"
    if "salty" in caution_categories or "spicy" in caution_categories:
        return "bland"
    if "sweet" in caution_categories:
        return "low_sugar"
    if "raw" in caution_categories:
        return "cooked_gentle"
    if "label_check" in caution_categories:
        return "simple_label"
    if verdict != "Safe":
        return "simple_label"
    return "general"


def _safe_swap_title(verdict: str, pet_name: str, already_ate: bool, language: str = "en") -> str:
    if _language_code(language) == "ru":
        if verdict == "Avoid":
            return f"Более безопасные замены для {pet_name}"
        if verdict == "Caution":
            return f"Более чистые варианты для {pet_name}"
        if already_ate:
            return f"Хорошие запасные варианты для {pet_name}"
        return f"Что стоит держать дома для {pet_name}"
    if verdict == "Avoid":
        return f"Safer swaps for {pet_name}"
    if verdict == "Caution":
        return f"Cleaner options for {pet_name}"
    if already_ate:
        return f"Good backup options for {pet_name}"
    return f"Stock-up favorites for {pet_name}"


def _safe_swap_subtitle(
    verdict: str,
    focus: str,
    species: str,
    already_ate: bool,
    language: str = "en",
) -> str:
    if _language_code(language) == "ru":
        species_word = "собачьих" if species == "dog" else "кошачьих"
        focus_copy = {
            "low_fat": "Нежирные варианты здесь разумнее, чем жирные остатки со стола.",
            "simple_label": "Короткий состав — самый простой способ избежать скрытых рискованных ингредиентов.",
            "bland": "Простые и мягкие варианты лучше, чем соленая, острая или сильно приправленная еда.",
            "low_sugar": "Лучше уйти от десертов и выбирать белковые лакомства для питомцев.",
            "low_sodium": "Менее соленые и менее переработанные варианты здесь безопаснее.",
            "soft_small": "Мягкие маленькие лакомства безопаснее, чем твердые кости, большие куски и объедки.",
            "cooked_gentle": "Приготовленные продукты для питомцев безопаснее, чем сырая человеческая еда.",
            "general": "Готовые лакомства для питомцев обычно надежнее случайной человеческой еды.",
        }.get(focus, "Простые лакомства для питомцев обычно безопаснее как запасной вариант.")

        if verdict == "Avoid" and already_ate:
            return (
                f"Сначала разберите срочную ситуацию. Потом такие {species_word} варианты стоит держать под рукой, "
                "чтобы не возвращаться к тому же рискованному продукту."
            )

        return focus_copy

    species_word = "dog" if species == "dog" else "cat"
    focus_copy = {
        "low_fat": "Lean and lower-fat picks make more sense than greasy leftovers.",
        "simple_label": "Short ingredient lists are the easiest way to avoid hidden problem ingredients.",
        "bland": "Simple, gentler options are better than salty, spicy, or heavily seasoned foods.",
        "low_sugar": "Skip dessert-type foods and steer toward protein-first pet treats.",
        "low_sodium": "Lower-sodium, less processed choices are the safer lane here.",
        "soft_small": "Small, soft treats are a better fit than hard objects, bones, or chunky scraps.",
        "cooked_gentle": "Cooked, pet-formulated options are a safer direction than raw human foods.",
        "general": "Pet-formulated treats are still a cleaner baseline than random human food.",
    }.get(focus, "Simple pet treats are usually the safer fallback.")

    if verdict == "Avoid" and already_ate:
        return (
            f"Handle the urgent situation first. After that, these are the kinds of {species_word}-safe options "
            "worth keeping around so the same risky food question does not come up again."
        )

    return focus_copy


def _safe_swap_items(
    species: str,
    focus: str,
) -> list[dict[str, str]]:
    catalog = _safe_swap_catalog(species)
    return catalog.get(focus) or catalog["general"]


def _build_safe_swap(
    species: str,
    pet_name: str,
    verdict: str,
    toxic_matches: list[dict[str, Any]],
    caution_matches: list[dict[str, Any]],
    conditions: set[str],
    allergy_text: str,
    already_ate: bool,
    language: str = "en",
) -> dict[str, Any]:
    focus = _safe_swap_focus(
        verdict=verdict,
        toxic_matches=toxic_matches,
        caution_matches=caution_matches,
        conditions=conditions,
        allergy_text=allergy_text,
    )
    items = _safe_swap_items(species, focus)
    return {
        "focus": focus,
        "title": _safe_swap_title(verdict, pet_name, already_ate, language),
        "subtitle": _safe_swap_subtitle(verdict, focus, species, already_ate, language),
        "note": (
            "Это только поисковые ссылки. Перед покупкой всегда перепроверяйте полный состав."
            if _language_code(language) == "ru"
            else "Search links only. Double-check the full ingredient label before buying anything new."
        ),
        "items": items,
    }


def analyze_food(
    food_text: str,
    pet_profile: dict[str, Any],
    already_ate: bool = False,
    amount_label: str = "Small bite",
    symptoms: list[str] | None = None,
    time_since: str = "",
    image_summary: str = "",
    language: str = "en",
) -> dict[str, Any]:
    symptoms = symptoms or []
    species = (pet_profile.get("species") or "Dog").strip().lower()
    species = "cat" if species.startswith("cat") else "dog"
    pet_name = (pet_profile.get("name") or "your pet").strip() or "your pet"
    weight_lbs = float(pet_profile.get("weight_lbs") or 0)
    age_years = float(pet_profile.get("age_years") or 0)
    conditions = {condition.strip().lower() for condition in pet_profile.get("conditions", []) if condition}
    allergies = pet_profile.get("allergies", "")
    combined_text = " ".join(part for part in [food_text, image_summary] if part).strip()
    combined_text = _augment_multilingual_text(combined_text)
    normalized_text = _normalize_text(combined_text)
    toxic_matches = _find_rule_matches(normalized_text, species, HIGH_RISK_RULES)
    caution_matches = _find_rule_matches(normalized_text, species, CAUTION_RULES)
    safe_matches = _find_rule_matches(normalized_text, species, SAFE_RULES)
    severe_hits = [symptom for symptom in symptoms if symptom.lower() in SEVERE_SYMPTOMS]
    moderate_hits = [symptom for symptom in symptoms if symptom.lower() in MODERATE_SYMPTOMS]
    unknown_item = not toxic_matches and not caution_matches and not safe_matches

    score = 0
    if toxic_matches:
        score = 2
    elif caution_matches or unknown_item:
        score = 1

    if already_ate and weight_lbs and weight_lbs < 15 and (toxic_matches or caution_matches):
        score = max(score, 2 if toxic_matches else 1)

    if age_years >= 10 and caution_matches:
        score = max(score, 1)

    if amount_label in {"Moderate portion", "Large portion"} and (caution_matches or unknown_item):
        score = max(score, 1)

    condition_reasons, condition_boost = _condition_adjustments(conditions, caution_matches)
    score = min(2, score + condition_boost)
    allergy_reasons = _allergy_adjustments(allergies, normalized_text)
    if allergy_reasons:
        score = max(score, 1)

    acute_case = _is_acute_case(already_ate, severe_hits, moderate_hits)

    if severe_hits:
        score = 2
    elif moderate_hits and (toxic_matches or already_ate):
        score = max(score, 1)

    verdict = "Safe" if score == 0 else "Caution" if score == 1 else "Avoid"
    if acute_case:
        verdict_tone = {
            "Safe": {
                "label": "Низкий риск" if _language_code(language) == "ru" else "Low risk",
                "display": "Можно" if _language_code(language) == "ru" else "Safe",
                "color": "#177245",
            },
            "Caution": {
                "label": "Осторожно" if _language_code(language) == "ru" else "Use caution",
                "display": "Осторожно" if _language_code(language) == "ru" else "Caution",
                "color": "#9a6300",
            },
            "Avoid": {
                "label": "Срочная проверка" if _language_code(language) == "ru" else "Urgent review",
                "display": "Нельзя" if _language_code(language) == "ru" else "Avoid",
                "color": "#a42d2d",
            },
        }[verdict]
    else:
        coach_preview = _coach_copy(
            verdict=verdict,
            pet_name=pet_name,
            match_labels=[match["label"] for match in toxic_matches + caution_matches + safe_matches],
            toxic_matches=toxic_matches,
            caution_matches=caution_matches,
            weight_lbs=weight_lbs,
            language=language,
        )
        verdict_tone = {
            "label": str(coach_preview["badge"]),
            "display": str(coach_preview["display"]),
            "color": "#177245" if verdict == "Safe" else "#9a6300" if verdict == "Caution" else "#a42d2d",
        }

    match_labels = [match["label"] for match in toxic_matches + caution_matches + safe_matches]
    reasons = [
        _localize_reason(match["why"], language)
        for match in toxic_matches + caution_matches + safe_matches
        if match.get("why")
    ]
    reasons.extend(_localize_reason(item, language) for item in condition_reasons)
    if _language_code(language) == "ru":
        reasons.extend(
            f"В описании, похоже, есть {allergy}, а это совпадает со списком аллергий питомца."
            for allergy in [item.strip() for item in re.split(r"[,/]", allergies or "") if item.strip()]
            if _keyword_present(normalized_text, allergy)
        )
    else:
        reasons.extend(allergy_reasons)

    if amount_label in {"Moderate portion", "Large portion"} and verdict != "Safe":
        reasons.append(_localize_reason("The amount matters. Bigger portions create more risk than a tiny lick or crumb.", language))

    if time_since and verdict == "Avoid":
        if _language_code(language) == "ru":
            reasons.append(
                f"С момента поедания прошло: {_localize_value(time_since, language)}. Обычно безопаснее обратиться за помощью раньше, чем ждать."
            )
        else:
            reasons.append(f"Time since exposure: {time_since}. Early professional guidance is usually safer than waiting.")

    if severe_hits:
        reasons.append(_localize_reason("Current symptoms already include emergency warning signs.", language))
    elif moderate_hits:
        reasons.append(_localize_reason("Current symptoms raise the level of concern above a routine treat question.", language))

    actions: list[str] = []
    if verdict == "Avoid" and acute_case:
        actions.extend(
            [
                "Уберите еду и держите рядом упаковку или состав."
                if _language_code(language) == "ru"
                else "Remove the food and keep the packaging or ingredient label nearby.",
                "Сразу свяжитесь с ветеринаром, круглосуточной клиникой или службой pet poison."
                if _language_code(language) == "ru"
                else "Contact a veterinarian, urgent care clinic, or pet poison resource right away.",
                "Не вызывайте рвоту и не давайте человеческие лекарства без указания ветеринара."
                if _language_code(language) == "ru"
                else "Do not induce vomiting or give human medication unless a veterinarian tells you to.",
            ]
        )
        if severe_hits:
            actions.append(
                "Если тяжело дышит, случился коллапс или судороги — езжайте в экстренную клинику прямо сейчас."
                if _language_code(language) == "ru"
                else "If breathing is hard, your pet collapses, or seizures occur, go to an emergency clinic now."
            )
    elif verdict == "Caution" and acute_case:
        actions.extend(
            [
                "Поставьте на паузу и перепроверьте полный состав, прежде чем давать еще."
                if _language_code(language) == "ru"
                else "Pause and double-check the full ingredient list before offering more.",
                "Если питомец уже съел часть, внимательно наблюдайте в ближайшие несколько часов."
                if _language_code(language) == "ru"
                else "If your pet already ate some, monitor closely over the next several hours.",
                "Свяжитесь с ветеринаром раньше, если питомец маленький, пожилой или с хроническими состояниями."
                if _language_code(language) == "ru"
                else "Reach out to your veterinarian sooner if your pet is small, senior, or has chronic conditions.",
            ]
        )
    elif acute_case:
        actions.extend(
            [
                "Давайте только в простом виде и маленькой порцией."
                if _language_code(language) == "ru"
                else "Serve it plain and in a small portion.",
                "Избегайте приправ, соусов, костей и жирных добавок."
                if _language_code(language) == "ru"
                else "Avoid heavy seasoning, sauces, bones, and rich extras.",
                "Остановитесь и пересмотрите решение, если появятся рвота, диарея или необычная вялость."
                if _language_code(language) == "ru"
                else "Stop and reassess if vomiting, diarrhea, or unusual tiredness appears.",
            ]
        )

    match_labels = [match["label"] for match in toxic_matches + caution_matches + safe_matches]
    coach_copy = _coach_copy(
        verdict=verdict,
        pet_name=pet_name,
        match_labels=match_labels,
        toxic_matches=toxic_matches,
        caution_matches=caution_matches,
        weight_lbs=weight_lbs,
        language=language,
    )

    if not acute_case:
        actions = list(coach_copy["actions"])

    watch_for = [
        symptom
        for match in toxic_matches + caution_matches
        for symptom in match.get("watch_for", [])
    ]
    if moderate_hits:
        watch_for.extend(moderate_hits)
    if not watch_for and verdict != "Safe":
        watch_for.extend(["vomiting", "diarrhea", "lethargy", "drooling"])

    confidence = "high" if toxic_matches or safe_matches else "medium" if caution_matches else "low"

    return {
        "verdict": verdict,
        "badge_label": verdict_tone["label"],
        "verdict_display": verdict_tone["display"],
        "badge_color": verdict_tone["color"],
        "summary": (
            _make_summary(
                verdict=verdict,
                pet_name=pet_name,
                species=species,
                amount_label=amount_label,
                already_ate=already_ate,
                match_labels=match_labels,
                unknown_item=unknown_item,
                language=language,
            )
            if acute_case
            else str(coach_copy["summary"])
        ),
        "reasons": _dedupe(reasons),
        "actions": _dedupe(actions),
        "watch_for": _dedupe([_localize_symptom(item, language) for item in watch_for]),
        "alternatives": _safe_alternatives(species, language),
        "safe_swap": _build_safe_swap(
            species=species,
            pet_name=pet_name,
            verdict=verdict,
            toxic_matches=toxic_matches,
            caution_matches=caution_matches,
            conditions=conditions,
            allergy_text=allergies,
            already_ate=already_ate,
            language=language,
        ),
        "matched_labels": _dedupe([_localize_label(label, language) for label in match_labels]),
        "confidence": confidence,
        "already_ate": already_ate,
        "amount_label": amount_label,
        "symptoms": symptoms,
        "time_since": time_since,
        "image_summary": image_summary.strip(),
        "food_text": food_text.strip(),
        "pet_name": pet_name,
        "species": species,
        "language": _language_code(language),
        "presentation_mode": "acute" if acute_case else "coach",
        "actions_title": (
            "Что делать сейчас" if _language_code(language) == "ru" else "What To Do Now"
        )
        if acute_case
        else str(coach_copy["actions_title"]),
        "reasons_title": (
            "Почему такой вердикт" if _language_code(language) == "ru" else "Why This Verdict"
        )
        if acute_case
        else str(coach_copy["reasons_title"]),
        "watch_title": (
            "За какими симптомами следить" if _language_code(language) == "ru" else "Symptoms to watch"
        )
        if acute_case
        else str(coach_copy["watch_title"]),
    }


def answer_follow_up(
    question: str,
    analysis: dict[str, Any],
    pet_profile: dict[str, Any],
    language: str = "en",
) -> str:
    normalized_question = _normalize_text(question)
    pet_name = analysis.get("pet_name") or pet_profile.get("name") or "your pet"
    language = _language_code(language)
    watch_for = analysis.get("watch_for") or (
        ["рвота", "диарея", "вялость", "слюнотечение"]
        if language == "ru"
        else ["vomiting", "diarrhea", "lethargy", "drooling"]
    )

    if not normalized_question:
        return (
            "Спроси про размер порции, симптомы для наблюдения или более безопасные варианты, и я отвечу коротко и по делу."
            if language == "ru"
            else "Ask about portion size, symptoms to watch for, or safer alternatives and I will keep it focused."
        )

    if _contains_any(normalized_question, ["how much", "portion", "bite", "small amount", "сколько", "порц", "кус", "немного"]):
        return (
            f"Для {pet_name} количество очень важно. Маленький лизок и полноценная порция — это разные уровни риска, а маленькие питомцы обычно попадают в проблему быстрее. Если точное количество неизвестно, лучше считать ситуацию более рискованной."
            if language == "ru"
            else f"For {pet_name}, size matters a lot. A tiny lick can be very different from a full serving, and smaller pets tend to get into trouble faster. When the exact amount is unclear, treat the situation more cautiously."
        )

    if _contains_any(normalized_question, ["symptom", "watch", "look for", "симптом", "наблюд", "следить"]):
        return (
            f"Наблюдай за такими признаками: {_join_labels(watch_for, language)}. Если симптомы усиливаются или кажутся необычными, свяжись с ветеринаром."
            if language == "ru"
            else f"Keep an eye out for: {_join_labels(watch_for, language)}. If symptoms escalate or feel unusual, contact a veterinarian."
        )

    if _contains_any(normalized_question, ["vet", "clinic", "emergency", "er", "call", "вет", "клиник", "экстр", "позвон", "врач"]):
        action = analysis.get("actions", [])
        return (
            f"Мой самый безопасный вывод: {action[0]} {action[1] if len(action) > 1 else ''}".strip()
            + " Приложение помогает быстро сориентироваться, но срочные случаи должен вести ветеринар."
            if language == "ru"
            else f"My safest read is: {action[0]} {action[1] if len(action) > 1 else ''}".strip()
            + " This app supports quick decisions, but a veterinarian should guide urgent cases."
        )

    if _contains_any(normalized_question, ["instead", "alternative", "safer", "treat", "вместо", "альтернатив", "безопасн", "лакомств"]):
        return (
            f"Более безопасные идеи для {pet_name}: {_join_labels(analysis.get('alternatives', []), language)}."
            if language == "ru"
            else f"Safer ideas for {pet_name}: {_join_labels(analysis.get('alternatives', []), language)}."
        )

    if _contains_any(normalized_question, ["buy", "shop", "order", "куп", "заказ", "магазин"]):
        safe_swap = analysis.get("safe_swap", {})
        items = [item["title"] for item in safe_swap.get("items", [])]
        if items:
            return (
                f"Если нужен более чистый вариант, начни с {_join_labels(items[:3], language)}. Pet Help AI показывает это как идеи для поиска, а не как медицинские гарантии, поэтому всегда проверяй состав."
                if language == "ru"
                else f"If you want a cleaner replacement, start with {_join_labels(items[:3], language)}. Pet Help AI treats those as search ideas, not guaranteed medical recommendations, so always double-check labels."
            )

    if analysis.get("verdict") == "Safe":
        return (
            f"Пока это выглядит как относительно низкий риск, но держи продукт простым, порцию маленькой и остановись, если у {pet_name} появится расстройство желудка."
            if language == "ru"
            else f"This still looks relatively low risk, but keep it plain, keep the portion small, and stop if {pet_name} shows stomach upset."
        )

    if analysis.get("verdict") == "Avoid":
        return (
            f"Так как это попало в более рискованную категорию, я бы не ждал длинного списка симптомов перед обращением к ветеринару. Самый безопасный следующий шаг для {pet_name} — быстро получить профессиональную помощь."
            if language == "ru"
            else f"Because this landed in the higher-risk bucket, I would not wait for a long list of symptoms before asking a vet. The safest next step is quick professional guidance for {pet_name}."
        )

    return (
        f"Это серая зона. Я бы еще раз проверил состав, не давал больше и наблюдал за {pet_name}, если что-то кажется необычным."
        if language == "ru"
        else f"This is a gray-zone situation. I would double-check the label, avoid giving more, and monitor {pet_name} closely for any change in energy, stomach comfort, or breathing."
    )


def get_care_tips(pet_profile: dict[str, Any], language: str = "en") -> dict[str, list[str]]:
    species = (pet_profile.get("species") or "Dog").strip().lower()
    species = "cat" if species.startswith("cat") else "dog"
    weight_lbs = float(pet_profile.get("weight_lbs") or 0)
    age_years = float(pet_profile.get("age_years") or 0)
    conditions = {condition.strip().lower() for condition in pet_profile.get("conditions", []) if condition}
    language = _language_code(language)

    if language == "ru":
        daily_choices = (
            [
                "простая приготовленная курица или индейка маленькими кусочками",
                "простая тыква или простой рис для мягкого режима",
                "готовые кошачьи лакомства с коротким составом",
            ]
            if species == "cat"
            else [
                "простая приготовленная курица или индейка",
                "кусочки моркови или огурца",
                "готовые собачьи лакомства с простым составом",
            ]
        )

        red_flags = [
            "шоколад, ксилит, виноград и изюм",
            "лук, чеснок и сильно приправленные остатки еды",
            "алкоголь, кофеин, edible-продукты с каннабисом и человеческие лекарства",
        ]
    else:
        daily_choices = (
            [
                "plain cooked chicken or turkey in small bites",
                "plain pumpkin or plain rice for a bland reset",
                "commercial cat treats with short ingredient lists",
            ]
            if species == "cat"
            else [
                "plain cooked chicken or turkey",
                "carrot or cucumber pieces",
                "commercial dog treats with simple ingredients",
            ]
        )

        red_flags = [
            "chocolate, xylitol, grapes or raisins",
            "onion, garlic, and heavily seasoned leftovers",
            "alcohol, caffeine, cannabis edibles, and human medicines",
        ]

    personalization: list[str] = []
    if weight_lbs and weight_lbs < 15:
        personalization.append(
            "Маленькие питомцы могут быстрее попасть в проблему с тем же количеством еды, поэтому держите угощения совсем маленькими."
            if language == "ru"
            else "Small pets can get into trouble faster with the same amount of food, so keep treats tiny."
        )
    if age_years >= 10:
        personalization.append(
            "Пожилые питомцы часто хуже переносят тяжелую еду, поэтому простой и мягкий вариант обычно безопаснее."
            if language == "ru"
            else "Senior pets often tolerate rich food less well, so bland and simple is the safer default."
        )
    if "pancreatitis" in conditions:
        personalization.append(
            "Раз в профиле указан панкреатит, жирные остатки со стола лучше исключить."
            if language == "ru"
            else "Because pancreatitis is on the profile, greasy table scraps should stay off the menu."
        )
    if "kidney disease" in conditions:
        personalization.append(
            "Для чувствительных почек лучше подходят менее соленые варианты."
            if language == "ru"
            else "Lower-salt options are a better fit for kidney-sensitive pets."
        )
    if "diabetes" in conditions:
        personalization.append(
            "Сладкие перекусы плохо подходят питомцам с диабетом, даже если это не явный токсин."
            if language == "ru"
            else "Sugary snacks are a poor fit for diabetic pets even when they are not outright toxic."
        )
    if not personalization:
        personalization.append(
            "Обычно безопаснее всего начинать с простой еды без приправ и маленьких кусочков."
            if language == "ru"
            else "Plain, unseasoned, bite-sized foods are usually the safest place to start."
        )

    return {
        "daily_choices": daily_choices,
        "red_flags": red_flags,
        "personalization": personalization,
    }
