G1端侧部署服务：
source ioenv_cli/ioenv.sh
ioenv run onboard

cd ~/workspace/workspace_decoupled_WBC/GR00T-WholeBodyControl
source .venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH

python decoupled_wbc/control/sensor/composed_camera.py \
  --ego_view_camera realsense \
  --port 5555 \
  --fps 20



宿主机
# 启动容器
cd /home/long/workspace_decoupled_WBC/GR00T-WholeBodyControl/decoupled_wbc
./docker/run_docker.sh --root

python decoupled_wbc/scripts/deploy_g1.py \
  --interface real \
  --robot_ip 192.168.123.164 \
  --camera_host 192.168.123.164 \
  --camera_port 5555 \
  --body_control_device pico \
  --hand_control_device dummy \
  --no-add_stereo_camera

可选：--no-with_hands 不用灵巧手


