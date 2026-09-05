from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    lunabot_share = get_package_share_directory('lunabot_core')
    nav2_share = get_package_share_directory('nav2_bringup')

    simulation_launch = os.path.join(
        lunabot_share,
        'launch',
        'lunabot_slam.launch.py'
    )

    nav2_launch = os.path.join(
        nav2_share,
        'launch',
        'navigation_launch.py'
    )

    nav2_params = os.path.join(
        lunabot_share,
        'config',
        'nav2_params.yaml'
    )

    # ---------------------------------------------------------
    # 1. GAZEBO + SENSORS + EKF + SLAM + RVIZ
    # ---------------------------------------------------------

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            simulation_launch
        )
    )

    # ---------------------------------------------------------
    # 2. NAV2
    # Wait until EKF + SLAM + TF have stabilized
    # ---------------------------------------------------------

    nav2 = TimerAction(
        period=15.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    nav2_launch
                ),
                launch_arguments={
                    'params_file': nav2_params,
                    'use_sim_time': 'true'
                }.items()
            )
        ]
    )

    # ---------------------------------------------------------
    # 3. RISK-AWARE MISSION MANAGER
    # ---------------------------------------------------------

    mission_manager = TimerAction(
        period=24.0,
        actions=[
            Node(
                package='lunabot_core',
                executable='mission_manager',
                name='lunabot_mission_manager',
                output='screen'
            )
        ]
    )

    # ---------------------------------------------------------
    # 4. MISSION CONTROL APPLICATION
    # ---------------------------------------------------------

    mission_control = TimerAction(
        period=27.0,
        actions=[
            Node(
                package='lunabot_core',
                executable='mission_control',
                name='lunabot_mission_control',
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        simulation,
        nav2,
        mission_manager,
        mission_control
    ])

