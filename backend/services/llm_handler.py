import json
import re
import os
from groq import AsyncGroq
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default cap on generated tokens. The merge step gets a larger budget because
# it may need to emit a union of many chunk extractions in a single JSON object.
DEFAULT_MAX_OUTPUT_TOKENS = 2500
MERGE_MAX_OUTPUT_TOKENS = 8192

EXTRACTION_SYSTEM_PROMPT = """You are an expert context extraction engine. Your job is to analyze chat conversations or development notes and extract STRUCTURED INTELLIGENCE — not summaries.

You will return STRICT JSON only. No prose. No markdown. No explanation outside the JSON.

Extract the following fields:
- goal: The primary objective being achieved (1-3 sentences max, dense)
- tech_stack: Array of technologies, frameworks, languages, tools mentioned
- key_decisions: Array of architectural/technical decisions made
- problems_faced: Array of errors, bugs, blockers encountered
- solutions_applied: Array of fixes, workarounds, or approaches that resolved problems
- code_snippets: Array of objects {"label": "what this does", "code": "the actual code"}
- constraints: Array of limitations, requirements, or boundaries established
- notes: Array of important facts, warnings, gotchas, or context that doesn't fit above

Rules:
- Be DENSE. Omit filler. Every word must carry information.
- Preserve technical precision. Never paraphrase error messages, function names, or config values.
- If something was tried and failed, put it in problems_faced. If it succeeded, put it in solutions_applied.
- For code_snippets, only include truly important snippets (not trivial examples).
- key_decisions should capture WHY something was chosen, not just what.
- Merge duplicate information. Never repeat the same fact twice.

Return ONLY this JSON structure:
{
  "goal": "string",
  "tech_stack": ["string"],
  "key_decisions": ["string"],
  "problems_faced": ["string"],
  "solutions_applied": ["string"],
  "code_snippets": [{"label": "string", "code": "string"}],
  "constraints": ["string"],
  "notes": ["string"]
}"""

MERGE_SYSTEM_PROMPT = """You are a deduplication and merging engine. You receive multiple JSON objects extracted from chunks of the same conversation.

Merge them into ONE unified JSON object. Rules:
- goal: Synthesize into the most complete, accurate single statement
- tech_stack: Union of all arrays, deduplicated
- key_decisions, problems_faced, solutions_applied, constraints, notes: Merge arrays, remove duplicates, combine entries that say the same thing
- code_snippets: Keep only the most important/unique ones, remove duplicates
- Preserve ALL unique information. Do not discard anything that appears in only one chunk.
- Output STRICT JSON only. Same schema as input.

Schema:
{
  "goal": "string",
  "tech_stack": ["string"],
  "key_decisions": ["string"],
  "problems_faced": ["string"],
  "solutions_applied": ["string"],
  "code_snippets": [{"label": "string", "code": "string"}],
  "constraints": ["string"],
  "notes": ["string"]
}"""

def _parse_json_response(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from LLM response: {text[:300]}")

async def _call_gemini(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
) -> str:
    client = genai.Client(api_key=api_key)

    response = await client.aio.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,
            max_output_tokens=max_output_tokens,
            # Force a raw JSON response so parsing is reliable.
            response_mime_type="application/json",
        ),
    )
    return response.text

async def _call_groq(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
) -> str:
    client = AsyncGroq(api_key=api_key)
    response = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=max_output_tokens,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content

async def extract_from_chunk(chunk_text: str, model: str = "gemini-3-flash-preview", api_key: str = None) -> dict:
    user_prompt = f"Extract structured intelligence from this chat segment:\n\n{chunk_text}"
    
    if "gemini" in model.lower():
        # Handle empty strings from UI explicitly
        key = api_key if api_key and api_key.strip() else os.getenv("GEMINI_API_KEY")
        if not key: raise ValueError("GEMINI_API_KEY not found")
        content = await _call_gemini(model, EXTRACTION_SYSTEM_PROMPT, user_prompt, key)
    else:
        key = api_key if api_key and api_key.strip() else os.getenv("GROQ_API_KEY")
        if not key: raise ValueError("GROQ_API_KEY not found")
        content = await _call_groq(model, EXTRACTION_SYSTEM_PROMPT, user_prompt, key)
        
    return _parse_json_response(content)

async def merge_extractions(extractions: list, model: str = "gemini-3-flash-preview", api_key: str = None) -> dict:
    if len(extractions) == 1:
        return extractions[0]

    payload = json.dumps(extractions, indent=2)
    user_prompt = f"Merge these extracted JSON objects into one:\n\n{payload}"

    if "gemini" in model.lower():
        key = api_key if api_key and api_key.strip() else os.getenv("GEMINI_API_KEY")
        if not key: raise ValueError("GEMINI_API_KEY not found")
        content = await _call_gemini(model, MERGE_SYSTEM_PROMPT, user_prompt, key, MERGE_MAX_OUTPUT_TOKENS)
    else:
        key = api_key if api_key and api_key.strip() else os.getenv("GROQ_API_KEY")
        if not key: raise ValueError("GROQ_API_KEY not found")
        content = await _call_groq(model, MERGE_SYSTEM_PROMPT, user_prompt, key, MERGE_MAX_OUTPUT_TOKENS)

    return _parse_json_response(content)

EMPTY_SCHEMA = {
    "goal": "",
    "tech_stack": [],
    "key_decisions": [],
    "problems_faced": [],
    "solutions_applied": [],
    "code_snippets": [],
    "constraints": [],
    "notes": []
}

_LIST_FIELDS = [
    "tech_stack",
    "key_decisions",
    "problems_faced",
    "solutions_applied",
    "constraints",
    "notes",
]


def union_merge(extractions: list) -> dict:
    """Deterministic, no-LLM merge used as a fallback when the LLM merge fails.

    Concatenates list fields (de-duplicated, order-preserving), keeps the first
    non-empty goal, and de-duplicates code snippets by their code body.
    """
    merged = {
        "goal": "",
        "tech_stack": [],
        "key_decisions": [],
        "problems_faced": [],
        "solutions_applied": [],
        "code_snippets": [],
        "constraints": [],
        "notes": [],
    }
    seen_lists = {field: set() for field in _LIST_FIELDS}
    seen_code = set()

    for extraction in extractions:
        if not isinstance(extraction, dict):
            continue
        if not merged["goal"] and extraction.get("goal"):
            merged["goal"] = extraction["goal"]
        for field in _LIST_FIELDS:
            for item in extraction.get(field, []) or []:
                key_item = item if isinstance(item, str) else json.dumps(item, sort_keys=True)
                if key_item not in seen_lists[field]:
                    seen_lists[field].add(key_item)
                    merged[field].append(item)
        for snippet in extraction.get("code_snippets", []) or []:
            code = snippet.get("code", "") if isinstance(snippet, dict) else ""
            if code and code not in seen_code:
                seen_code.add(code)
                merged["code_snippets"].append(snippet)

    return merged
