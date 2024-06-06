# Copyright (c) 2024, Arabella Gromova, Ivan Moskalenko, Kirill Ivanov, Anastasiia Kornilova
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

import os
import subprocess
import types
from pathlib import Path
from shutil import copytree

from common.adapter_base import AdapterBase
from common.config import Var


class Adapter(AdapterBase):
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
    ):
        super().__init__(input_dir, output_dir)

    def _convert_colmap_to_mvsnet(self):
        pass

    def _process(self):
        dense_folder = Path(self.input_dir) / Var.dense_name
        geom_consistency = True
        base_command = f"colmap patch_match_stereo"
        workspace_path = f"--workspace_path {dense_folder}"
        workspace_format = f"--workspace_format COLMAP"
        patch_match_stereo = f"--PatchMatchStereo.geom_consistency {geom_consistency}"
        gpu_index = f"--PatchMatchStereo.gpu_index=0,1"
        startup_command = " ".join(
            [
                base_command,
                workspace_path,
                workspace_format,
                patch_match_stereo,
                gpu_index,
            ]
        )
        subprocess.run(startup_command, shell=True)

    def _load_model(self):
        pass

    def _preprocess(self):
        pass

    def _postprocess(self):
        dense_folder = Path(self.input_dir) / Var.dense_name
        path_to_ply = Path(dense_folder) / Var.file_point_cloud
        base_command = f"colmap stereo_fusion"
        workspace_path = f"--workspace_path {dense_folder}"
        workspace_format = f"--workspace_format COLMAP"
        input_type = f"--input_type photometric"
        output_path = f"--output_path {path_to_ply}"
        startup_command = " ".join(
            [
                base_command,
                workspace_path,
                workspace_format,
                input_type,
                output_path,
            ]
        )
        subprocess.run(startup_command, shell=True)
        copytree(dense_folder, self.output_dir, dirs_exist_ok=True)
