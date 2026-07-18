import re


TABLE_PATTERNS = [
    r"\$\s?\d[\d,]*",                 # $109,158
    r"\d[\d,]*\s*%",                  # 14 %
    r"\b202[0-9]\b",                  # Years
    r"\b20\d{2}\b",
]


def is_table(text: str) -> bool:
    """
    Detect whether a chunk is likely to be a financial table.
    """

    if not text:
        return False

    score = 0

    # Many numbers
    number_count = len(re.findall(r"\d[\d,]*", text))
    if number_count >= 8:
        score += 1

    # Currency / Percent / Years
    for pattern in TABLE_PATTERNS:
        if re.search(pattern, text):
            score += 1

    # Lots of short lines
    lines = text.splitlines()

    short_lines = sum(
        1 for line in lines
        if len(line.strip()) < 80
    )

    if short_lines > len(lines) * 0.5:
        score += 1

    return score >= 3