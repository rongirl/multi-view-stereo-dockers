# Copyright (c) 2024, Arabella Gromova, Ivan Moskalenko, Kirill Ivanov, Anastasiia Kornilova
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

import os
import random

from datasets.data_io import *

import cv2
import numpy as np
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

IMAGE_SCALE_FACTOR = 2


class OurDataset(Dataset):
    def __init__(self, root_dir, n_views, **kwargs):
        super(OurDataset, self).__init__()

        self.root_dir = root_dir
        self.n_views = n_views

        self.total_depths = 192
        self.interval_scale = 1.06

        self.data_scale = kwargs.get("data_scale", "mid")
        self.color_augment = transforms.ColorJitter(brightness=0.5, contrast=0.5)
        self.max_wh = kwargs.get("max_wh", (1600, 1200))
        self.metas = self.build_metas()

    def build_metas(self):
        metas = []
        pair_file = "./pair.txt"
        with open(os.path.join(self.root_dir, pair_file)) as f:
            num_viewpoint = int(f.readline())
            for _ in range(num_viewpoint):
                ref_view = int(f.readline().rstrip())
                src_views = [int(x) for x in f.readline().rstrip().split()[1::2]]

                if len(src_views) < self.n_views:
                    print("{} < num_views:{}".format(len(src_views), self.n_views))
                    src_views += [src_views[0]] * (self.n_views - len(src_views))
                metas.append((3, ref_view, src_views))

        print("Our Dataset metas:", len(metas))
        return metas

    def __len__(self):
        return len(self.metas)

    def read_cam_file(self, filename):
        with open(filename) as f:
            lines = f.readlines()
            lines = [line.rstrip() for line in lines]
        # extrinsics: line [1,5), 4x4 matrix
        extrinsics_col = 4
        extrinsics = np.fromstring(
            " ".join(lines[1:5]), dtype=np.float32, sep=" "
        ).reshape((extrinsics_col, extrinsics_col))
        # intrinsics: line [7-10), 3x3 matrix
        intrinsics_col = 3
        intrinsics = np.fromstring(
            " ".join(lines[7:10]), dtype=np.float32, sep=" "
        ).reshape((intrinsics_col, intrinsics_col))

        intrinsics_factor = 4.0
        intrinsics[:2, :] /= intrinsics_factor

        # depth_min & depth_interval: line 11
        depth_min = float(lines[11].split()[0])
        depth_interval = float(lines[11].split()[1])
        min_len = 3
        if len(lines[11].split()) >= min_len:
            num_depth = lines[11].split()[2]
            depth_max = depth_min + int(float(num_depth)) * depth_interval
            depth_interval = (depth_max - depth_min) / self.total_depths

        depth_interval *= self.interval_scale

        return intrinsics, extrinsics, depth_min, depth_interval

    def read_img(self, filename):
        img = Image.open(filename)
        # scale 0~255 to 0~1
        scale_factor = 255.0
        np_img = np.array(img, dtype=np.float32) / scale_factor
        return np_img

    def crop_img(self, img):
        raw_h, raw_w = img.shape[:2]
        diff_h, diff_w = 1024, 1280
        start_h = (raw_h - diff_h) // IMAGE_SCALE_FACTOR
        start_w = (raw_w - diff_w) // IMAGE_SCALE_FACTOR
        return img[
            start_h : start_h + diff_h, start_w : start_w + diff_w, :
        ]  # (1024, 1280)

    def prepare_img(self, hr_img):
        h, w = hr_img.shape
        data_scales = ["mid", "raw"]
        if self.data_scale == data_scales[0]:
            hr_img_ds = cv2.resize(
                hr_img,
                (w // IMAGE_SCALE_FACTOR, h // IMAGE_SCALE_FACTOR),
                interpolation=cv2.INTER_NEAREST,
            )
            h, w = hr_img_ds.shape
            target_h, target_w = 512, 640
            start_h, start_w = (h - target_h) // IMAGE_SCALE_FACTOR, (
                w - target_w
            ) // IMAGE_SCALE_FACTOR
            hr_img_crop = hr_img_ds[
                start_h : start_h + target_h, start_w : start_w + target_w
            ]
        elif self.data_scale == data_scales[1]:
            hr_img_crop = hr_img[
                h // IMAGE_SCALE_FACTOR - target_h : h // IMAGE_SCALE_FACTOR + target_h,
                w // IMAGE_SCALE_FACTOR - target_w : w // IMAGE_SCALE_FACTOR + target_w,
            ]  # (1024, 1280)
        return hr_img_crop

    def scale_mvs_input(self, img, intrinsics, max_w, max_h, base=64):
        h, w = img.shape[:2]
        scale_factor = 1.0
        if h > max_h or w > max_w:
            scale = scale_factor * max_h / h
            if scale * w > max_w:
                scale = scale_factor * max_w / w
            new_w, new_h = scale * w // base * base, scale * h // base * base
        else:
            new_w, new_h = (
                scale_factor * w // base * base,
                scale_factor * h // base * base,
            )

        scale_w = scale_factor * new_w / w
        scale_h = scale_factor * new_h / h
        intrinsics[0, :] *= scale_w
        intrinsics[1, :] *= scale_h

        img = cv2.resize(img, (int(new_w), int(new_h)))

        return img, intrinsics

    def read_mask_hr(self, filename):
        img = Image.open(filename)
        np_img = np.array(img, dtype=np.float32)
        np_img = (np_img > 10).astype(np.float32)
        np_img = self.prepare_img(np_img)

        h, w = np_img.shape

        np_img_ms = {
            "stage1": cv2.resize(
                np_img, (w // 8, h // 8), interpolation=cv2.INTER_NEAREST
            ),
            "stage2": cv2.resize(
                np_img, (w // 4, h // 4), interpolation=cv2.INTER_NEAREST
            ),
            "stage3": cv2.resize(
                np_img, (w // 2, h // 2), interpolation=cv2.INTER_NEAREST
            ),
            "stage4": np_img,
        }
        return np_img_ms

    def read_depth_hr(self, filename, scale):
        depth_hr = np.array(read_pfm(filename)[0], dtype=np.float32) * scale
        depth_lr = self.prepare_img(depth_hr)

        h, w = depth_lr.shape
        depth_lr_ms = {
            "stage1": cv2.resize(
                depth_lr, (w // 8, h // 8), interpolation=cv2.INTER_NEAREST
            ),
            "stage2": cv2.resize(
                depth_lr, (w // 4, h // 4), interpolation=cv2.INTER_NEAREST
            ),
            "stage3": cv2.resize(
                depth_lr, (w // 2, h // 2), interpolation=cv2.INTER_NEAREST
            ),
            "stage4": depth_lr,
        }
        return depth_lr_ms

    def __getitem__(self, idx):
        light_idx, ref_view, src_views = self.metas[idx]

        view_ids = [ref_view] + src_views[: self.n_views - 1]
        scale_ratio = 1

        imgs = []
        depth_values = None
        proj_matrices = []

        for i, vid in enumerate(view_ids):
            # @Note image & cam

            img_filename = os.path.join(self.root_dir, "images/{:0>8}.jpg".format(vid))
            proj_mat_filename = os.path.join(
                self.root_dir, "cams/{:0>8}_cam.txt".format(vid)
            )

            img = self.read_img(img_filename)
            intrinsics, extrinsics, depth_min, depth_interval = self.read_cam_file(
                proj_mat_filename
            )

            img, intrinsics = self.scale_mvs_input(
                img, intrinsics, self.max_wh[0], self.max_wh[1]
            )

            imgs.append(img.transpose(2, 0, 1))

            # reference view
            if i == 0:
                # @Note depth values
                depth_max = depth_interval * self.total_depths + depth_min
                depth_values = np.array(
                    [depth_min * scale_ratio, depth_max * scale_ratio], dtype=np.float32
                )

            proj_mat = np.zeros(shape=(2, 4, 4), dtype=np.float32)
            proj_mat[0, :4, :4] = extrinsics
            proj_mat[1, :3, :3] = intrinsics
            proj_matrices.append(proj_mat)

        proj_matrices = np.stack(proj_matrices)
        intrinsics = np.stack(intrinsics)
        stage1_pjmats = proj_matrices.copy()
        stage1_pjmats[:, 1, :2, :] = proj_matrices[:, 1, :2, :] / 2.0
        stage1_ins = intrinsics.copy()
        stage1_ins[:2, :] = intrinsics[:2, :] / 2.0
        stage3_pjmats = proj_matrices.copy()
        stage3_pjmats[:, 1, :2, :] = proj_matrices[:, 1, :2, :] * 2
        stage3_ins = intrinsics.copy()
        stage3_ins[:2, :] = intrinsics[:2, :] * 2.0
        stage4_pjmats = proj_matrices.copy()
        stage4_pjmats[:, 1, :2, :] = proj_matrices[:, 1, :2, :] * 4
        stage4_ins = intrinsics.copy()
        stage4_ins[:2, :] = intrinsics[:2, :] * 4.0
        proj_matrices = {
            "stage1": stage1_pjmats,
            "stage2": proj_matrices,
            "stage3": stage3_pjmats,
            "stage4": stage4_pjmats,
        }
        intrinsics_matrices = {
            "stage1": stage1_ins,
            "stage2": intrinsics,
            "stage3": stage3_ins,
            "stage4": stage4_ins,
        }

        sample = {
            "imgs": imgs,
            "proj_matrices": proj_matrices,
            "intrinsics_matrices": intrinsics_matrices,
            "depth_values": depth_values,
        }
        sample["filename"] = "/{}/" + "{:0>8}".format(view_ids[0]) + "{}"

        return sample
