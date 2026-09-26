"""Programme Consultant: trained ranker plus catalogue planner.

Live quantities come from main_inventory (total and available), open
check_in_out rows, and staff names. Photo embedding tables have no quantity.
"""

from __future__ import annotations

import json
import math
import os
import re
import urllib.error
import urllib.request

import numpy as np
import torch
from torch import nn

from config import BASE_DIR

CATALOGUE_PATH = os.path.join(BASE_DIR, "data", "programme_catalogue.json")
BOOKINGS_PATH = os.path.join(BASE_DIR, "data", "kit_bookings.json")
WEIGHTS_PATH = os.path.join(BASE_DIR, "models", "programme_ranker.pt")
ENCODER_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ponytail: frozen encoder. Head sees constraint fits + theme cover + cosine,
# not the raw 768-d concat. 47 catalogue rows cannot train that width.

_ENCODER = None
_PACK = None


class ProgrammeRanker(nn.Module):
    def __init__(self, in_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.net(features).squeeze(-1)


def load_catalogue() -> dict:
    with open(CATALOGUE_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def load_booked_ids() -> set[str]:
    if not os.path.isfile(BOOKINGS_PATH):
        return set()
    with open(BOOKINGS_PATH, encoding="utf-8") as handle:
        payload = json.load(handle)
    return {str(item) for item in payload.get("booked_offering_ids") or []}


def _encoder():
    global _ENCODER
    if _ENCODER is None:
        from sentence_transformers import SentenceTransformer

        _ENCODER = SentenceTransformer(ENCODER_NAME)
    return _ENCODER


def encode_texts(texts: list[str]) -> np.ndarray:
    vectors = _encoder().encode(list(texts), normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vectors, dtype=np.float32)


def offering_document(offering: dict) -> str:
    parts = [
        offering.get("activity_title"),
        offering.get("short_description"),
        offering.get("suitable_themes"),
        offering.get("suitable_objectives"),
        offering.get("learning_outcomes"),
        offering.get("key_concepts"),
    ]
    return ". ".join(str(part).strip() for part in parts if part)


def request_document(request: dict) -> str:
    bits = [str(request.get("text") or "").strip()]
    for key in ("audience", "age", "count", "duration", "venue", "electricity", "internet", "water", "budget"):
        value = request.get(key)
        if value not in (None, "", "unknown"):
            bits.append(f"{key} {value}")
    access = str(request.get("accessibility") or "").strip()
    if access:
        bits.append(access)
    return ". ".join(bit for bit in bits if bit)


def _num(value) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"n/a", "unknown", "nil"} or "valid" in text.lower():
        return None
    try:
        return float(text)
    except ValueError:
        return None


def age_bounds(raw) -> tuple[float | None, float | None]:
    text = str(raw or "").strip().lower()
    if not text or "valid" in text or text in {"n/a", "unknown"}:
        return None, None
    span = re.search(r"(\d+)\s*[-–]\s*(\d+)", text)
    if span:
        return float(span.group(1)), float(span.group(2))
    plus = re.search(r"(\d+)\s*\+", text)
    if plus:
        return float(plus.group(1)), 99.0
    one = re.search(r"(\d+)", text)
    if one:
        return float(one.group(1)), 99.0
    return None, None


def _flag(raw) -> str:
    text = str(raw or "").strip().lower()
    if text.startswith("y"):
        return "yes"
    if text.startswith("n"):
        return "no"
    if "opt" in text:
        return "optional"
    return "unknown"


def _tokens(text: str) -> set[str]:
    found = set()
    for word in re.findall(r"[a-z0-9]+", str(text or "").lower()):
        if len(word) > 3 and word.endswith("s"):
            word = word[:-1]
        if len(word) < 5:
            continue
        found.add(word[:6])
    return found


_HINT_STOP = {
    "progra", "reques", "school", "studen", "count", "indoo", "outdo",
    "unknow", "audien", "theme", "object", "durati", "electr", "intern",
    "water", "budget", "about", "group", "singl", "class", "youth",
    "early", "years", "sessio", "wants", "many",
}


def _hint_tokens(text: str) -> set[str]:
    return {token for token in _tokens(text) if token not in _HINT_STOP}


def _cover(query: set[str], doc: set[str]) -> float:
    if not query:
        return 0.0
    return len(query & doc) / len(query)


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _rule_text(catalogue: dict, rule_id: str) -> str:
    for rule in catalogue.get("rules") or []:
        if rule.get("rule_id") == rule_id:
            return str(rule.get("recommended_action") or rule.get("guidance") or rule_id)
    return rule_id


def _guidance(catalogue: dict, rule_id: str) -> str:
    for rule in catalogue.get("rules") or []:
        if rule.get("rule_id") == rule_id:
            return str(rule.get("guidance") or rule.get("recommended_action") or "")
    return ""


def theme_blob(offering: dict, catalogue: dict) -> str:
    bits = [
        offering.get("activity_title"),
        offering.get("suitable_themes"),
        offering.get("suitable_objectives"),
        offering.get("key_concepts"),
    ]
    offering_id = offering.get("offering_id")
    for mapping in catalogue.get("mappings") or []:
        ids = {mapping.get("primary_offering_id"), mapping.get("secondary_offering_id")}
        if offering_id in ids:
            bits.extend([mapping.get("theme"), mapping.get("related_concepts"), mapping.get("stakeholder_objective")])
    return " ".join(str(bit) for bit in bits if bit)


def blocking_rule(request: dict, offering: dict) -> str | None:
    low, high = age_bounds(offering.get("recommended_age"))
    age = request.get("age")
    if age is not None and low is not None and float(age) < low:
        return "RULE-001"
    if age is not None and high is not None and float(age) > high:
        return "RULE-001"
    # Capacity is a rotation, not a reject. Scored offering stays legal.
    duration = request.get("duration")
    setup = _num(offering.get("setup_time_min")) or 0.0
    delivery = _num(offering.get("standard_duration_min"))
    if duration is not None and delivery is not None and float(duration) < setup + delivery:
        return "RULE-005"
    venue = str(request.get("venue") or "unknown").lower()
    place = str(offering.get("indoor_outdoor") or "").lower()
    if venue == "outdoor" and "indoor" in place and "outdoor" not in place:
        return "RULE-006"
    if venue == "indoor" and "outdoor" in place and "indoor" not in place:
        return "RULE-006"
    power = str(request.get("electricity") or "unknown").lower()
    if power == "no" and _flag(offering.get("electricity_required")) == "yes":
        return "RULE-003"
    net = str(request.get("internet") or "unknown").lower()
    if net == "no" and _flag(offering.get("internet_required")) == "yes":
        return "RULE-004"
    water = str(request.get("water") or "unknown").lower()
    if water == "no" and _flag(offering.get("water_required")) == "yes":
        return "RULE-003"
    return None


def _fit_age(request: dict, offering: dict) -> float:
    low, high = age_bounds(offering.get("recommended_age"))
    age = request.get("age")
    if age is None or low is None:
        return 0.5
    age_f = float(age)
    if high is not None and low <= age_f <= high:
        return 1.0
    return 0.0


def _fit_duration(request: dict, offering: dict) -> float:
    duration = request.get("duration")
    delivery = _num(offering.get("standard_duration_min"))
    setup = _num(offering.get("setup_time_min")) or 0.0
    if duration is None or delivery is None:
        return 0.5
    need = setup + delivery
    if need <= 0:
        return 0.5
    if float(duration) >= need:
        return 1.0
    return max(0.0, float(duration) / need)


def _fit_venue(request: dict, offering: dict) -> float:
    venue = str(request.get("venue") or "unknown").lower()
    if venue in {"", "unknown"}:
        return 0.5
    if blocking_rule({**request, "age": None, "duration": None, "electricity": "unknown", "internet": "unknown", "water": "unknown"}, offering) == "RULE-006":
        return 0.0
    place = str(offering.get("indoor_outdoor") or "").lower()
    if venue in place:
        return 1.0
    return 0.4


def _fit_need(request_flag: str, offering_flag: str) -> float:
    if request_flag in {"", "unknown"}:
        return 0.5
    if offering_flag in {"unknown", "optional", "no"}:
        return 1.0 if request_flag == "no" or offering_flag != "yes" else 0.7
    if request_flag == "yes":
        return 1.0
    return 0.0


def _fit_cost(request: dict, offering: dict) -> float:
    budget = str(request.get("budget") or "unknown").lower()
    band = str(offering.get("cost_band") or "").lower()
    if budget in {"", "unknown"} or not band or "valid" in band:
        return 0.5
    return 1.0 if budget in band else 0.25


def _safety(offering: dict) -> float:
    level = str(offering.get("safety_level") or "").lower()
    if level.startswith("l"):
        return 1.0
    if level.startswith("m"):
        return 0.66
    if level.startswith("h"):
        return 0.33
    return 0.5


def pair_features(request: dict, offering: dict, request_vec: np.ndarray, offering_vec: np.ndarray, catalogue: dict) -> np.ndarray:
    hint = _cover(_hint_tokens(request_document(request)), _tokens(theme_blob(offering, catalogue)))
    text_sim = float(np.dot(request_vec, offering_vec))
    scalars = np.array(
        [
            _fit_age(request, offering),
            _fit_duration(request, offering),
            _fit_venue(request, offering),
            _fit_need(str(request.get("electricity") or "unknown").lower(), _flag(offering.get("electricity_required"))),
            _fit_need(str(request.get("internet") or "unknown").lower(), _flag(offering.get("internet_required"))),
            _fit_need(str(request.get("water") or "unknown").lower(), _flag(offering.get("water_required"))),
            _fit_cost(request, offering),
            _safety(offering),
            hint,
            text_sim,
        ],
        dtype=np.float32,
    )
    return scalars


def _load_pack() -> dict:
    global _PACK
    if _PACK is None:
        if not os.path.isfile(WEIGHTS_PATH):
            raise FileNotFoundError(f"missing {WEIGHTS_PATH}")
        try:
            _PACK = torch.load(WEIGHTS_PATH, map_location="cpu", weights_only=False)
        except TypeError:
            _PACK = torch.load(WEIGHTS_PATH, map_location="cpu")
    return _PACK


def rank(request: dict) -> list[dict]:
    catalogue = load_catalogue()
    pack = _load_pack()
    offerings = catalogue["offerings"]
    ids = pack["offering_ids"]
    if [row["offering_id"] for row in offerings] != list(ids):
        raise RuntimeError("catalogue order does not match programme_ranker.pt")
    matrix = np.asarray(pack["offering_embeddings"], dtype=np.float32)
    model = ProgrammeRanker(int(pack["in_dim"]))
    model.load_state_dict(pack["state_dict"])
    model.eval()
    request_vec = encode_texts([request_document(request)])[0]
    rows = [
        pair_features(request, offering, request_vec, matrix[index], catalogue)
        for index, offering in enumerate(offerings)
    ]
    with torch.no_grad():
        logits = model(torch.from_numpy(np.stack(rows))).numpy()
    booked = load_booked_ids() | _stock_booked(catalogue, request.get("_stock") or [])
    ranked = []
    for index, offering in enumerate(offerings):
        block = blocking_rule(request, offering)
        score = -1.0e9 if block else float(logits[index])
        ranked.append(
            {
                "offering_id": offering["offering_id"],
                "title": offering.get("activity_title") or offering["offering_id"],
                "score": round(score, 4) if score > -1.0e8 else None,
                "blocked": block,
                "booked": offering["offering_id"] in booked,
                "offering": offering,
            }
        )
    ranked.sort(key=lambda row: (row["score"] is not None, row["score"] or -1.0e9), reverse=True)
    return ranked


_NAME_STOP = {"the", "and", "for", "with", "set", "box", "contains"}
# ponytail: size/color words are not a different item. "rod"/"solution" still block a match.
_EXTRA_OK = {
    "black", "blue", "red", "white", "green", "yellow", "orange", "pink", "grey", "gray",
    "mm", "mf", "ff",
}


def _name_key(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(text or "").lower()))


