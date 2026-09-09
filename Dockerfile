ARG ROS_DISTRO=humble
FROM osrf/ros:${ROS_DISTRO}-desktop

ARG ROS_DISTRO

ENV DEBIAN_FRONTEND=noninteractive

# Core ROS 2 packages, Gazebo bridge, math deps, and GUI tools
RUN apt-get update && apt-get install -y \
    ros-${ROS_DISTRO}-robot-localization \
    ros-${ROS_DISTRO}-ros-gz \
    ros-${ROS_DISTRO}-ros-ign-gazebo \
    ros-${ROS_DISTRO}-robot-state-publisher \
    ros-${ROS_DISTRO}-ros-gz-sim \
    python3-pip \
    python3-colcon-common-extensions \
    python3-numpy \
    python3-scipy \
    mesa-utils \
    libgl1-mesa-dri \
    libgl1 \
    libglx-mesa0 \
    ros-${ROS_DISTRO}-ros-gz-interfaces \
    && rm -rf /var/lib/apt/lists/*

# Install micro-ROS agent
RUN apt-get update && (apt-get install -y ros-${ROS_DISTRO}-micro-ros-agent || true) \
    && rm -rf /var/lib/apt/lists/*

# Paho MQTT (pip version without invalid flags)
RUN pip3 install --no-cache-dir "paho-mqtt<2.0.0"

WORKDIR /ros2_ws

RUN echo '#!/bin/bash\nset -e\nsource "/opt/ros/$ROS_DISTRO/setup.bash"\nif [ -f "/ros2_ws/install/setup.bash" ]; then\n  source "/ros2_ws/install/setup.bash"\nfi\nexec "$@"' > /ros_entrypoint.sh \
    && chmod +x /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]