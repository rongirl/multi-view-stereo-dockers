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