def _name_tokens(text: str) -> set[str]:
    words = _name_key(text).split()
    merged = []
    for word in words:
        if merged and len(word) == 1 and len(merged[-1]) == 1 and merged[-1].isalpha() and word.isalpha():
            merged[-1] = merged[-1] + word
        elif merged and word.isdigit() and len(merged[-1]) <= 3 and merged[-1].isalpha():
            merged[-1] = merged[-1] + word
        else:
            merged.append(word)
    found = set()
    for word in merged:
        if len(word) >= 5 and word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]
        if word not in {"mm", "mf", "ff"} and (len(word) < 3 or word in _NAME_STOP):
            continue
        found.add(word)
    return found


def _real_extra(extra: set[str]) -> set[str]:
    return {token for token in extra if token not in _EXTRA_OK and not _size_token(token)}


def _size_token(token: str) -> bool:
    return bool(re.fullmatch(r"\d+(ml|mm|cm|m|v|w|pin|mah)?", token))


def _stock_rows(stock: list[dict]) -> list[dict]:
    rows = []
    for item in stock or []:
        name = str(item.get("inventory_name") or item.get("item_name") or "").strip()
        if not name:
            continue
        total = item.get("orig_quantity")
        if total is None:
            total = item.get("quantity")
        available = item.get("available")
        if available is None:
            available = item.get("available_quantity")
        rows.append(
            {
                "name": name,
                "key": _name_key(name),
                "tokens": _name_tokens(name),
                "total": int(total or 0),
                "available": int(available or 0),
            }
        )
    return rows


