import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask(system, prompt):
    r = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role":"system","content":system},
            {"role":"user","content":prompt}
        ],
        temperature=0.4
    )
    return r.choices[0].message.content
