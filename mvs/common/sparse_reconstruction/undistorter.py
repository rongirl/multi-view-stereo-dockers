import subprocess

from pathlib import Path


class Undistorter:
    def __init__(self, image_path: Path, sparse_path: Path, dense_path: Path):
        self.image_path = image_path
        self.sparse_path = sparse_path
        self.dense_path = dense_path

    def _get_startup_command(self) -> str:
        base_command = f"colmap image_undistorter"
        images_param = f"--image_path {self.image_path}"
        sparse_path_param = f"--input_path {self.sparse_path}/0"
        dense_path_param = f"--output_path {self.dense_path}"
        output_type_param = "--output_type COLMAP"

        return " ".join(
            [
                base_command,
                images_param,
                sparse_path_param,
                dense_path_param,
                output_type_param,
            ]
        )

    def undistort(self):
        startup_command = self._get_startup_command()

        subprocess.run(startup_command, shell=True)