def _match_stock(kit_name: str, rows: list[dict], strict: bool = False) -> dict | None:
    """Match a kit line to store rows. Equal names only, plus size/color variants summed."""
    tokens = _name_tokens(kit_name)
    if not tokens:
        return None
    hits = []
    for row in rows:
        if not row["tokens"] or not tokens <= row["tokens"]:
            continue
        extra = row["tokens"] - tokens
        if strict:
            if extra:
                continue
        elif _real_extra(extra):
            continue
        hits.append(row)
    if not hits:
        return None
    if len(hits) == 1:
        return hits[0]
    return {
        "name": ", ".join(row["name"] for row in hits[:4]),
        "key": _name_key(kit_name),
        "tokens": tokens,
        "total": sum(row["total"] for row in hits),
        "available": sum(row["available"] for row in hits),
    }


def warehouse_view(stock: list | None, staff: list | None = None, movements: list | None = None) -> dict:
    """Compact live store. Embedding tables are photos, not stock counts."""
    items = [
        {"name": row["name"], "total": row["total"], "available": row["available"]}
        for row in _stock_rows(stock)
    ]
    people = []
    for row in staff or []:
        name = str(row.get("staff_name") or "").strip()
        if name and name not in people:
            people.append(name)
    checked_out = []
    for row in movements or []:
        direction = str(row.get("direction") or "")
        if direction and direction != "OUT":
            continue
        if row.get("in_dt") and not row.get("out_dt"):
            continue
        name = str(row.get("inventory_name") or row.get("class_name") or "").strip()
        if not name:
            continue
        checked_out.append(
            {
                "name": name,
                "quantity": int(row.get("quantity") or row.get("count") or 0),
                "staff": str(row.get("out_staff_name") or row.get("operator") or row.get("staff_name") or ""),
            }
        )
    return {"items": items, "staff": people, "checked_out": checked_out}


