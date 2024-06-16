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

from math import ceil

import numpy as np


def hidden_removal_points(pcd):
    diameter = np.linalg.norm(
        np.asarray(pcd.get_max_bound()) - np.asarray(pcd.get_min_bound())
    )
    cam = [0, 0, 0]
    radius = diameter * 100000
    _, indices = pcd.hidden_point_removal(cam, radius)
    return indices


def projection_point(index, pcd, camera):
    x, y, z = np.asarray(pcd.points)[index]
    intrinsic = np.asarray(
        [
            [camera.K[0], camera.K[1], camera.K[2]],
            [camera.K[3], camera.K[4], camera.K[5]],
            [camera.K[6], camera.K[7], camera.K[8]],
        ]
    )
    pixel_coord = np.dot(intrinsic, (x, y, z)) / z
    pixel_coord[0], pixel_coord[1] = int(ceil(pixel_coord[0])), int(
        ceil(pixel_coord[1])
    )
    return pixel_coord
