from setuptools import setup, find_packages

setup(
    name='perennityai-mediapipe-data-viz',
    version='0.1.0',
    author='Perennity AI',
    author_email='contact@perennityai.com',
    description='A data visualization tool for MediaPipe hand, face, and pose landmarks with Perennity AI enhancements.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/perennityai/perennityai-mediapipe-data-viz',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    python_requires='>=3.8',
    install_requires=[
        'matplotlib>=3.4',
        'opencv-python-headless>=4.5',
        'mediapipe>=0.8',
        'pandas>=1.3',
        'numpy>=1.21',
    ],
    entry_points={
        'console_scripts': [
            'perennityai-mediapipe-data-viz=perennityai_mediapipe_data_viz.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        # Include any config or other necessary data files in the package
        '': ['configs/*.ini'],
    },
    license='MIT',
    keywords='mediapipe visualization hand landmarks face landmarks pose landmarks data-viz PerennityAI',
)
