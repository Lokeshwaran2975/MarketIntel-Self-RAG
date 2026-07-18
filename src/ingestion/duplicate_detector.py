from pathlib import Path

from src.utils.hash_utils import calculate_file_hash


class DuplicateDetector:

    def __init__(self):

        self.hashes = set()

    def is_duplicate(self, file_path: str | Path):

        file_hash = calculate_file_hash(file_path)

        if file_hash in self.hashes:

            return True

        self.hashes.add(file_hash)

        return False