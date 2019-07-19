from setuptools import setup, find_packages

setup(
    name='ezcv-gui',
    packages=find_packages(),
    author='Frederico Caroli',
    description='GUI for the ezCV project',
    install_requires=['PyQt5', 'ezcv', 'numpy'],
    tests_requires=['pytest', 'pytest-qt', 'pytest-datadir']
)
