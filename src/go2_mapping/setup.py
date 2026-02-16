from setuptools import setup
import os
from glob import glob

package_name = 'go2_mapping'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), [
            'launch/go2_navigation.launch.py',
            'launch/go2_mapping.launch.py',
            'launch/go2_bridge.launch.py',
            'launch/pointcloud_to_laserscan.launch.py',
        ]),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='unitree',
    maintainer_email='unitree@todo.todo',
    description='Go2 Robot SLAM and Mapping Utilities',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'odom_to_tf = go2_mapping.odom_to_tf:main',
        ],
    },
    scripts=[
        'scripts/save_map.py',
    ],
)
