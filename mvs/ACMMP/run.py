import argparse
from adapter import Adapter
from pathlib import Path
import sys

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
    print(sys.path)
    Adapter(
        input_dir=args.input_dir,
        output_dir=args.output_dir
    ).run()
