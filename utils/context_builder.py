def build_user_context(user_id: str, parsed_texts: list[str]) -> str:
    """
    Builds a user context string by combining user ID and parsed texts.

    Args:
        user_id (str): The unique identifier for the user.
        parsed_texts (list[str]): A list of parsed text contents.
    """
    header = f"""
            USER PROFILE CONTEXT
            ====================
            This file contains consolidated personal data for downstream LLM agents.
            """
    body = "\n\n---\n\n".join(parsed_texts)

    final_text = header + body
    path = f"user_data/{user_id}user_context.txt"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(final_text)

    return path
