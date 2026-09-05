from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'lunabot_core'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')
        ),
        (
            os.path.join('share', package_name, 'worlds'),
            glob('worlds/*.sdf')
        ),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yogka',
    maintainer_email='yogka@todo.todo',
    description='LunaBot ROS 2 core package',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'lunabot_node = lunabot_core.lunabot_node:main',
            'lunabot_monitor = lunabot_core.lunabot_monitor:main',
            'lunabot_patrol = lunabot_core.lunabot_patrol:main',
            'environment_sensor = lunabot_core.environment_sensor:main',
            'mission_manager = lunabot_core.mission_manager:main',
             'mission_control = lunabot_core.mission_control:main',
       ],
    },
)


