from pathlib import Path
from common.adapter_base import AdapterBase
import subprocess
import os

class Adapter(AdapterBase):
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
    ):
        super().__init__(input_dir, output_dir)
        
    def _convert_colmap_to_mvsnet(self):
        base_command = "python3 colmap2mvsnet_acm.py"
        dense_folder = os.path.join(self.input_dir, "dense")
        dense_folder_param = f"--dense_folder {dense_folder}"
        output_folder_param = f"--save_folder {self.output_dir}"
        model_ext_param = f"--model_ext .bin"

        startup_command = " ".join(
            [base_command, dense_folder_param, output_folder_param, model_ext_param]
        )
        subprocess.run(startup_command, shell=True)

    def _process(self):
        startup_command = f"./build/ACMMP {self.output_dir}"
        subprocess.run(startup_command, shell=True)

    def _load_model(self):
        pass

    def _preprocess(self):
        pass
  
    def _postprocess(self): 
        pass       