def _stock_booked(catalogue: dict, stock: list[dict]) -> set[str]:
    rows = _stock_rows(stock)
    booked = set()
    for offering_id, lines in (catalogue.get("kits") or {}).items():
        for line in lines:
            hit = _match_stock(str(line.get("name") or ""), rows, strict=True)
            if hit and hit["available"] <= 0:
                booked.add(str(offering_id))
                break
    return booked


def _blank(request: dict, key: str) -> bool:
    value = request.get(key)
    return value in (None, "", "unknown")


def _map_reason(catalogue: dict, offering_id: str, request: dict) -> str:
    request_tokens = _tokens(request_document(request))
    best = ""
    best_score = 0.0
    for mapping in catalogue.get("mappings") or []:
        ids = {mapping.get("primary_offering_id"), mapping.get("secondary_offering_id")}
        if offering_id not in ids:
            continue
        blob = " ".join(
            str(mapping.get(key) or "")
            for key in ("theme", "related_concepts", "stakeholder_objective", "reason_for_match")
        )
        score = _jaccard(request_tokens, _tokens(blob))
        if score >= best_score:
            best_score = score
            best = str(mapping.get("reason_for_match") or "")
    return best


def _split_bits(value) -> list[str]:
    text = str(value or "").strip()
    if not text or text.lower() in {"n/a", "unknown"} or "valid" in text.lower():
        return []
    parts = re.split(r"[;\n]+", text)
    return [part.strip() for part in parts if part.strip()]


