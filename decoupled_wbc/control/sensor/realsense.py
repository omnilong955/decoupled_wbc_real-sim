import time
from typing import Any, Dict, Optional

import cv2
import gymnasium as gym
import numpy as np

from decoupled_wbc.control.base.sensor import Sensor
from decoupled_wbc.control.sensor.sensor_server import CameraMountPosition

try:
    import pyrealsense2 as rs
except ImportError as e:  # pragma: no cover - exercised on deployment target
    raise ImportError(
        "pyrealsense2 is required for RealSenseSensor. "
        "Install librealsense/pyrealsense2 on the robot side."
    ) from e


class RealSenseSensor(Sensor):
    """Sensor wrapper for Intel RealSense cameras."""

    def __init__(
        self,
        mount_position: str = CameraMountPosition.EGO_VIEW.value,
        device_id: Optional[str] = None,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
        enable_stereo: bool = False,
    ):
        self.mount_position = mount_position
        self.device_id = device_id
        self.width = width
        self.height = height
        self.fps = fps
        self.enable_stereo = enable_stereo

        self.pipeline = rs.pipeline()
        self.config = rs.config()

        if self.device_id is not None:
            self.config.enable_device(self.device_id)

        # Match the data feature defaults in this project: 640x480 RGB.
        self.config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        if self.enable_stereo:
            self.config.enable_stream(rs.stream.infrared, 1, width, height, rs.format.y8, fps)
            self.config.enable_stream(rs.stream.infrared, 2, width, height, rs.format.y8, fps)

        try:
            self.profile = self.pipeline.start(self.config)
        except Exception as e:
            extra = f" device_id={self.device_id}" if self.device_id is not None else ""
            raise RuntimeError(f"Failed to start RealSense pipeline{extra}: {e}") from e

    def read(self) -> Optional[Dict[str, Any]]:
        try:
            frames = self.pipeline.wait_for_frames(timeout_ms=1000)
        except RuntimeError:
            return None

        color_frame = frames.get_color_frame()
        if not color_frame:
            return None

        now = time.time()
        timestamps: Dict[str, float] = {self.mount_position: now}
        images: Dict[str, np.ndarray] = {}

        color_bgr = np.asanyarray(color_frame.get_data())
        images[self.mount_position] = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2RGB)

        if self.enable_stereo:
            left_ir_frame = frames.get_infrared_frame(1)
            right_ir_frame = frames.get_infrared_frame(2)

            if left_ir_frame:
                left_gray = np.asanyarray(left_ir_frame.get_data())
                images[f"{self.mount_position}_left_mono"] = cv2.cvtColor(
                    left_gray, cv2.COLOR_GRAY2RGB
                )
                timestamps[f"{self.mount_position}_left_mono"] = now

            if right_ir_frame:
                right_gray = np.asanyarray(right_ir_frame.get_data())
                images[f"{self.mount_position}_right_mono"] = cv2.cvtColor(
                    right_gray, cv2.COLOR_GRAY2RGB
                )
                timestamps[f"{self.mount_position}_right_mono"] = now

        return {"timestamps": timestamps, "images": images}

    def observation_space(self) -> gym.Space:
        spaces = {
            self.mount_position: gym.spaces.Box(
                low=0,
                high=255,
                shape=(self.height, self.width, 3),
                dtype=np.uint8,
            )
        }

        if self.enable_stereo:
            spaces[f"{self.mount_position}_left_mono"] = gym.spaces.Box(
                low=0,
                high=255,
                shape=(self.height, self.width, 3),
                dtype=np.uint8,
            )
            spaces[f"{self.mount_position}_right_mono"] = gym.spaces.Box(
                low=0,
                high=255,
                shape=(self.height, self.width, 3),
                dtype=np.uint8,
            )

        return gym.spaces.Dict(spaces)

    def close(self):
        if hasattr(self, "pipeline"):
            try:
                self.pipeline.stop()
            except Exception:
                pass
