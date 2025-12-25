import json
import re


def parse_json_strict(text: str) -> dict:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError("Invalid JSON from model")
    return json.loads(m.group(0).strip())


def bullets_to_text(v):
    if v is None:
        return ""
    if isinstance(v, list):
        items = [str(x).strip() for x in v if str(x).strip()]
        return "\n".join([f"• {x}" for x in items])
    s = str(v).strip()
    if not s:
        return ""
    lines = [ln.strip() for ln in s.split("\n") if ln.strip()]
    out = []
    for ln in lines:
        if ln.startswith("•"):
            out.append(ln)
        else:
            out.append(f"• {ln}")
    return "\n".join(out)


def score_to_text(obj: dict) -> str:
    total = obj.get("score_total", None)
    breakdown = obj.get("score_breakdown", None)
    interp = str(obj.get("score_interpretation", "") or "").strip()

    if total is None and not isinstance(breakdown, dict) and not interp:
        return ""

    lines = []
    if total is not None:
        try:
            t = int(total)
        except Exception:
            t = None
        if t is not None:
            lines.append(f"Общая оценка: {t}/100")
            if t >= 85:
                lines.append("Уровень: сильный кандидат")
            elif t >= 70:
                lines.append("Уровень: уверенный, но есть зоны роста")
            elif t >= 55:
                lines.append("Уровень: средний, высокий риск отказа")
            else:
                lines.append("Уровень: слабая подача, высокий риск отказа")

    if isinstance(breakdown, dict):
        m = {
            "structure": "Структура",
            "specificity": "Конкретика",
            "logic": "Логика",
            "communication": "Коммуникация",
            "fit": "Соответствие роли",
        }
        parts = []
        for k, label in m.items():
            if k in breakdown and breakdown[k] is not None:
                try:
                    parts.append(f"{label}: {int(breakdown[k])}/20")
                except Exception:
                    pass
        if parts:
            lines.append("")
            lines.append("Разбор по критериям:")
            lines.extend([f"— {p}" for p in parts])

    if interp:
        lines.append("")
        lines.append(interp)

    return "\n".join(lines).strip()