def advise(request: dict, stock: list | None = None, staff: list | None = None, movements: list | None = None) -> dict:
    catalogue = load_catalogue()
    payload = dict(request)
    payload["_stock"] = list(stock or [])
    ranked = rank(payload)
    legal = [row for row in ranked if not row["blocked"]]
    picked = legal[:2]
    moved = [row for row in picked if row["booked"]]
    kept = [row for row in picked if not row["booked"]]
    backfill = [row for row in legal[2:] if not row["booked"]]
    chosen = (kept + backfill)[:2]
    alternative = moved[0] if moved else None
    questions = []
    if any(_blank(request, key) for key in ("age", "count", "duration", "venue", "budget")):
        guidance = _guidance(catalogue, "RULE-009")
        if guidance:
            questions.append(guidance)
    assumptions = []
    if _blank(request, "venue"):
        assumptions.append(_guidance(catalogue, "RULE-006"))
    if _blank(request, "budget"):
        assumptions.append(_guidance(catalogue, "RULE-008"))
    if not str(request.get("accessibility") or "").strip():
        assumptions.append(_guidance(catalogue, "RULE-011"))
    assumptions = [line for line in assumptions if line]
    rotations = []
    count = request.get("count")
    recommendations = []
    for row in chosen:
        offering = row["offering"]
        reason = _map_reason(catalogue, row["offering_id"], request) or str(offering.get("learning_outcomes") or "")
        rules = []
        high = _num(offering.get("max_participants"))
        if count is not None and high is not None and float(count) > high:
            rules.append("RULE-002")
            note = f"{row['title']}. {_rule_text(catalogue, 'RULE-002')}"
            if note not in rotations:
                rotations.append(note)
        recommendations.append(
            {
                "offering_id": row["offering_id"],
                "title": row["title"],
                "score": row["score"],
                "reason": reason,
                "rules": rules,
                "kit": "booked" if row["booked"] else "available",
                "description": str(offering.get("short_description") or ""),
            }
        )
    title = _programme_title(catalogue, request, chosen)
    journey = [_journey_step(row["offering"]) for row in _by_setup(chosen)]
    enhancements = []
    constraints = []
    for row in chosen:
        offering = row["offering"]
        for bit in _split_bits(offering.get("customisable_elements")):
            enhancements.append(f"Proposed Enhancement: {bit}")
        for key in ("key_constraints", "key_hazards", "participant_handling_rule"):
            text = str(offering.get(key) or "").strip()
            if text and text.lower() not in {"n/a", "unknown"}:
                constraints.append(f"{row['title']}. {text}")
        safety = str(offering.get("safety_level") or "").strip()
        if safety:
            constraints.append(f"{row['title']}. Safety_Level {safety}")
    alt_payload = None
    if alternative:
        substitute = chosen[0]["offering"] if chosen else {}
        alt_off = alternative["offering"]
        alt_payload = {
            "offering_id": alternative["offering_id"],
            "title": alternative["title"],
            "tradeoff": ". ".join(
                part
                for part in (
                    str(alt_off.get("short_description") or ""),
                    str(alt_off.get("key_constraints") or ""),
                    str(substitute.get("short_description") or ""),
                )
                if part
            ),
        }
    understanding_parts = [str(request.get("text") or "").strip()]
    understanding_parts.extend(row["description"] for row in recommendations if row["description"])
    return {
        "model": "programme_ranker",
        "understanding": " ".join(part for part in understanding_parts if part),
        "missing_questions": questions,
        "assumptions": assumptions,
        "items": _item_lines(catalogue, chosen, count, stock),
        "warehouse": warehouse_view(stock, staff, movements),
        "in_charge": _in_charge(chosen),
        "recommendations": recommendations,
        "programme_title": title,
        "storyline": " ".join(row["description"] for row in recommendations if row["description"]),
        "journey": journey,
        "enhancements": enhancements,
        "constraints_safety": constraints,
        "alternative": alt_payload,
        "rotations": rotations,
    }


