def format_context_pack(data: dict) -> str:
    lines = ["=== CONTEXT PACK START ===", ""]

    if data.get("user_goal"):
        lines += ["[GOAL]", data["user_goal"], ""]

    if data.get("tech_stack"):
        lines += ["[STACK]", ", ".join(data["tech_stack"]), ""]

    if data.get("constraints"):
        lines += ["[CONSTRAINTS]"]
        for c in data["constraints"]:
            lines.append(f"• {c}")
        lines.append("")

    if data.get("decisions"):
        lines += ["[DECISIONS MADE]"]
        for d in data["decisions"]:
            lines.append(f"• {d}")
        lines.append("")

    if data.get("problems"):
        lines += ["[KNOWN ISSUES / ERRORS]"]
        for p in data["problems"]:
            lines.append(f"• {p}")
        lines.append("")

    if data.get("solutions"):
        lines += ["[SOLUTIONS / FIXES APPLIED]"]
        for s in data["solutions"]:
            lines.append(f"• {s}")
        lines.append("")

    if data.get("code_snippets"):
        lines += ["[KEY CODE]"]
        for snippet in data["code_snippets"]:
            label = snippet.get("label", "Snippet")
            code = snippet.get("code", "")
            lines.append(f"// {label}")
            lines.append("```")
            lines.append(code)
            lines.append("```")
            lines.append("")

    if data.get("notes"):
        lines += ["[IMPORTANT NOTES]"]
        for n in data["notes"]:
            lines.append(f"• {n}")
        lines.append("")

    lines.append("=== CONTEXT PACK END ===")
    lines.append("")
    lines.append("Use this context pack to continue the project without losing any prior context.")

    return "\n".join(lines)
