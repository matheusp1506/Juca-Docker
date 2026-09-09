from setuptools import setup
import os
from glob import glob

package_name = 'juca_localization'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        # If you have meshes (uncomment if using visual STL/DAE files):
        # (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Matheus Pereira',
    maintainer_email='matheusp1506@gmail.com',
    description='Juca localization and simulation pipeline',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'mqtt_bridge = juca_localization.mqtt_bridge:main',
            'gz_bridge = juca_localization.gz_bridge:main',
        ],
    },
)