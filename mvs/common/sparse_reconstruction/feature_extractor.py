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

from common.config import Var


class FeatureExtractor:
    def __init__(
        self,
        database_path: Path,
        image_path: Path,
        init_camera_params: bool,
        one_camera_per_folder: bool,
    ):
        self.database_path = database_path
        self.image_path = image_path
        self.init_camera_params = init_camera_params
        self.one_camera_per_folder = one_camera_per_folder

        if not one_camera_per_folder and init_camera_params:
            raise ValueError(
                "When using initial camera parameters, you should set one_camera_per_folder=True"
            )

    def _get_startup_commands(self):
        base_command = f"colmap feature_extractor"
        database_param = f"--database_path {self.database_path}"
        images_param = f"--image_path {self.image_path}"
        
        subfolders = sorted(self.image_path.iterdir())
        image_list_paths = [subfolder / Var.image_list_name for subfolder in subfolders]
        intrinsics_paths = [subfolder / Var.intrinsics_name  for subfolder in subfolders]
        startup_commands = []
        for image_list_path, intrinsics_path in zip(image_list_paths, intrinsics_paths):
            image_list_param = f"--image_list_path {image_list_path}"
            startup_command = [
                base_command,
                database_param,
                images_param,
                image_list_param,
            ]

            if self.one_camera_per_folder:
                single_cam = f"--ImageReader.single_camera 1"
                startup_command.append(single_cam)

            if self.init_camera_params:
                with open(intrinsics_path) as f:
                    intrinsics = f.readline()
                intrinsics = intrinsics.split()
                intrinsics = ", ".join(intrinsics)
                camera_param = f'--ImageReader.camera_params "{intrinsics}"'
                startup_command.append(camera_param)
         
            startup_commands.append(" ".join(startup_command))

        return startup_commands

    def calculate_features(self):
        startup_commands = self._get_startup_commands()
        for startup_command in startup_commands:
            subprocess.run(startup_command, shell=True)

