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

import argparse

from pathlib import Path

from adapter import Adapter

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input_dir",
        type=str,
        help="Path to the images and information about images",
        default="/mvs/working",
    )
    
    parser.add_argument(
        "--output_dir", 
        type=str,
        help="Path to the dense reconstruction",
        default="/mvs/result",
    )  

    args = parser.parse_args()
    Adapter(
        input_dir=args.input_dir,
        output_dir=args.output_dir
    ).run()
