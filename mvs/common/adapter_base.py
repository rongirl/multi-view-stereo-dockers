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

import shutil

from pathlib import Path
from abc import ABC, abstractmethod

from common.config import Var
from common.sparse_reconstruction.preprocessing import get_intrinsics_from_report
from common.sparse_reconstruction.feature_extractor import FeatureExtractor
from common.sparse_reconstruction.feature_matcher import FeatureMatcher
from common.sparse_reconstruction.sparse_reconstructor import SparseReconstructor
from common.sparse_reconstruction.undistorter import Undistorter


class AdapterBase(ABC):
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def run(self):
        self._preprocess()
        self._sparse_reconstruction()
        self._convert_colmap_to_mvsnet()
        self._load_model()
        self._process()
        self._postprocess()

    def _preprocess(self):
        workdir = Path(self.input_dir)

        path_to_raw_images = workdir / Var.raw_images_name
        camera_a308_report = workdir / Var.a308_report_name
        camera_a311_report = workdir / Var.a311_report_name

        path_to_preprocessed = workdir / Var.images_name
        if path_to_preprocessed.exists():
            shutil.rmtree(path_to_preprocessed)
        path_to_preprocessed.mkdir(exist_ok=False)
        intrinsics = dict()
        intrinsics["a308_0"], intrinsics["a308_1"] = get_intrinsics_from_report(
            camera_a308_report
        )
        intrinsics["a311_0"], intrinsics["a311_1"] = get_intrinsics_from_report(
            camera_a311_report
        )

        for camera, intrinsic in intrinsics.items():
            subfolder = path_to_preprocessed / camera
            subfolder.mkdir()

            with open(subfolder / Var.intrinsics_name, "w") as intrinsics_file:
                intrinsics_file.write(
                    f"{intrinsic.f} {intrinsic.cx} {intrinsic.cy} {intrinsic.k}"
                )

        cameras = ["a308_0", "a308_1", "a311_0", "a311_1"]

        raw_images = path_to_raw_images.iterdir()
        for raw_image in raw_images:
            raw_image_name = raw_image.name
            match len(raw_image_name), int(raw_image_name[-5]):
                case Var.images_308_name_len, Var.camera_number_0:
                    chosen_camera = cameras[0]
                case Var.images_308_name_len, Var.camera_number_1:
                    chosen_camera = cameras[1]
                case Var.images_311_name_len, Var.camera_number_0:
                    chosen_camera = cameras[2]
                case Var.images_311_name_len, Var.camera_number_1:
                    chosen_camera = cameras[3]
                case _:
                    raise ValueError("Invalid image name")
            shutil.copyfile(
                raw_image, path_to_preprocessed / chosen_camera / raw_image_name
            )

        for cam_subfolder in path_to_preprocessed.iterdir():
            camera_name = cam_subfolder.name

            images_list = sorted(cam_subfolder.iterdir())[:-1]
            with open(cam_subfolder / Var.image_list_name, "w") as images_list_file:
                for image in images_list:
                    images_list_file.write(f"{camera_name}/{image.name}\n")

    def _sparse_reconstruction(self):
        workdir = Path(self.input_dir)

        database_path = workdir / Var.database_name
        images_path = workdir / Var.images_name
        sparse_reconstruction_path = workdir / Var.sparse_name
        dense_reconstruction_path = workdir / Var.dense_name

        if sparse_reconstruction_path.exists():
            shutil.rmtree(sparse_reconstruction_path)
        if dense_reconstruction_path.exists():
            shutil.rmtree(dense_reconstruction_path)
        sparse_reconstruction_path.mkdir(exist_ok=False)
        dense_reconstruction_path.mkdir(exist_ok=False)

        feature_extractor = FeatureExtractor(
            database_path,
            images_path,
            init_camera_params=True,
            one_camera_per_folder=True,
        )
        feature_matcher = FeatureMatcher(database_path)
        sparse_reconstructor = SparseReconstructor(
            database_path,
            images_path,
            sparse_reconstruction_path,
            refine_principal_point=True,
            tri_min_angle=0.01,
            ignore_two_view_tracks=False,
        )
        undistorter = Undistorter(
            images_path, sparse_reconstruction_path, dense_reconstruction_path
        )
        feature_extractor.calculate_features()
        feature_matcher.match_features()
        sparse_reconstructor.get_sparse_reconstruction()
        undistorter.undistort()

    @abstractmethod
    def _convert_colmap_to_mvsnet(self) -> None:
        pass

    @abstractmethod
    def _load_model(self):
        pass

    @abstractmethod
    def _process(self):
        pass

    @abstractmethod
    def _postprocess(self):
        pass
