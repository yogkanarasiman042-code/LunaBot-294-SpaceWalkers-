from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():

    gazebo = ExecuteProcess(
        cmd=[
            'gz',
            'sim',
            '/home/yogka/lunabot_ws/src/lunabot_core/worlds/lunar_habitat.sdf'
        ],
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/cmd_vel@geometry_msgs/msg/TwistStamped]gz.msgs.Twist',
        ],
        output='screen'
    )

    lidar_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', '0',
            '--y', '0',
            '--z', '0.40',
            '--roll', '0',
            '--pitch', '0',
            '--yaw', '0',
            '--frame-id', 'lunabot/base_link',
            '--child-frame-id', 'lunabot/lidar_link/lidar'
        ],
        output='screen'
    )

    ekf = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        parameters=[
            '/home/yogka/lunabot_ws/src/lunabot_core/config/ekf.yaml',
            {'use_sim_time': True}
        ],
        output='screen'
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                FindPackageShare('slam_toolbox').find('slam_toolbox'),
                'launch',
                'online_async_launch.py'
            )
        ),
        launch_arguments={
            'slam_params_file':
                '/home/yogka/lunabot_ws/src/lunabot_core/config/slam.yaml',
            'use_sim_time': 'true'
        }.items()
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        additional_env={
            'QT_QPA_PLATFORM': 'xcb'
        }
    )

    return LaunchDescription([
        gazebo,
        bridge,
        lidar_tf,

        # Give Gazebo /clock time to start
        TimerAction(
            period=3.0,
            actions=[ekf]
        ),

        # Start SLAM after EKF / TF are alive
        TimerAction(
            period=5.0,
            actions=[slam_launch]
        ),

        # Open RViz after map pipeline has started
        TimerAction(
            period=7.0,
            actions=[rviz]
        ),
    ])
