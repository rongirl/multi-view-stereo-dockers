FROM nvidia/cuda:11.2.2-devel-ubuntu20.04

ENV PROJECT_DIR=/mvs

ENV DEBIAN_FRONTEND=noninteractive

ARG ALGORITHM_FOLDER=GeoMVSNet

ARG CUDA_ARCHITECTURES=native

WORKDIR $PROJECT_DIR

RUN apt-get update && apt-get install -y \
    python3-pip \
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
    libsqlite3-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev && \
    rm -rf /var/lib/apt/lists/*   

RUN git clone https://github.com/colmap/colmap.git && \
    cd colmap && \
    git fetch https://github.com/colmap/colmap.git ${COLMAP_GIT_COMMIT} && \
    git checkout FETCH_HEAD && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCHITECTURES} && \
    ninja && \
    ninja install && \
    cd .. && rm -rf colmap

COPY $ALGORITHM_FOLDER/requirements.txt requirements.txt

RUN python3 -m pip install --no-cache-dir gdown -r requirements.txt

RUN mkdir checkpoints \
    && gdown "147_UbjE87E-HB9sZ5yLDbckynH825nJd" -O checkpoints/model_geomvsnet_release.ckpt

COPY $ALGORITHM_FOLDER .

COPY ./common ./common

ENTRYPOINT ["python3", "run.py"]
