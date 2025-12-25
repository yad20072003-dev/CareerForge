from prompts.base import SYSTEM_RULES
from prompts.mock import QUESTIONS_PROMPT, EVAL_PROMPT
from services.ai import chat
from services.utils import parse_json_strict


def generate_questions(context: str, n: int) -> list[str]:
    prompt = QUESTIONS_PROMPT.format(n=n) + "\n\nКонтекст кандидата:\n" + context
    obj = parse_json_strict(chat(prompt=prompt, system=SYSTEM_RULES))
    qs = obj.get("questions", [])
    if not isinstance(qs, list):
        return []
    out = []
    for q in qs:
        q = str(q).strip()
        if q:
            out.append(q)
    return out[:n]


def evaluate(context: str, questions: list[str], answers: list[str]) -> dict:
    qa_lines = []
    for i, (q, a) in enumerate(zip(questions, answers), start=1):
        qa_lines.append(f"Q{i}: {q}\nA{i}: {a}")
    transcript = "\n\n".join(qa_lines)

    prompt = EVAL_PROMPT + "\n\nКонтекст кандидата:\n" + context + "\n\nДиалог:\n" + transcript
    obj = parse_json_strict(chat(prompt=prompt, system=SYSTEM_RULES))

    if not str(obj.get("transcript") or "").strip():
        obj["transcript"] = transcript
    return obj
