import re
from pathlib import Path


# ============================================================
# Companies
# ============================================================

COMPANIES = {
    "apple": "APPLE",
    "aapl": "APPLE",

    "microsoft": "MICROSOFT",
    "msft": "MICROSOFT",

    "nvidia": "NVIDIA",
    "nvda": "NVIDIA",

    "tesla": "TESLA",
    "tsla": "TESLA",

    "amazon": "AMAZON",
    "amzn": "AMAZON",

    "alphabet": "ALPHABET",
    "google": "ALPHABET",
}


# ============================================================
# Document Priority
# ============================================================

DOCUMENT_PRIORITY = {

    "Annual Report": 100,

    "10-K": 95,

    "10-Q": 90,

    "Financial Statement": 85,

    "Quarterly Presentation": 80,

    "Presentation": 75,

    "8-K": 70,

    "Press Release": 60,

    "News": 50,

    "Unknown": 0,

}


# ============================================================
# Company
# ============================================================

def extract_company(filename: str, folder: str):

    filename = filename.lower()
    folder = folder.lower()

    for keyword, company in COMPANIES.items():

        if keyword in filename:
            return company

        if keyword in folder:
            return company

    return "UNKNOWN"


# ============================================================
# Document Year
# ============================================================

def extract_document_year(filename: str):

    match = re.search(r"(20\d{2})", filename)

    if match:
        return int(match.group())

    return None


# ============================================================
# Quarter
# ============================================================

def extract_quarter(filename: str):

    filename = filename.upper()

    match = re.search(r"Q([1-4])", filename)

    if match:
        return f"Q{match.group(1)}"

    return None


# ============================================================
# Document Type
# ============================================================

def extract_document_type(filename: str):

    filename = filename.lower()

    if "annual" in filename:
        return "Annual Report"

    if "10-k" in filename or "10k" in filename:
        return "10-K"

    if "10-q" in filename or "10q" in filename:
        return "10-Q"

    if "financial" in filename:
        return "Financial Statement"

    if "presentation" in filename:
        return "Quarterly Presentation"

    if "earnings" in filename:
        return "Quarterly Presentation"

    if "8-k" in filename or "8k" in filename:
        return "8-K"

    if "press" in filename:
        return "Press Release"

    return "Unknown"


# ============================================================
# Metadata
# ============================================================

def extract_metadata(file_path):

    path = Path(file_path)

    filename = path.name

    folder = path.parent.name

    document_type = extract_document_type(filename)

    document_year = extract_document_year(filename)

    metadata = {

        "company": extract_company(
            filename,
            folder
        ),

        # Backward compatibility
        "year": document_year,

        # Preferred field
        "document_year": document_year,

        "quarter": extract_quarter(
            filename
        ),

        "document_type": document_type,

        "priority": DOCUMENT_PRIORITY.get(
            document_type,
            0
        ),

        "source_folder": folder,

        "file_name": filename,

    }

    return metadata