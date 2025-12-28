def build_user_context(user_id: str, parsed_texts: list[str]) -> str:
    """
    Builds a user context string by combining user ID and parsed texts.

    Args:
        user_id (str): The unique identifier for the user.
        parsed_texts (list[str]): A list of parsed text contents.
        
    Returns:
        str: The combined user context string.
    """
    header = f"""
            USER PROFILE CONTEXT
            ====================
            User ID: {user_id}
            This file contains consolidated personal data for downstream LLM agents.
            """
    body = "\n\n---\n\n".join(parsed_texts)

    final_text = header + "\n" + body
    return final_text
