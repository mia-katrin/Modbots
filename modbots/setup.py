from distutils.core import setup
import setuptools

setup(
    name='modbots',
    version='1.0',
    author="Mia-Katrin Kvalsund",
    author_email="mkkvalsu@ifi.uio.no",
    packages=setuptools.find_packages(),
    install_requires=[
        "mlagents-envs==0.27.0",
        "numpy==1.19.2",
        "matplotlib==3.4.2",
        "seaborn==0.11.2"
    ]
)
