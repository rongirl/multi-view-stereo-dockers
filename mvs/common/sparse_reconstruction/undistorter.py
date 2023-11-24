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


class Undistorter:
    def __init__(self, image_path: Path, sparse_path: Path, dense_path: Path):
        self.image_path = image_path
        self.sparse_path = sparse_path
        self.dense_path = dense_path

    def _get_startup_command(self) -> str:
        base_command = f"colmap image_undistorter"
        images_param = f"--image_path {self.image_path}"
        sparse_path_param = f"--input_path {self.sparse_path}/0"
        dense_path_param = f"--output_path {self.dense_path}"
        output_type_param = "--output_type COLMAP"

        return " ".join(
            [
                base_command,
                images_param,
                sparse_path_param,
                dense_path_param,
                output_type_param,
            ]
        )

    def undistort(self):
        startup_command = self._get_startup_command()

        subprocess.run(startup_command, shell=True)
