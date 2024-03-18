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
import os
import types

from pathlib import Path

from common.adapter_base import AdapterBase
from common.config import Var
from colmap2mvsnet_acm import processing_single_scene


class Adapter(AdapterBase):
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
    ):
        super().__init__(input_dir, output_dir)

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
        processing_single_scene(args)

    def _process(self):
        startup_command = f"./build/ACMMP {self.output_dir}"
        subprocess.run(startup_command, shell=True)

    def _load_model(self):
        pass

    def _preprocess(self):
        pass

    def _postprocess(self):
        pass
