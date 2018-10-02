from setuptools import setup, find_packages

setup(
    name='Tequilla',
    version='0.1.1',
    packages=find_packages(),
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    include_package_data=True,
    install_requires=[
        'pyquery',
    ]
)
