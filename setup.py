from setuptools import setup, find_packages
from os import path

local = path.abspath(path.dirname(__file__))

# README file
with open(path.join(local, 'README.md'), encoding='utf-8') as file:
    readme_file = file.read()

with open(path.join(local, 'LICENSE'), encoding='utf-8') as file:
    license_file = file.read()

setup(
    name='sumo_statistics',
    url='https://github.com/Pbarbecho/sst.git',
    version='1.0',
    description='Process sumo output files',
    long_description=readme_file,
    long_description_content_type='text/markdown',
    py_modules=['sumo_statistics'],
    author='Guillem',
    author_email='pablo.barbecho@upc.edu',
    keywords='SUMO Outputs',
    packages=find_packages(),
    python_requires='>=3.5',
    install_requires=['matplotlib', 'numpy ', 'pandas', 'seaborn', 'argparse', 'Tk'],
    entry_points={
        'console_scripts': [
            'sumo_statistics=sumo_statistics:main',
        ],
    },
    license="GNU GPL v2",
)
