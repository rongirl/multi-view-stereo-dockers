# Copyright (c) 2022, Arabella Gromova, Ivan Moskalenko, Kirill Ivanov, Anastasiia Kornilova
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
