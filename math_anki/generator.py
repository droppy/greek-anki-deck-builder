"""Claude API integration for math hint generation."""
import json
import os
import re
import time
from typing import Dict, List, Optional

import keyring
from anthropic import Anthropic

from .cache import MathCardCache
from .config import DEFAULT_MODEL, HINT_PROMPT_PATH, ORDER_PROMPT_PATH
from .problems import MathProblem

KEYRING_SERVICE = "greek-anki"
KEYRING_USERNAME = "anthropic-api-key"

# Batch size for API calls
BATCH_SIZE = 20


def get_api_key() -> Optional[str]:
    """Resolve API key: keyring first, then env var."""
    key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    if key:
        return key
    return os.environ.get("ANTHROPIC_API_KEY")


def store_api_key(key: str) -> None:
    """Store API key in the OS credential store."""
    keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, key)


def delete_api_key() -> None:
    """Remove API key from the OS credential store."""
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except keyring.errors.PasswordDeleteError:
        pass


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)


def _extract_json(text: str) -> object:
    """Extract JSON (array or object) from Claude's response."""
    # 1. Try fenced code block
    m = _JSON_FENCE_RE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # 2. Find outermost [ ... ] or { ... }
    for open_ch, close_ch in [("[", "]"), ("{", "}")]:
        start = text.find(open_ch)
        if start != -1:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == open_ch:
                    depth += 1
                elif text[i] == close_ch:
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[start : i + 1])
                        except json.JSONDecodeError:
                            break

    raise ValueError(f"Could not extract JSON from response:\n{text[:500]}")


def _load_template(path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path.resolve()}")
    return path.read_text(encoding="utf-8")


def generate_hints_batch(
    problems: List[MathProblem],
    age: int,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    with_images: bool = False,
) -> List[dict]:
    """Generate hints for a batch of problems via Claude API.

    Returns list of dicts with keys: problem, hint, fun_fact, difficulty, image_desc (optional).
    """
    resolved_key = api_key or get_api_key()
    if not resolved_key:
        raise RuntimeError(
            "No API key found. Set one with:\n"
            "  python -m math_anki set-key\n"
            "Or set the ANTHROPIC_API_KEY environment variable."
        )

    client = Anthropic(api_key=resolved_key)
    template = _load_template(HINT_PROMPT_PATH)

    # Format problems as JSON list
    # For mirror problems, send the primary form (first line) to Claude
    problems_json = json.dumps(
        [{"problem": p.display_no_question.split("\n")[0], "answer": p.answer} for p in problems],
        ensure_ascii=False,
    )

    image_instruction = ""
    if with_images:
        image_instruction = (
            '\n- Also include an "image_desc" field: a short description of a fun cartoon '
            "illustration for this problem (e.g., \"A happy cat juggling 7 apples while "
            '5 more fall from a tree"). Keep under 150 characters.'
        )

    prompt = (
        template.replace("{age}", str(age))
        .replace("{problems}", problems_json)
        .replace("{with_images}", image_instruction)
    )

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()
    results = _extract_json(raw_text)
    if isinstance(results, dict):
        results = [results]
    if not isinstance(results, list):
        raise ValueError(f"Expected JSON array, got {type(results).__name__}")

    return results


def generate_hints(
    problems: List[MathProblem],
    age: int,
    cache: MathCardCache,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    with_images: bool = False,
    delay: float = 1.0,
    progress_callback=None,
) -> Dict[str, dict]:
    """Generate hints for problems, using cache and batching API calls.

    Returns dict of {problem_key: hint_data} for all problems.
    """
    # Check cache first
    all_keys = [p.key for p in problems]
    cached = cache.get_batch(all_keys, age)

    uncached = [p for p in problems if p.key not in cached]

    if progress_callback:
        progress_callback(
            f"[dim]{len(cached)} cached, {len(uncached)} to generate[/dim]"
        )

    # Batch uncached problems
    for i in range(0, len(uncached), BATCH_SIZE):
        batch = uncached[i : i + BATCH_SIZE]

        if progress_callback:
            progress_callback(
                f"Generating hints for batch {i // BATCH_SIZE + 1}"
                f"/{(len(uncached) + BATCH_SIZE - 1) // BATCH_SIZE}..."
            )

        results = generate_hints_batch(
            batch, age, model=model, api_key=api_key, with_images=with_images
        )

        # Match results back to problems by primary display string (first line)
        display_to_problem = {p.display_no_question.split("\n")[0]: p for p in batch}
        for item in results:
            problem_str = item.get("problem", "")
            prob = display_to_problem.get(problem_str)
            if prob is None:
                continue

            hint = item.get("hint", "")
            fun_fact = item.get("fun_fact")
            difficulty = item.get("difficulty")
            image_desc = item.get("image_desc")

            cache.store(
                prob.key, age, hint, fun_fact, difficulty, model, image_desc
            )
            cached[prob.key] = {
                "hint": hint,
                "fun_fact": fun_fact,
                "difficulty": difficulty,
                "image_desc": image_desc,
            }

        # Rate limiting between batches
        if i + BATCH_SIZE < len(uncached):
            time.sleep(delay)

    return cached


def suggest_ordering(
    problems: List[MathProblem],
    age: int,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
) -> List[str]:
    """Ask Claude to suggest pedagogical ordering for problems.

    Returns list of problem display strings in recommended order.
    """
    resolved_key = api_key or get_api_key()
    if not resolved_key:
        raise RuntimeError("No API key found.")

    client = Anthropic(api_key=resolved_key)
    template = _load_template(ORDER_PROMPT_PATH)

    problems_json = json.dumps(
        [p.display_no_question for p in problems], ensure_ascii=False
    )

    prompt = (
        template.replace("{age}", str(age)).replace("{problems}", problems_json)
    )

    response = client.messages.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()
    order = _extract_json(raw_text)

    if not isinstance(order, list):
        raise ValueError(f"Expected JSON array, got {type(order).__name__}")

    return order
