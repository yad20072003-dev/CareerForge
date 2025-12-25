from prompts.base import SYSTEM_RULES
from prompts.competitiveness import PROMPT
from services.ai import chat
from services.utils import parse_json_strict


def run(user_text: str) -> dict:
    prompt = PROMPT + "\n\nДанные пользователя:\n" + user_text
    return parse_json_strict(chat(prompt=prompt, system=SYSTEM_RULES))
