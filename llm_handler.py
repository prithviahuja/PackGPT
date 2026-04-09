import json
import re
import asyncio
import os
from groq import AsyncGroq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EXTRACTION_SYSTEM_PROMPT = """You are an expert context extraction engine. Your job is to analyze chat conversations between a user and an AI assistant and extract STRUCTURED INTELLIGENCE — not summaries.

You will return STRICT JSON only. No prose. No markdown. No explanation outside the JSON.

Extract the following fields:
- user_goal: The primary objective the user is trying to achieve (1-3 sentences max, dense)
- tech_stack: Array of technologies, frameworks, languages, tools mentioned
- decisions: Array of architectural/technical decisions made during the conversation
- problems: Array of errors, bugs, blockers encountered (include error messages if mentioned)
- solutions: Array of fixes, workarounds, approaches that resolved problems
- code_snippets: Array of objects {label: "what this does", code: "the actual code"}
- constraints: Array of limitations, requirements, or boundaries established
- notes: Array of important facts, warnings, gotchas, or context that doesn't fit above

Rules:
- Be DENSE. Omit filler. Every word must carry information.
- Preserve technical precision. Never paraphrase error messages, function names, or config values.
- If something was tried and failed, put it in problems. If it succeeded, put it in solutions.
- For code_snippets, only include truly important snippets (not trivial examples).
- decisions should capture WHY something was chosen, not just what.
- Merge duplicate information. Never repeat the same fact twice.

Return ONLY this JSON structure:
{
  "user_goal": "string",
  "tech_stack": ["string"],
  "decisions": ["string"],
  "problems": ["string"],
  "solutions": ["string"],
  "code_snippets": [{"label": "string", "code": "string"}],
  "constraints": ["string"],
  "notes": ["string"]
}"""


MERGE_SYSTEM_PROMPT = """You are a deduplication and merging engine. You receive multiple JSON objects extracted from chunks of the same conversation.

Merge them into ONE unified JSON object. Rules:
- user_goal: Synthesize into the most complete, accurate single statement
- tech_stack: Union of all arrays, deduplicated
- decisions, problems, solutions, constraints, notes: Merge arrays, remove duplicates, combine entries that say the same thing
- code_snippets: Keep only the most important/unique ones, remove duplicates
- Preserve ALL unique information. Do not discard anything that appears in only one chunk.
- Output STRICT JSON only. Same schema as input.

Schema:
{
  "user_goal": "string",
  "tech_stack": ["string"],
  "decisions": ["string"],
  "problems": ["string"],
  "solutions": ["string"],
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


async def extract_from_chunk(chunk_text: str, model: str = "llama-3.3-70b-versatile", api_key: str = None) -> dict:
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not found in environment or provided")
    
    client = AsyncGroq(api_key=key)
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract structured intelligence from this chat segment:\n\n{chunk_text}"}
        ],
        temperature=0.1,
        max_tokens=2000,
    )
    return _parse_json_response(response.choices[0].message.content)


async def merge_extractions(extractions: list, model: str = "llama-3.3-70b-versatile", api_key: str = None) -> dict:
    if len(extractions) == 1:
        return extractions[0]

    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not found in environment or provided")

    client = AsyncGroq(api_key=key)
    payload = json.dumps(extractions, indent=2)
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": MERGE_SYSTEM_PROMPT},
            {"role": "user", "content": f"Merge these extracted JSON objects into one:\n\n{payload}"}
        ],
        temperature=0.1,
        max_tokens=2500,
    )
    return _parse_json_response(response.choices[0].message.content)


EMPTY_SCHEMA = {
    "user_goal": "",
    "tech_stack": [],
    "decisions": [],
    "problems": [],
    "solutions": [],
    "code_snippets": [],
    "constraints": [],
    "notes": []
}
