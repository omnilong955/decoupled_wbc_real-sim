cd ~/workspace/workspace_decoupled_WBC/GR00T-WholeBodyControl

sudo apt update
sudo apt install -y python3-venv python3-pip python3-opencv

python3 -m venv --system-site-packages .venv
source .venv/bin/activate

python -m pip install -U pip
python -m pip install -r requirements_g1_camera.txt

export PYTHONPATH=$PWD:$PYTHONPATH


# test
python - <<'PY'
import cv2, numpy, gymnasium, zmq, msgpack, msgpack_numpy, tyro
print("basic camera deps ok")
try:
    import pyrealsense2 as rs
    print("pyrealsense2 ok", getattr(rs, "__version__", ""))
except Exception as e:
    print("pyrealsense2 missing:", e)
PY
