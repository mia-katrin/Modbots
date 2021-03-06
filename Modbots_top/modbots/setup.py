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
        "matplotlib",
        "seaborn",
        "scikit-image",
        "neat-python==0.92"
    ]
)
