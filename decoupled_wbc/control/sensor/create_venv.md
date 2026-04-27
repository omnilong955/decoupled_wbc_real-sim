# create venv
cd ~
source ioenv_cli/ioenv.sh
ioenv run onboard

sudo apt update
sudo apt install -y python3-venv python3-pip python3-opencv

cd /root/workspace/decoupled_wbc_real-sim/decoupled_wbc/
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

python3 -m pip install -U pip
python3 -m pip install -r requirements_g1_camera.txt
python3 -m pip install pyrealsense2



# 运行
cd ~
source ioenv_cli/ioenv.sh
ioenv run onboard

cd /root/workspace/decoupled_wbc_real-sim
source /root/workspace/decoupled_wbc_real-sim/decoupled_wbc/.venv/bin/activate
export PYTHONPATH=/root/workspace/decoupled_wbc_real-sim:$PYTHONPATH

python3 decoupled_wbc/control/sensor/composed_camera.py \
  --ego_view_camera realsense \
  --port 5555 \
  --fps 20
