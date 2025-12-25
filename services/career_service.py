from prompts.base import SYSTEM_RULES
from prompts.career_diag import PROMPT as DIAG_PROMPT
from prompts.career_full import PROMPT as FULL_PROMPT
from services.ai import chat
from services.utils import parse_json_strict


def run(service: str, user_text: str) -> dict:
    if service == "career_diag":
        prompt = DIAG_PROMPT + "\n\nВходные данные пользователя:\n" + user_text
    else:
        prompt = FULL_PROMPT + "\n\nВходные данные пользователя:\n" + user_text
    return parse_json_strict(chat(prompt=prompt, system=SYSTEM_RULES))
