import re


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while preserving table structure.
    """

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing spaces at the end of each line
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    # Collapse multiple spaces and tabs only
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()