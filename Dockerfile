FROM ros:jazzy-ros-base

# Install SLAM, visualization and C++ development tools
RUN apt-get update && apt-get install -y \
    ros-jazzy-rtabmap-ros \
    ros-jazzy-rviz2 \
    python3-colcon-common-extensions \
    build-essential \
    && rm -rf /var/lib/apt/lists/*