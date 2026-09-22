#syntax=docker/dockerfile:1
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
    python3-rosdep \
    python3-numpy \
    python3-scipy \
    mesa-utils \
    libgl1-mesa-dri \
    libgl1 \
    libglx-mesa0 \
    ros-${ROS_DISTRO}-ros-gz-interfaces \
    git \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Inicializa rosdep (necessário antes do rosdep update)
RUN [ -d /etc/ros/rosdep/sources.list.d ] || rosdep init

RUN mkdir -p /microros_ws/src && \
    git clone -b humble https://github.com/micro-ROS/micro_ros_setup.git /microros_ws/src/micro_ros_setup && \
    cd /microros_ws && \
    . /opt/ros/${ROS_DISTRO}/setup.sh && \
    apt-get update && \
    rosdep update && \
    rosdep install --from-paths src --ignore-src -y && \
    colcon build && \
    . install/setup.sh && \
    ros2 run micro_ros_setup create_agent_ws.sh && \
    ros2 run micro_ros_setup build_agent.sh && \
    rm -rf /var/lib/apt/lists/*
    
# Adiciona o overlay do micro-ROS ao entrypoint padrão do sistema
RUN sed -i '/setup.bash/a source "/microros_ws/install/setup.bash"' /ros_entrypoint.sh 2>/dev/null || true

# Paho MQTT (pip version without invalid flags)
RUN pip3 install --no-cache-dir "paho-mqtt<2.0.0"

WORKDIR /ros2_ws

# Entrypoint que exporta ROS base, micro-ROS agent e o workspace local (/ros2_ws)
RUN echo '#!/bin/bash\n\
set -e\n\
source "/opt/ros/$ROS_DISTRO/setup.bash"\n\
if [ -f "/microros_ws/install/setup.bash" ]; then\n\
  source "/microros_ws/install/setup.bash"\n\
fi\n\
if [ -f "/ros2_ws/install/setup.bash" ]; then\n\
  source "/ros2_ws/install/setup.bash"\n\
fi\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
