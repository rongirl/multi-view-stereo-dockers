# GeoMVSNet Docker Image
This folder contains adapter for [GeoMVSNet](https://github.com/doubleZ0108/GeoMVSNet) and a docker image
## Installation 
Clone the repo
```
git clone https://github.com/rongirl/multi-view-stereo-dockers.git 
cd multi-view-stereo-dockers/mvs/GeoMVSNet 
```
## Building Docker Image
Build docker image using `Dockerfile`:
```
docker build -t geomvsnet --build-arg CUDA_ARCHITECTURES=75  -f Dockerfile ..
```
You can check compute architectures [here](https://arnon.dk/matching-sm-architectures-arch-and-gencode-for-various-nvidia-cards/).
## Running Docker Container
To run the container use the following command:
```
docker run --gpus all --rm \
-v <IMAGES_PATH>:/mvs/working \
-v <OUTPUT_PATH>:/mvs/result \ 
geomvsnet [OPTIONAL_ARGS]
```

Here `<IMAGES_PATH>` with subfolder `images_raw` and files `Detailed Report A308.txt` and `Detailed Report A311.txt`. The `images_raw` folder should contain all the necessary pictures. `<OUTPUT_PATH>` is the path where the results will be saved.

The following `[OPTIONAL_ARGS]` can be used:
```
optional arguments:
  --input_dir  PATH     path to the images and information about images (default: /mvs/working)
  --output_dir PATH     output path (default: /mvs/result)
