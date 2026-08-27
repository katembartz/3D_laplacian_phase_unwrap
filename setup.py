from pathlib import Path
from setuptools import setup, find_packages

__package_name__ = "phase_unwrap"


def get_version_and_cmdclass(pkg_path):
    """Load version.py module without importing the whole package.

    Template code from miniver
    """
    import os
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("version", os.path.join(pkg_path, "_version.py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__, module.get_cmdclass(pkg_path)


__version__, cmdclass = get_version_and_cmdclass(__package_name__)

setup(
    name=__package_name__,
    version=__version__,
    description=(
        "3-dimensional phase processing pipeline (unwrapping and background removal) for MRI phase images in Python."
    ),
    long_description=(Path(__file__).parent.resolve() / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Kathleen M Bartz",
    author_email="kbartz2@jh.edu",
    url="https://github.com/katembartz/3D_laplacian_phase_unwrap",
    license="Apache-2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: Apache License, Version 2.0",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(),
    keywords="3D mri phase unwrapping",
    entry_points={
        "console_scripts": [
            "unwrap-phase-3D=phase_unwrap.cli:main",
        ]
    },
    python_requires=">=3.8",
    install_requires=[
        "nibabel",
        "numpy",
    ],
    cmdclass=cmdclass,
)
