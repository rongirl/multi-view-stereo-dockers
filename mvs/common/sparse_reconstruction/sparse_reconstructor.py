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


class SparseReconstructor:
    def __init__(
        self,
        database_path: Path,
        image_path: Path,
        output_path: Path,
        refine_principal_point: bool,
        tri_min_angle: float = 0.01,
        ignore_two_view_tracks: bool = False,
    ):
        self.database_path = database_path
        self.image_path = image_path
        self.output_path = output_path
        self.refine_principal_point = refine_principal_point
        self.tri_min_angle = tri_min_angle
        self.ignore_two_view_tracks = ignore_two_view_tracks

    def _get_startup_command(self) -> str:
        base_command = f"colmap mapper"
        database_param = f"--database_path {self.database_path}"
        images_param = f"--image_path {self.image_path}"
        output_path_param = f"--output_path {self.output_path}"
        refine_pp_param = (
            f"--Mapper.ba_refine_principal_point {int(self.refine_principal_point)}"
        )
        tri_min_angle_param = f"--Mapper.tri_min_angle {self.tri_min_angle}"
        ignore_two_view_tracks_param = (
            f"--Mapper.tri_ignore_two_view_tracks {int(self.ignore_two_view_tracks)}"
        )

        return " ".join(
            [
                base_command,
                database_param,
                images_param,
                output_path_param,
                refine_pp_param,
                tri_min_angle_param,
                ignore_two_view_tracks_param,
            ]
        )

    def get_sparse_reconstruction(self):
        startup_command = self._get_startup_command()
        subprocess.run(startup_command, shell=True)
