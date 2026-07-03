import asyncio
from typing import List
from services.chat_parser import Chunk
from services.llm_handler import extract_from_chunk, merge_extractions, union_merge, EMPTY_SCHEMA


PARALLEL_BATCH_SIZE = 3


async def _process_chunk(chunk: Chunk, model: str = None, api_key: str = None) -> dict:
    code_context = ""
    all_code = [cb for msg in chunk.messages for cb in msg.code_blocks]
    if all_code:
        # Label each block with the placeholder used in raw_text so the LLM can
        # map [CODE_BLOCK_N] references back to the actual snippet.
        labeled = [f"[CODE_BLOCK_{i + 1}]:\n{code}" for i, code in enumerate(all_code)]
        code_context = "\n\nCODE BLOCKS IN THIS SEGMENT:\n" + "\n---\n".join(labeled)

    full_text = chunk.raw_text + code_context
    try:
        # Pass through model and api_key if they exist (will use defaults in llm_handler otherwise)
        kwargs = {}
        if model: kwargs["model"] = model
        if api_key: kwargs["api_key"] = api_key
        
        return await extract_from_chunk(full_text, **kwargs)
    except Exception as e:
        result = dict(EMPTY_SCHEMA)
        result["notes"] = [f"Extraction failed for chunk: {str(e)}"]
        return result


async def compress_chunks(chunks: List[Chunk], model: str = None, api_key: str = None) -> dict:
    if not chunks:
        return dict(EMPTY_SCHEMA)

    results = []
    for i in range(0, len(chunks), PARALLEL_BATCH_SIZE):
        batch = chunks[i:i + PARALLEL_BATCH_SIZE]
        batch_results = await asyncio.gather(
            *[_process_chunk(c, model, api_key) for c in batch]
        )
        results.extend(batch_results)

    if len(results) == 1:
        return results[0]

    kwargs = {}
    if model: kwargs["model"] = model
    if api_key: kwargs["api_key"] = api_key

    try:
        return await merge_extractions(results, **kwargs)
    except Exception:
        # LLM merge failed (e.g. truncated/invalid JSON) — fall back to a
        # deterministic union so the user still gets all extracted content.
        return union_merge(results)
