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

from collections import namedtuple
from pathlib import Path

Intrinsics = namedtuple("Intrinsics", "f cx cy k")


def convert_intrinsics(intrinsics_raw: list[str]) -> Intrinsics:
    height, width, focal_length, dx, dy, k = [float(x) for x in intrinsics_raw]

    cx = width / 2 + dx
    cy = height / 2 + dy

    return Intrinsics(focal_length, cx, cy, k)


def get_intrinsics_from_report(path_to_report: Path):
    first_camera_raw_intrinsic, second_camera_raw_intrinsic = None, None
    with open(path_to_report) as report_file:
        for i, line in enumerate(report_file):
            if i == 5:
                first_camera_raw_intrinsic = line.split()[22:28]
            elif i == 6:
                second_camera_raw_intrinsic = line.split()[22:28]
            elif i > 6:
                break
    if first_camera_raw_intrinsic is None or second_camera_raw_intrinsic is None:
        raise ValueError("Invalid report file")
    first_cam_intrinsics = convert_intrinsics(first_camera_raw_intrinsic)
    second_cam_intrinsics = convert_intrinsics(second_camera_raw_intrinsic)
    return first_cam_intrinsics, second_cam_intrinsics
