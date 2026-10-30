import hashlib
import json
import os
import time
from pathlib import Path

import groq
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
CACHE_DIR = Path(".cache/llm")
LOG_FILE = Path("reports/llm_log.jsonl")

_client = groq.Groq()


def complete(system: str, user: str, prompt_version: str, max_tokens: int = 8000) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(exist_ok=True)

    key = hashlib.sha256(
        json.dumps([MODEL, system, user], ensure_ascii=False).encode()
    ).hexdigest()
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))["text"]

    for attempt in range(4):
        try:
            start = time.time()
            resp = _client.chat.completions.create(
                model=MODEL,
                max_tokens=max_tokens,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            break
        except (groq.RateLimitError, groq.APIConnectionError,
                groq.InternalServerError):
            if attempt == 3:
                raise
            time.sleep(2**attempt)

    text = resp.choices[0].message.content
    cache_file.write_text(json.dumps({"text": text}, ensure_ascii=False), encoding="utf-8")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "model": MODEL,
            "prompt_version": prompt_version,
            "input_tokens": resp.usage.prompt_tokens,
            "output_tokens": resp.usage.completion_tokens,
            "duration_s": round(time.time() - start, 2),
        }) + "\n")
    return text
