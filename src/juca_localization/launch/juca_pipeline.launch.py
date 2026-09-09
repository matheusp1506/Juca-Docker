import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('juca_localization')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    ekf_config_path = os.path.join(pkg_share, 'config', 'ekf.yaml')
    urdf_file = os.path.join(pkg_share, 'urdf', 'juca.urdf')

    use_microros = LaunchConfiguration('use_microros')

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_microros',
            default_value='false',
            description='Switch between MQTT ingestion and micro-ROS agent'
        ),

        # 1A. MQTT Ingestion
        Node(
            condition=UnlessCondition(use_microros),
            package='juca_localization',
            executable='mqtt_bridge',
            name='mqtt_bridge',
            output='screen'
        ),

        # 1B. micro-ROS Agent
        Node(
            condition=IfCondition(use_microros),
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent',
            arguments=['udp4', '--port', '8888'],
            output='screen'
        ),

        # 2. State Estimation
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_config_path],
            remappings=[('odometry/filtered', '/juca/odometry/filtered')]
        ),

        # 3. TF State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),

        # 4. Official Gazebo Sim launcher (resolves binary automatically)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={'gz_args': '-r empty.sdf'}.items()
        ),

        # 5. Spawn URDF into Gazebo
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-world', 'empty',
                '-name', 'juca',
                '-string', robot_desc,
                '-z', '0.1'
            ],
            output='screen'
        ),

        Node(
            package='juca_localization',
            executable='gz_bridge',
            name='gz_pose_bridge',
            output='screen'
        ),

        # 6. Bridge the SetEntityPose service and Clock between ROS 2 and Gazebo
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/world/empty/set_pose@ros_gz_interfaces/srv/SetEntityPose',
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
            ],
            output='screen'
        )
    ])