import re
from dataclasses import dataclass, field
from typing import List

CHUNK_TOKEN_LIMIT = 2000
AVG_CHARS_PER_TOKEN = 4
CHUNK_CHAR_LIMIT = CHUNK_TOKEN_LIMIT * AVG_CHARS_PER_TOKEN


@dataclass
class Message:
    role: str
    content: str
    code_blocks: List[str] = field(default_factory=list)


@dataclass
class Chunk:
    messages: List[Message]
    raw_text: str


# Internal sentinel for a code block. It is renumbered globally per chunk (in
# document order) when raw_text is assembled, so placeholders line up with the
# flattened code-block list the compressor builds.
_CODE_SENTINEL = "\x00CODE_BLOCK\x00"


def _extract_code_blocks(text: str):
    """Replace fenced code blocks with a sentinel placeholder and return the
    extracted snippets in document order."""
    pattern = re.compile(r"```[\w]*\n?(.*?)```", re.DOTALL)
    blocks: List[str] = []

    def _replace(match):
        block = match.group(1).strip()
        if not block:
            return ""
        blocks.append(block)
        return _CODE_SENTINEL

    cleaned = pattern.sub(_replace, text)
    return cleaned, blocks


def _number_code_placeholders(text: str) -> str:
    """Replace sentinels with sequential [CODE_BLOCK_N] markers in order."""
    counter = {"n": 0}

    def _replace(_match):
        counter["n"] += 1
        return f"[CODE_BLOCK_{counter['n']}]"

    return re.sub(re.escape(_CODE_SENTINEL), _replace, text)


def _detect_role_lines(text: str) -> List[Message]:
    patterns = [
        (re.compile(r"^(You|User|Human)\s*[:：]\s*", re.IGNORECASE | re.MULTILINE), "user"),
        (re.compile(r"^(ChatGPT|Assistant|Claude|AI|GPT)\s*[:：]\s*", re.IGNORECASE | re.MULTILINE), "assistant"),
    ]

    splits = []
    for pattern, role in patterns:
        for m in pattern.finditer(text):
            splits.append((m.start(), m.end(), role))

    if not splits:
        cleaned, code_blocks = _extract_code_blocks(text.strip())
        return [Message(role="unknown", content=cleaned.strip(), code_blocks=code_blocks)]

    splits.sort(key=lambda x: x[0])
    messages = []

    for i, (start, end, role) in enumerate(splits):
        next_start = splits[i + 1][0] if i + 1 < len(splits) else len(text)
        raw_content = text[end:next_start].strip()
        cleaned_content, code_blocks = _extract_code_blocks(raw_content)
        messages.append(Message(role=role, content=cleaned_content.strip(), code_blocks=code_blocks))

    return messages


def _split_oversized_message(msg: Message, limit_chars: int) -> List[Message]:
    """Split a single message whose content exceeds the chunk limit into several
    smaller messages so very large inputs (e.g. a marker-less paste) still get
    chunked instead of producing one giant LLM call."""
    if len(msg.content) <= limit_chars:
        return [msg]

    pieces: List[Message] = []
    content = msg.content
    for i in range(0, len(content), limit_chars):
        slice_text = content[i:i + limit_chars]
        # Attach the original code blocks only to the first piece to avoid
        # duplicating them across every slice.
        code = msg.code_blocks if i == 0 else []
        pieces.append(Message(role=msg.role, content=slice_text, code_blocks=code))
    return pieces


def _chunk_messages(messages: List[Message], token_limit: int) -> List[Chunk]:
    limit_chars = token_limit * AVG_CHARS_PER_TOKEN

    # Break apart any single message that is larger than the chunk budget.
    normalized: List[Message] = []
    for msg in messages:
        normalized.extend(_split_oversized_message(msg, limit_chars))

    chunks = []
    current: List[Message] = []
    current_chars = 0

    def _build_raw(msgs: List[Message]) -> str:
        joined = "\n".join(f"[{m.role.upper()}]: {m.content}" for m in msgs)
        return _number_code_placeholders(joined)

    for msg in normalized:
        msg_len = len(msg.content) + sum(len(c) for c in msg.code_blocks)
        if current_chars + msg_len > limit_chars and current:
            chunks.append(Chunk(messages=current, raw_text=_build_raw(current)))
            current = []
            current_chars = 0
        current.append(msg)
        current_chars += msg_len

    if current:
        chunks.append(Chunk(messages=current, raw_text=_build_raw(current)))

    return chunks


def parse_chat(raw_text: str) -> List[Chunk]:
    messages = _detect_role_lines(raw_text)
    return _chunk_messages(messages, CHUNK_TOKEN_LIMIT)
