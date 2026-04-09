import re
from dataclasses import dataclass, field
from typing import List

CHUNK_TOKEN_LIMIT = 3000
AVG_CHARS_PER_TOKEN = 4


@dataclass
class Message:
    role: str
    content: str
    code_blocks: List[str] = field(default_factory=list)


@dataclass
class Chunk:
    messages: List[Message]
    raw_text: str


def _extract_code_blocks(text: str):
    pattern = re.compile(r"```[\w]*\n?(.*?)```", re.DOTALL)
    blocks = pattern.findall(text)
    cleaned = pattern.sub("[CODE_BLOCK]", text)
    return cleaned, [b.strip() for b in blocks if b.strip()]


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
        return [Message(role="unknown", content=text.strip())]

    splits.sort(key=lambda x: x[0])
    messages = []

    for i, (start, end, role) in enumerate(splits):
        next_start = splits[i + 1][0] if i + 1 < len(splits) else len(text)
        raw_content = text[end:next_start].strip()
        cleaned_content, code_blocks = _extract_code_blocks(raw_content)
        messages.append(Message(role=role, content=cleaned_content.strip(), code_blocks=code_blocks))

    return messages


def _chunk_messages(messages: List[Message], token_limit: int) -> List[Chunk]:
    chunks = []
    current: List[Message] = []
    current_chars = 0
    limit_chars = token_limit * AVG_CHARS_PER_TOKEN

    for msg in messages:
        msg_len = len(msg.content) + sum(len(c) for c in msg.code_blocks)
        if current_chars + msg_len > limit_chars and current:
            raw = "\n".join(f"[{m.role.upper()}]: {m.content}" for m in current)
            chunks.append(Chunk(messages=current, raw_text=raw))
            current = []
            current_chars = 0
        current.append(msg)
        current_chars += msg_len

    if current:
        raw = "\n".join(f"[{m.role.upper()}]: {m.content}" for m in current)
        chunks.append(Chunk(messages=current, raw_text=raw))

    return chunks


def parse_chat(raw_text: str) -> List[Chunk]:
    messages = _detect_role_lines(raw_text)
    return _chunk_messages(messages, CHUNK_TOKEN_LIMIT)
