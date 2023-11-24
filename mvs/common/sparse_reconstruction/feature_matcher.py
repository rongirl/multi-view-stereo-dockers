import subprocess

from pathlib import Path


class FeatureMatcher:
    def __init__(self, database_path: Path):
        self.database_path = database_path

    def _get_startup_command(self) -> str:
        base_command = f"colmap exhaustive_matcher"
        database_param = f"--database_path {self.database_path}"

        return " ".join([base_command, database_param])

    def match_features(self):
        startup_command = self._get_startup_command()
        subprocess.run(startup_command, shell=True)
