import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription, LaunchContext
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():

    package_name = "delivery_bot"

    world = LaunchConfiguration("world")

    default_world = os.path.join(get_package_share_directory(package_name), "worlds", "empty.world")


    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description="World to use",
    )


    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
        os.path.join(get_package_share_directory(package_name), 'launch', 'rsp.launch.py')
        ]), launch_arguments={'use_sim_time': "true"}.items()
        )
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py")
        ]), launch_arguments={"gz_args": ['-r -v4 ', world], 'on_exit_shutdown': "true"}.items()
    )

    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=['-topic', 'robot_description',
                   '-entity', 'DeliveryBot',
                   '-z', '0.14',
                   ],
        output="screen",
    )

    gz_bridge_params = os.path.join(get_package_share_directory(package_name), 'config', 'gz_bridge.yaml')

    gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={gz_bridge_params}',
        ]
    )

    gz_image_bridge = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=["/camera/image_raw"]
    )

    return LaunchDescription([
        rsp,
        world_arg,
        gazebo,
        spawn_entity,
        gz_bridge,
        gz_image_bridge,
    ])