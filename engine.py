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


def _normalize_text(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", " ", (value or "").lower())
    return re.sub(r"\s+", " ", clean).strip()


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


def _join_labels(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


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


def extract_food_context_from_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict[str, str | bool]:
    if not has_openai_key():
        return {
            "ok": False,
            "summary": "",
            "error": "Add OPENAI_API_KEY to enable AI image understanding.",
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
                        "You analyze pet food risk. Identify the likely food or product shown, list the most "
                        "important visible ingredients or preparation clues, and surface hidden risk cues like "
                        "chocolate, grapes, onion, garlic, xylitol, caffeine, alcohol, bones, or spicy sauces. "
                        "Be concise and factual."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Describe the food or packaging in 3 short lines.\n"
                                "Line 1: Likely item\n"
                                "Line 2: Visible ingredients or preparation\n"
                                "Line 3: Risk cues for dogs or cats"
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
) -> str:
    species_word = "dog" if species == "dog" else "cat"
    amount_text = amount_label.lower()
    match_text = _join_labels(match_labels)

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


def _safe_alternatives(species: str) -> list[str]:
    if species == "cat":
        return [
            "plain cooked chicken or turkey",
            "a small spoon of plain pumpkin",
            "commercial cat treats with simple ingredients",
        ]
    return [
        "plain cooked chicken or turkey",
        "carrot slices or cucumber pieces",
        "commercial dog treats with short ingredient lists",
    ]


def analyze_food(
    food_text: str,
    pet_profile: dict[str, Any],
    already_ate: bool = False,
    amount_label: str = "Small bite",
    symptoms: list[str] | None = None,
    time_since: str = "",
    image_summary: str = "",
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

    if severe_hits:
        score = 2
    elif moderate_hits and (toxic_matches or already_ate):
        score = max(score, 1)

    verdict = "Safe" if score == 0 else "Caution" if score == 1 else "Avoid"
    verdict_tone = {
        "Safe": {"label": "Low risk", "color": "#177245"},
        "Caution": {"label": "Use caution", "color": "#9a6300"},
        "Avoid": {"label": "Urgent review", "color": "#a42d2d"},
    }[verdict]

    match_labels = [match["label"] for match in toxic_matches + caution_matches + safe_matches]
    reasons = [
        match["why"]
        for match in toxic_matches + caution_matches + safe_matches
        if match.get("why")
    ]
    reasons.extend(condition_reasons)
    reasons.extend(allergy_reasons)

    if amount_label in {"Moderate portion", "Large portion"} and verdict != "Safe":
        reasons.append("The amount matters. Bigger portions create more risk than a tiny lick or crumb.")

    if time_since and verdict == "Avoid":
        reasons.append(f"Time since exposure: {time_since}. Early professional guidance is usually safer than waiting.")

    if severe_hits:
        reasons.append("Current symptoms already include emergency warning signs.")
    elif moderate_hits:
        reasons.append("Current symptoms raise the level of concern above a routine treat question.")

    actions: list[str] = []
    if verdict == "Avoid":
        actions.extend(
            [
                "Remove the food and keep the packaging or ingredient label nearby.",
                "Contact a veterinarian, urgent care clinic, or pet poison resource right away.",
                "Do not induce vomiting or give human medication unless a veterinarian tells you to.",
            ]
        )
        if severe_hits:
            actions.append("If breathing is hard, your pet collapses, or seizures occur, go to an emergency clinic now.")
    elif verdict == "Caution":
        actions.extend(
            [
                "Pause and double-check the full ingredient list before offering more.",
                "If your pet already ate some, monitor closely over the next several hours.",
                "Reach out to your veterinarian sooner if your pet is small, senior, or has chronic conditions.",
            ]
        )
    else:
        actions.extend(
            [
                "Serve it plain and in a small portion.",
                "Avoid heavy seasoning, sauces, bones, and rich extras.",
                "Stop and reassess if vomiting, diarrhea, or unusual tiredness appears.",
            ]
        )

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
        "badge_color": verdict_tone["color"],
        "summary": _make_summary(
            verdict=verdict,
            pet_name=pet_name,
            species=species,
            amount_label=amount_label,
            already_ate=already_ate,
            match_labels=match_labels,
            unknown_item=unknown_item,
        ),
        "reasons": _dedupe(reasons),
        "actions": _dedupe(actions),
        "watch_for": _dedupe(watch_for),
        "alternatives": _safe_alternatives(species),
        "matched_labels": _dedupe(match_labels),
        "confidence": confidence,
        "already_ate": already_ate,
        "amount_label": amount_label,
        "symptoms": symptoms,
        "time_since": time_since,
        "image_summary": image_summary.strip(),
        "food_text": food_text.strip(),
        "pet_name": pet_name,
        "species": species,
    }


def answer_follow_up(question: str, analysis: dict[str, Any], pet_profile: dict[str, Any]) -> str:
    normalized_question = _normalize_text(question)
    pet_name = analysis.get("pet_name") or pet_profile.get("name") or "your pet"

    if not normalized_question:
        return "Ask about portion size, symptoms to watch for, or safer alternatives and I will keep it focused."

    if any(token in normalized_question for token in ["how much", "portion", "bite", "small amount"]):
        return (
            f"For {pet_name}, size matters a lot. A tiny lick can be very different from a full serving, and smaller pets "
            f"tend to get into trouble faster. When the exact amount is unclear, treat the situation more cautiously."
        )

    if any(token in normalized_question for token in ["symptom", "watch", "look for"]):
        watch_for = analysis.get("watch_for") or ["vomiting", "diarrhea", "lethargy", "drooling"]
        return f"Keep an eye out for: {_join_labels(watch_for)}. If symptoms escalate or feel unusual, contact a veterinarian."

    if any(token in normalized_question for token in ["vet", "clinic", "emergency", "er", "call"]):
        action = analysis.get("actions", [])
        return (
            f"My safest read is: {action[0]} {action[1] if len(action) > 1 else ''}".strip()
            + " This app supports quick decisions, but a veterinarian should guide urgent cases."
        )

    if any(token in normalized_question for token in ["instead", "alternative", "safer", "treat"]):
        return f"Safer ideas for {pet_name}: {_join_labels(analysis.get('alternatives', []))}."

    if analysis.get("verdict") == "Safe":
        return (
            f"This still looks relatively low risk, but keep it plain, keep the portion small, and stop if {pet_name} "
            "shows stomach upset."
        )

    if analysis.get("verdict") == "Avoid":
        return (
            f"Because this landed in the higher-risk bucket, I would not wait for a long list of symptoms before asking a vet. "
            f"The safest next step is quick professional guidance for {pet_name}."
        )

    return (
        f"This is a gray-zone situation. I would double-check the label, avoid giving more, and monitor {pet_name} "
        "closely for any change in energy, stomach comfort, or breathing."
    )


def get_care_tips(pet_profile: dict[str, Any]) -> dict[str, list[str]]:
    species = (pet_profile.get("species") or "Dog").strip().lower()
    species = "cat" if species.startswith("cat") else "dog"
    weight_lbs = float(pet_profile.get("weight_lbs") or 0)
    age_years = float(pet_profile.get("age_years") or 0)
    conditions = {condition.strip().lower() for condition in pet_profile.get("conditions", []) if condition}

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
        personalization.append("Small pets can get into trouble faster with the same amount of food, so keep treats tiny.")
    if age_years >= 10:
        personalization.append("Senior pets often tolerate rich food less well, so bland and simple is the safer default.")
    if "pancreatitis" in conditions:
        personalization.append("Because pancreatitis is on the profile, greasy table scraps should stay off the menu.")
    if "kidney disease" in conditions:
        personalization.append("Lower-salt options are a better fit for kidney-sensitive pets.")
    if "diabetes" in conditions:
        personalization.append("Sugary snacks are a poor fit for diabetic pets even when they are not outright toxic.")
    if not personalization:
        personalization.append("Plain, unseasoned, bite-sized foods are usually the safest place to start.")

    return {
        "daily_choices": daily_choices,
        "red_flags": red_flags,
        "personalization": personalization,
    }
