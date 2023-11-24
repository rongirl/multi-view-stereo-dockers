import subprocess

from pathlib import Path


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

    def _get_startup_commands(self) -> list[str]:
        base_command = f"colmap feature_extractor"
        database_param = f"--database_path {self.database_path}"
        images_param = f"--image_path {self.image_path}"

        subfolders = sorted(self.image_path.iterdir())
        image_list_paths = [subfolder / "images_list.txt" for subfolder in subfolders]
        intrinsics_paths = [subfolder / "intrinsic.txt" for subfolder in subfolders]

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
                startup_command.append("--ImageReader.single_camera 1")

            if self.init_camera_params:
                with open(intrinsics_path) as f:
                    intrinsics = f.readline()
                intrinsics = intrinsics.split()
                intrinsics = ", ".join(intrinsics)
                startup_command.append(f'--ImageReader.camera_params "{intrinsics}"')

            startup_commands.append(" ".join(startup_command))

        return startup_commands

    def calculate_features(self):
        startup_commands = self._get_startup_commands()

        for startup_command in startup_commands:
            subprocess.run(startup_command, shell=True)
