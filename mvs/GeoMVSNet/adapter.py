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

import subprocess
import os
import types
import time 
import sys
import gc
import cv2
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn

from torch.utils.data import DataLoader
from pathlib import Path

from datasets.data_io import save_pfm, write_cam
from datasets.our import OurDataset
from common.adapter_base import AdapterBase
from common.config import Var
from colmap2mvsnet import processing_single_scene
from fusions.our.open3d_fuse import open3d_filter
from models.geomvsnet import GeoMVSNet
from models.utils import tensor2numpy, tocuda


class Adapter(AdapterBase):
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
    ):
        super().__init__(input_dir, output_dir)

        logging.basicConfig(level=logging.INFO)
        
    def _convert_colmap_to_mvsnet(self):
        dense_folder = Path(self.input_dir) / Var.dense_name 
        args = {
              'dense_folder': f"{dense_folder}",
              'save_folder': f"{self.output_dir}",
              'max_d': 192, 
              'interval_scale': 1, 
              'theta0': 5, 
              'sigma1': 1, 
              'sigma2': 10, 
              'model_ext': ".bin"
        }
        args = types.SimpleNamespace(**args)
        Path(args.save_folder).mkdir(exist_ok=True)   
        processing_single_scene(args)
    
    def _load_model(self):        
        args = {
              'testpath': f"{self.output_dir}",
              'n_views': 5,
              'levels': 4, 
              'hypo_plane_num_stages': "8,8,4,4", 
              'depth_interal_ratio_stages': "0.5,0.5,0.5,1", 
              'feat_base_channel': 8, 
              'reg_base_channel': 8, 
              'group_cor_dim_stages': "8,8,4,4",
              'loadckpt' : "./checkpoints/model_geomvsnet_release.ckpt",
              'batch_size' : 1,
              'outdir' : f"{self.output_dir}"
        }
        args = types.SimpleNamespace(**args)
        test_dataset = OurDataset(args.testpath, args.n_views, max_wh=(1600, 1200))
        TestImgLoader = DataLoader(test_dataset, args.batch_size, shuffle=False, num_workers=4, drop_last=False)
        model = GeoMVSNet(
        levels=args.levels, 
        hypo_plane_num_stages=[int(n) for n in args.hypo_plane_num_stages.split(",")], 
        depth_interal_ratio_stages=[float(ir) for ir in args.depth_interal_ratio_stages.split(",")],
        feat_base_channel=args.feat_base_channel, 
        reg_base_channel=args.reg_base_channel,
        group_cor_dim_stages=[int(n) for n in args.group_cor_dim_stages.split(",")],
        )
        state_dict = torch.load(args.loadckpt, map_location=torch.device("cpu"))
        model.load_state_dict(state_dict['model'], strict=False)

        model.cuda()
        model.eval()
        return TestImgLoader, model, args

    def __save_depth_maps(self, filename, depth_est, outdir):
        depth_filename = ''.join([outdir, filename.format(Var.depth_est, Var.format_pfm)])
        Path(depth_filename).touch(exist_ok=True) 
        save_pfm(depth_filename, depth_est)

    def __save_images_cameras(self, filename, camera, image, outdir):
        image = image[0].numpy()  
        camera = camera[0]           
        cam_filename = ''.join([outdir + filename.format(Var.cameras, Var.cameras_format)])
        img_filename = ''.join([outdir + filename.format(Var.images_name, Var.format_images)])
        Path(cam_filename).touch(exist_ok=True)
        Path(img_filename).touch(exist_ok=True)           
        write_cam(cam_filename, camera)
        image = np.clip(np.transpose(image, (1, 2, 0)) * 255, 0, 255).astype(np.uint8)
        img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(img_filename, img_bgr)
    
    def __save_confidence_maps(self, filename, photometric_confidence, confidence_list, outdir, levels):
        confidence_filename = ''.join([outdir + filename.format(Var.confidence, Var.format_pfm)])
        Path(confidence_filename).touch(exist_ok=True)    
        for stage_idx, photometric_confidence in enumerate(confidence_list):
            if stage_idx != levels - 1:
                confidence_filename = ''.join([outdir, filename.format(Var.confidence, Var.stage + str(stage_idx)+Var.format_pfm)])
            else:
                confidence_filename = ''.join([outdir, filename.format(Var.confidence, Var.format_pfm)])
                save_pfm(confidence_filename, photometric_confidence) 

    def _process(self):
        total_time = 0
        TestImgLoader, model, args = self._load_model()
        with torch.no_grad():
            for batch_idx, sample in enumerate(TestImgLoader):
                sample_cuda = tocuda(sample)
                start_time = time.time()
                outputs = model(
                    sample_cuda["imgs"], 
                    sample_cuda["proj_matrices"], sample_cuda["intrinsics_matrices"], 
                    sample_cuda["depth_values"], 
                    sample["filename"]
                )
                end_time = time.time()
                total_time += end_time - start_time
                outputs = tensor2numpy(outputs)
                del sample_cuda
                filenames = sample["filename"]
                cams = sample["proj_matrices"]["stage{}".format(args.levels)].numpy()
                imgs = sample["imgs"]
                logging.info('Iter {}/{}, Time:{:.3f} Res:{}'.format(batch_idx, len(TestImgLoader), end_time - start_time, imgs[0].shape))
                for filename, cam, img, depth_est, photometric_confidence in zip(filenames, cams, imgs, outputs["depth"], outputs["photometric_confidence"]):
                    path_depth_est = Path(args.outdir) / Var.depth_est
                    Path(path_depth_est).mkdir(parents=True, exist_ok=True)
                    self.__save_depth_maps(filename, depth_est, outdir=args.outdir)
                    confidence_list = [outputs['stage{}'.format(i)]['photometric_confidence'].squeeze(0) for i in range(1,5)]
                    photometric_confidence = confidence_list[-1]
                    path_confidence_map = Path(args.outdir) / Var.confidence
                    Path(path_confidence_map).mkdir(parents=True, exist_ok=True)
                    self.__save_confidence_maps(filename, photometric_confidence, confidence_list, args.outdir, args.levels)
                    path_images = Path(args.outdir) / Var.images_name
                    Path(path_images).mkdir(parents=True, exist_ok=True)
                    path_cams = Path(args.outdir) / Var.cameras
                    Path(path_cams).mkdir(parents=True, exist_ok=True)
                    self.__save_images_cameras(filename, cam, img, args.outdir)
        torch.cuda.empty_cache()
        gc.collect()

    def _postprocess(self):
        ply_path = Path(self.output_dir) / Var.open3d_ply
        args = {
              'root_path' : f"{self.output_dir}",
              'depth_path' : f"{self.output_dir}",
              'ply_path' : ply_path,
              'dist_thresh' : 0.2, 
              'prob_thresh' : 0.3, 
              'num_consist' : 4,
              'device' : "cuda"
            }
        args = types.SimpleNamespace(**args)
        open3d_filter(args)
