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

FROM nvidia/cuda:12.0.0-devel-ubuntu22.04

ENV PROJECT_DIR=/mvs
 
ENV DEBIAN_FRONTEND=noninteractive

ARG ALGORITHM_FOLDER=ACMMP

ARG CUDA_ARCHITECTURES=native

WORKDIR $PROJECT_DIR

RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    build-essential \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgtest-dev \
    libopencv-dev \
    libsqlite3-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev \
    python3-pip

RUN git clone https://github.com/colmap/colmap.git
RUN cd colmap && \
    git fetch https://github.com/colmap/colmap.git ${COLMAP_GIT_COMMIT} && \
    git checkout FETCH_HEAD && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCHITECTURES} && \
    ninja && \
    ninja install && \
    cd .. && rm -rf colmap

RUN pip install numpy==1.22.0 \
    opencv-python==4.8.0.76

COPY $ALGORITHM_FOLDER  .

COPY ./common ./common

RUN mkdir build && \
    cd build && \
    sed -i "s/-gencode arch=compute_60,code=sm_60/-gencode arch=compute_$CUDA_ARCHITECTURES,code=sm_$CUDA_ARCHITECTURES/" ../CMakeLists.txt && \
    sed -i "s/cuda-8.0/cuda-12.0/" ../CMakeLists.txt && \
    cmake .. && \
    make -j4

ENTRYPOINT ["python3", "run.py"]
