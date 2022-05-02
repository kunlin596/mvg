import uuid
from dataclasses import dataclass
from typing import List, Optional

import cv2
import numpy as np
from mvg.basic import SE3
from mvg.camera import Camera
from mvg.image_processing import Image


@dataclass
class Frame:
    id: uuid.UUID
    timestamp: float
    keypoints: List[cv2.KeyPoint]
    descriptors: np.ndarray
    camera: Camera
    pose_G: SE3 = SE3.from_rotvec_pose(np.zeros(6))
    image: Optional[Image] = None

    def has_point(self, point: np.ndarray):
        # TODO
        return True