def _sessions(count, offering: dict) -> int:
    cap = _num(offering.get("max_participants"))
    # ponytail: sheet pack qty is one session. Multiply by rotations when headcount
    # exceeds max. Per-person BOM if a sheet ever splits unit qty from session qty.
    if count is None or cap is None or cap <= 0:
        return 1
    return max(1, math.ceil(float(count) / cap))


def _item_lines(catalogue: dict, chosen: list[dict], count, stock: list | None = None) -> list[dict]:
    kits = catalogue.get("kits") or {}
    index = _stock_rows(stock)
    merged = {}
    order = []
    for row in chosen:
        sessions = _sessions(count, row["offering"])
        for kit in kits.get(row["offering_id"]) or []:
            name = kit.get("name") or ""
            packs = kit.get("packs")
            needed = None if packs is None else int(math.ceil(float(packs) * sessions))
            hit = _match_stock(name, index)
            key = (row["offering_id"], name.strip().lower())
            if key not in merged:
                order.append(key)
                merged[key] = {
                    "offering_id": row["offering_id"],
                    "title": row["title"],
                    "name": name,
                    "packs": needed,
                    "store_name": hit["name"] if hit else "",
                    "store_total": hit["total"] if hit else None,
                    "store_available": hit["available"] if hit else None,
                }
                continue
            old = merged[key]["packs"]
            if old is None:
                total = needed
            elif needed is None:
                total = old
            else:
                total = old + needed
            merged[key] = {**merged[key], "packs": total}
    return [merged[key] for key in order]


def _in_charge(chosen: list[dict]) -> list[dict]:
    people = []
    for row in chosen:
        needed = _num(row["offering"].get("facilitators_required"))
        if needed is None:
            continue
        people.append(
            {
                "offering_id": row["offering_id"],
                "title": row["title"],
                "facilitators": int(needed),
            }
        )
    return people


_SPEAK_RULE = (
    "You are the OneShot programme consultant. Reply in short plain sentences. "
    "Recommend only items and facilitator counts that appear in FACTS. "
    "FACTS.warehouse.items is every main_inventory row: name, total, available. "
    "FACTS.warehouse.checked_out is open check-outs. FACTS.warehouse.staff is staff names. "
    "items.packs is how many to prepare, not how many are in the store. "
    "The store count is only store_available, or warehouse.items available. "
    "If store_available is null, say the item is not in the store. "
    "Never say the store has the packs number. "
    "Do not invent a quantity, product, kit, activity, or staff name. "
    "Continue the existing chat. Answer the latest message from FACTS. "
    "If FACTS has no items, ask only for a missing event, headcount, or target group."
)


def _plain_reply(facts: dict) -> str:
    items = facts.get("items") or []
    charge = facts.get("in_charge") or []
    if not items and not charge:
        return "Tell me the event, how many people, and the target group."
    lines = ["Here is what the catalogue supports."]
    groups = []
    index = {}
    for row in items:
        key = str(row.get("offering_id") or row.get("title") or "")
        if key not in index:
            index[key] = len(groups)
            groups.append([])
        groups[index[key]].append(row)
    for group in groups:
        title = group[0].get("title") or ""
        for row in group[:4]:
            name = row.get("name") or ""
            packs = row.get("packs")
            if packs is None:
                line = f"{title}: {name}."
            else:
                line = f"{title}: {name} × {packs}."
            available = row.get("store_available")
            if available is None:
                line += " Not in the store list."
            else:
                line += f" Store has {available} available."
            lines.append(line)
        extra = len(group) - 4
        if extra > 0:
            lines.append(f"{title}: and {extra} more in this kit.")
    for row in charge:
        lines.append(f"{row.get('title')} needs {row.get('facilitators')} facilitators.")
    return " ".join(lines)


