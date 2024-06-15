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

import copy
import os
import subprocess
import types
from pathlib import Path

import cv2
import numpy as np
import open3d as o3d
from colmap2mvsnet_acm import processing_single_scene
from common.adapter_base import AdapterBase
from common.association import hidden_removal_points, projection_point
from common.camera import read_camera
from common.config import Var


class Adapter(AdapterBase):
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
    ):
        super().__init__(input_dir, output_dir)
        self.images_cams = {}

    def _convert_colmap_to_mvsnet(self):
        dense_folder = Path(self.input_dir) / Var.dense_name
        args = {
            "dense_folder": f"{dense_folder}",
            "save_folder": f"{self.output_dir}",
            "max_d": 192,
            "interval_scale": 1,
            "theta0": 5,
            "sigma1": 1,
            "sigma2": 10,
            "model_ext": ".bin",
        }
        args = types.SimpleNamespace(**args)
        Path(args.save_folder).mkdir(exist_ok=True)
        processing_single_scene(args, self.images_cams)

    def _process(self):
        startup_command = f"./build/ACMMP {self.output_dir}"
        subprocess.run(startup_command, shell=True)

    def _load_model(self):
        pass

    def _preprocess(self):
        pass

    def _postprocess(self):
        association_path = Path(self.input_dir) / Var.association
        if not association_path.exists():
            return
        acmmp_ply = Path(self.output_dir) / Var.acmmp / Var.acmmp_ply
        acmmp_pcd = Path(self.output_dir) / Var.acmmp / Var.acmmp_pcd
        cams_path = Path(self.output_dir) / Var.cameras
        association_ply = Path(self.output_dir) / "association.ply"
        print(acmmp_ply)
        pcd = o3d.io.read_point_cloud(str(acmmp_ply))
        o3d.io.write_point_cloud(str(acmmp_pcd), pcd)
        del pcd
        pcd = o3d.io.read_point_cloud(str(acmmp_pcd))
        projection_points = np.vectorize(
            projection_point, signature="(), (), () -> (x)"
        )
        for file in os.scandir(association_path):
            if file.name[:-4] in self.images_cams.keys():
                cam = self.images_cams[file.name[:-4]]
                img_path = Path(association_path) / file.name
                img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
                cams_file = "".join([str(Path(cams_path) / cam), Var.cameras_format])
                camera = read_camera(str(cams_file))
                height, width = img.shape[:-1]
                trans = np.asarray(
                    [
                        [camera.R[0], camera.R[1], camera.R[2], camera.t[0]],
                        [camera.R[3], camera.R[4], camera.R[5], camera.t[1]],
                        [camera.R[6], camera.R[7], camera.R[8], camera.t[2]],
                        [0, 0, 0, 1],
                    ]
                )
                pcd_copy = copy.deepcopy(pcd)
                pcd_copy.transform(trans)
                indices = hidden_removal_points(pcd_copy)
                res = projection_points(indices, pcd_copy, camera)
                for i in range(len(res)):
                    x, y, z = res[i]
                    if 0 <= x < width and 0 <= y < height:
                        blue, green, red = img[int(y)][int(x)]
                        np.asarray(pcd.colors)[indices[i]] = (
                            np.array([red, green, blue]) / 255.0
                        )
                del img, pcd_copy
        o3d.io.write_point_cloud(str(association_ply), pcd, write_ascii=False)
        del pcd
