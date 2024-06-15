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


class Camera:
    def __init__(self):
        self.K = [0.0] * 9
        self.R = [0.0] * 9
        self.t = [0.0] * 3
        self.height = 0
        self.width = 0
        self.depth_min = 0.0
        self.depth_max = 0.0


def read_camera(cam_path):
    camera = Camera()
    with open(cam_path, "r") as file:
        line = file.readline().strip()
        for i in range(3):
            (
                camera.R[3 * i + 0],
                camera.R[3 * i + 1],
                camera.R[3 * i + 2],
                camera.t[i],
            ) = map(float, file.readline().split())

        tmp = list(map(float, file.readline().split()))
        line = file.readline().strip()
        line = file.readline().strip()

        for i in range(3):
            camera.K[3 * i + 0], camera.K[3 * i + 1], camera.K[3 * i + 2] = map(
                float, file.readline().split()
            )

        line = file.readline().strip()
        camera.depth_min, interval, depth_num, camera.depth_max = map(
            float, file.readline().split()
        )

    return camera
