from prompts.base import SYSTEM_RULES
from prompts.resume_create import PROMPT as CREATE_PROMPT
from prompts.resume_audit import PROMPT as AUDIT_PROMPT
from services.ai import chat
from services.utils import parse_json_strict


def run(service: str, user_text: str) -> dict:
    if service == "resume_create":
        prompt = CREATE_PROMPT + "\n\nДанные пользователя (опыт/навыки/цель):\n" + user_text
    else:
        prompt = AUDIT_PROMPT + "\n\nТекст резюме пользователя:\n" + user_text
    return parse_json_strict(chat(prompt=prompt, system=SYSTEM_RULES))
