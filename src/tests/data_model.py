import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from mvgkit.camera import CameraMatrix
from mvgkit.features import SIFT, Matcher
from mvgkit.image_processing import Image
from mvgkit.stereo import Fundamental

# FIXME: Put these into conf files.
WORKSPACE_PATH = Path(os.path.dirname(__file__))
DATA_ROOT_PATH = WORKSPACE_PATH / "data"
intrinsics_rms_threshold = 2.6
fundamental_rms_threshold = 1.5
stereo_reprojection_rms_threshold = 0.5


@dataclass
class StereoDataPack:
    image_L: np.ndarray
    image_R: np.ndarray
    points_L: np.ndarray
    points_R: np.ndarray
    camera_matrix: Optional[CameraMatrix] = None
    manual_points_L: Optional[np.ndarray] = None
    manual_points_R: Optional[np.ndarray] = None
    F_RL: Optional[np.ndarray] = None
    inlier_mask: Optional[np.ndarray] = None


def get_leuven_stereo_data_pack():
    manual_points_L = np.array(
        [
            [75, 297],
            [101, 304],
            [98, 386],
            [70, 386],
            [115, 18],
            [93, 24],
            [101, 45],
            [366, 164],
            [392, 173],
            [566, 269],
            [522, 62],
        ],
        dtype=np.float32,
    )

    manual_points_R = np.array(
        [
            [366, 330],
            [381, 333],
            [383, 384],
            [368, 384],
            [383, 124],
            [369, 157],
            [376, 172],
            [592, 197],
            [621, 200],
            [656, 310],
            [734, 91],
        ],
        dtype=np.float32,
    )

    fundamental_root_path = Path(DATA_ROOT_PATH) / "fundamental"
    with open(fundamental_root_path / "meta.json") as f:
        meta = json.load(f)
    image_L = Image.from_file(str(fundamental_root_path / meta["left"])).data
    image_R = Image.from_file(str(fundamental_root_path / meta["right"])).data
    camera_matrix = CameraMatrix.from_matrix(np.reshape(meta["K"], (3, 3)))

    # TODO(kun): after implementing RANSAC point registration, enable auto matching again
    print("Computing feature points and their matches on left and right images...")
    keypoints_L, descriptors_L = SIFT.detect(image_L)
    keypoints_R, descriptors_R = SIFT.detect(image_R)
    query_indices, train_indices = Matcher.match(
        descriptors1=descriptors_L, descriptors2=descriptors_R
    )
    points_L = np.asarray([kp.pt for kp in keypoints_L[query_indices]])
    points_R = np.asarray([kp.pt for kp in keypoints_R[train_indices]])
    F_RL, inlier_mask = Fundamental.compute(x_L=points_L, x_R=points_R)

    return StereoDataPack(
        image_L=image_L,
        image_R=image_R,
        manual_points_L=manual_points_L,
        manual_points_R=manual_points_R,
        points_L=points_L,
        points_R=points_R,
        camera_matrix=camera_matrix,
        F_RL=F_RL,
        inlier_mask=inlier_mask,
    )


def get_aloe_stereo_data_pack():
    root_path = Path(DATA_ROOT_PATH) / "stereo" / "aloe"
    with open(root_path / "meta.json") as f:
        meta = json.load(f)
    image_L = Image.from_file(str(root_path / meta["left"])).resize(0.4).data
    image_R = Image.from_file(str(root_path / meta["right"])).resize(0.4).data

    # TODO(kun): after implementing RANSAC point registration, enable auto matching again
    print("Computing feature points and their matches on left and right images...")
    keypoints_L, descriptors_L = SIFT.detect(
        image_L,
        # options=SIFT.Options(
        #     num_features=20000,
        #     num_octave_layers=4,
        #     contrast_threshold=0.02,
        #     edge_threshold=7,
        #     sigma=0.8,
        # ),
    )
    keypoints_R, descriptors_R = SIFT.detect(
        image_R,
        # options=SIFT.Options(
        #     num_features=20000,
        #     num_octave_layers=4,
        #     contrast_threshold=0.02,
        #     edge_threshold=7,
        #     sigma=0.8,
        # ),
    )
    query_indices, train_indices = Matcher.match(
        descriptors1=descriptors_L, descriptors2=descriptors_R
    )
    points_L = np.asarray([kp.pt for kp in keypoints_L[query_indices]])
    points_R = np.asarray([kp.pt for kp in keypoints_R[train_indices]])
    F_RL, inlier_mask = Fundamental.compute(x_L=points_L, x_R=points_R)

    return StereoDataPack(
        image_L=image_L,
        image_R=image_R,
        manual_points_L=None,
        manual_points_R=None,
        points_L=points_L,
        points_R=points_R,
        camera_matrix=None,
        F_RL=F_RL,
        inlier_mask=inlier_mask,
    )


def get_book_stereo_data_pack():
    root_path = Path(DATA_ROOT_PATH) / "stereo" / "book"
    with open(root_path / "meta.json") as f:
        meta = json.load(f)
    image_L = Image.from_file(root_path / meta["left"]).data
    image_R = Image.from_file(root_path / meta["right"]).data
    F_RL = np.asarray(meta["F_RL"])

    # TODO(kun): after implementing RANSAC point registration, enable auto matching again
    # print("Computing feature points and their matches on left and right images...")
    # keypoints_L, descriptors_L = SIFT.detect(
    #     image_L,
    #     options=SIFT.Options(
    #         num_features=20000,
    #         num_octave_layers=4,
    #         contrast_threshold=0.02,
    #         edge_threshold=7,
    #         sigma=0.8,
    #     ),
    # )
    # keypoints_R, descriptors_R = SIFT.detect(
    #     image_R,
    #     options=SIFT.Options(
    #         num_features=20000,
    #         num_octave_layers=4,
    #         contrast_threshold=0.02,
    #         edge_threshold=7,
    #         sigma=0.8,
    #     ),
    # )

    # matches = Matcher.match(descriptors1=descriptors_L, descriptors2=descriptors_R)
    # points_L, points_R, _ = Matcher.get_matched_points(
    #     keypoints_L, keypoints_R, matches, dist_threshold=0.6
    # )

    points_L = np.asarray(meta["points_L"])
    points_R = np.asarray(meta["points_R"])
    inlier_mask = np.asarray(meta["inlier_mask"], dtype=bool)

    return StereoDataPack(
        image_L=image_L,
        image_R=image_R,
        manual_points_L=None,
        manual_points_R=None,
        points_L=points_L,
        points_R=points_R,
        camera_matrix=None,
        F_RL=F_RL,
        inlier_mask=inlier_mask,
    )