def _post_json(url: str, payload: dict, headers: dict) -> dict | None:
    data = json.dumps(payload).encode()
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "OneShotConsultant/1.0", **headers},
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def _cloud_reply(messages: list[dict], facts: dict, rule: str | None = None) -> dict | None:
    packed = [{"role": "system", "content": (rule or _SPEAK_RULE) + " FACTS: " + json.dumps(facts)[:24000]}]
    for message in messages[-8:]:
        role = "assistant" if message.get("role") == "assistant" else "user"
        text = str(message.get("content") or "")[:2000]
        if text:
            packed.append({"role": role, "content": text})
    groq = os.environ.get("GROQ_API_KEY", "").strip()
    if groq:
        body = _post_json(
            "https://api.groq.com/openai/v1/chat/completions",
            {"model": "qwen/qwen3.8-27b", "temperature": 0.3, "max_tokens": 400, "messages": packed},
            {"Authorization": "Bearer " + groq},
        )
        try:
            text = body["choices"][0]["message"]["content"].strip()
        except (TypeError, KeyError, IndexError, AttributeError):
            text = ""
        if text:
            return {"reply": text, "model": "groq"}
    gemini = os.environ.get("GEMINI_API_KEY", "").strip()
    if gemini:
        prompt = "\n".join(part["content"] for part in packed)
        body = _post_json(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=" + gemini,
            {"contents": [{"parts": [{"text": prompt}]}]},
            {},
        )
        try:
            text = body["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (TypeError, KeyError, IndexError, AttributeError):
            text = ""
        if text:
            return {"reply": text, "model": "gemini"}
    return None


def _boundary_reply(facts: dict) -> str:
    titles = []
    for row in facts.get("recommendations") or []:
        title = str(row.get("title") or "").strip()
        if title and title not in titles:
            titles.append(title)
    listed = ", ".join(titles) if titles else "the options in the programme brief"
    return (
        "I understand, and that is okay. "
        f"We can only suggest these: {listed}. "
        "If you really want something else, please contact the person in charge."
    )


def speak(messages: list[dict], facts: dict | None, warehouse: dict | None = None) -> dict:
    safe = dict(facts or {})
    if warehouse is not None:
        safe["warehouse"] = warehouse
    if safe.get("intent") == "decline":
        boundary = _boundary_reply(safe)
        cloud = _cloud_reply(
            list(messages or []),
            safe,
            "Be warm and brief. The visitor wants something else or does not want the suggestions. "
            "Do not name any activity that is not in FACTS. "
            "End with this sentence exactly: " + boundary,
        )
        reply = (cloud or {}).get("reply") or ""
        if "person in charge" in reply.lower():
            return {"reply": reply, "model": (cloud or {}).get("model") or "catalogue"}
        return {"reply": boundary, "model": "catalogue"}
    cloud = _cloud_reply(list(messages or []), safe)
    if cloud:
        return cloud
    return {"reply": _plain_reply(safe), "model": "catalogue"}


def _check_plain_reply() -> None:
    text = _plain_reply(
        {
            "items": [
                {"offering_id": "ACT-014", "title": "Water water Everywhere", "name": "Universal Indicator", "packs": None},
                {"offering_id": "ACT-014", "title": "Water water Everywhere", "name": "Beaker", "packs": None},
                {"offering_id": "ACT-014", "title": "Water water Everywhere", "name": "Tube", "packs": None},
                {"offering_id": "ACT-014", "title": "Water water Everywhere", "name": "Rod", "packs": None},
                {"offering_id": "ACT-014", "title": "Water water Everywhere", "name": "Tray", "packs": None},
                {"offering_id": "ACT-002", "title": "Combustion Show", "name": "Burner", "packs": 1},
            ],
            "in_charge": [
                {"title": "Water water Everywhere", "facilitators": 2},
                {"title": "Combustion Show", "facilitators": 1},
            ],
        }
    )
    assert "qty not on sheet" not in text
    assert text.count("Universal Indicator") == 1
    assert "Combustion Show: Burner × 1. Not in the store list." in text
    assert "and 1 more in this kit." in text
    assert "Combustion Show needs 1 facilitators." in text


def _check_items() -> None:
    catalogue = load_catalogue()
    offering = next(row for row in catalogue["offerings"] if row["offering_id"] == "ACT-001")
    chosen = [{"offering_id": "ACT-001", "title": offering["activity_title"], "offering": offering}]
    one = [row["packs"] for row in _item_lines(catalogue, chosen, 10) if row["packs"]]
    two = [row["packs"] for row in _item_lines(catalogue, chosen, 40) if row["packs"]]
    assert one and two[0] == one[0] * 2
    assert _in_charge(chosen)[0]["facilitators"] == 3


def _programme_title(catalogue: dict, request: dict, chosen: list[dict]) -> str:
    ids = {row["offering_id"] for row in chosen}
    request_tokens = _tokens(request_document(request))
    best_title = chosen[0]["title"] if chosen else ""
    best_score = -1.0
    for mapping in catalogue.get("mappings") or []:
        if mapping.get("primary_offering_id") not in ids and mapping.get("secondary_offering_id") not in ids:
            continue
        theme = str(mapping.get("theme") or "")
        score = _jaccard(request_tokens, _tokens(theme))
        if score > best_score and theme:
            best_score = score
            best_title = theme
    return best_title


def _by_setup(rows: list[dict]) -> list[dict]:
    def setup(row: dict) -> float:
        return _num(row["offering"].get("setup_time_min")) or 0.0

    return sorted(rows, key=setup)


def _check_stock() -> None:
    stock = [
        {"inventory_name": "Jumper Wire M M", "quantity": 64, "available": 10},
        {"inventory_name": "Ruler", "quantity": 45, "available": 0},
    ]
    hit = _match_stock("Jumper Wire", _stock_rows(stock))
    assert hit and hit["available"] == 10 and hit["total"] == 64
    dead = _stock_booked({"kits": {"ACT-009": [{"name": "Ruler"}]}}, stock)
    assert dead == {"ACT-009"}
    rods = [{"inventory_name": "glass rod", "quantity": 48, "available": 48}]
    assert _match_stock("Glass", _stock_rows(rods)) is None
    beakers = [
        {"inventory_name": "beakers 250ml", "quantity": 55, "available": 40},
        {"inventory_name": "beakers 500ml", "quantity": 10, "available": 4},
    ]
    beaker = _match_stock("Beaker", _stock_rows(beakers))
    assert beaker and beaker["available"] == 44
    view = warehouse_view(
        stock,
        [{"staff_name": "Ada"}],
        [{"direction": "OUT", "class_name": "Ruler", "count": 2, "operator": "Ada"}],
    )
    assert view["items"][1]["available"] == 0
    assert view["staff"] == ["Ada"]
    assert view["checked_out"] == [{"name": "Ruler", "quantity": 2, "staff": "Ada"}]
    text = _plain_reply(
        {
            "items": [
                {
                    "offering_id": "ACT-001",
                    "title": "Kit",
                    "name": "Jumper Wire",
                    "packs": 2,
                    "store_available": 10,
                }
            ]
        }
    )
    assert "Store has 10 available." in text


def _journey_step(offering: dict) -> dict:
    return {
        "offering_id": offering.get("offering_id"),
        "title": offering.get("activity_title") or "",
        "setup_min": _num(offering.get("setup_time_min")),
        "duration_min": _num(offering.get("standard_duration_min")),
        "method": str(offering.get("engagement_methods") or offering.get("delivery_mode") or ""),
    }


if __name__ == "__main__":
    _check_plain_reply()
    _check_items()
    _check_stock()
    print("consultant checks ok")
