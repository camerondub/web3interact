from setuptools import find_packages, setup
from setuptools_scm import get_version

setup(
    name="web3interact",
    version=get_version(),
    author="Cameron Wong",
    description="",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "python-decouple",
        "rlog @ git+https://github.com/camerondub/python-rlog.git#egg=rlog",
        "py-solc-x",
        "web3",
        "ipython",
        "traitlets",
    ],
    entry_points={"console_scripts": ["web3interact = web3interact:main"]},
)
