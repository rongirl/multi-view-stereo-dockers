FROM nvidia/cuda:12.0.0-devel-ubuntu22.04

ENV PROJECT_DIR=/mvs

ENV DEBIAN_FRONTEND=noninteractive

ARG ALGORITHM_FOLDER=APD-MVS

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
    libboost-filesystem-dev \
    python3-pip && \
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

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY $ALGORITHM_FOLDER  .

COPY ./common ./common
 
RUN mkdir build && \
    cd build && \
    sed -i "s/-gencode arch=compute_75,code=sm_75/-gencode arch=compute_$CUDA_ARCHITECTURES,code=sm_$CUDA_ARCHITECTURES/" ../cpp/CMakeLists.txt && \
    sed -i "s/dslr_calibration_undistorted/sparse/" ../colmap2mvsnet.py && \ 
    cmake ../cpp && \
    make -j4

ENTRYPOINT ["python3", "run.py"]
