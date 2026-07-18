import json
from pathlib import Path

from src.utils.hash_utils import calculate_file_hash


INDEX_FILE = Path("chroma_db/index.json")


class IndexTracker:

    def __init__(self):

        INDEX_FILE.parent.mkdir(exist_ok=True)

        if INDEX_FILE.exists():

            with open(INDEX_FILE, "r") as f:

                self.index = json.load(f)

        else:

            self.index = {}

    def should_index(self, file_path):

        file_path = Path(file_path)

        current_hash = calculate_file_hash(file_path)

        modified_time = file_path.stat().st_mtime

        key = str(file_path)

        if key not in self.index:

            return True

        stored = self.index[key]

        return not (

            stored["hash"] == current_hash

            and stored["modified"] == modified_time

        )

    def update(self, file_path):

        file_path = Path(file_path)

        self.index[str(file_path)] = {

            "hash": calculate_file_hash(file_path),

            "modified": file_path.stat().st_mtime

        }

    def save(self):

        with open(INDEX_FILE, "w") as f:

            json.dump(

                self.index,

                f,

                indent=4
            )