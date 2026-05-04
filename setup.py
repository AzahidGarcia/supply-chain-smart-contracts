from setuptools import find_packages, setup

setup(
    name="supply-chain-smart-contracts",
    version="1.0.0",
    description="Blockchain con smart contracts para trazabilidad de cadena de suministro",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["rich>=13.0"],
    extras_require={"dev": ["pytest>=8.0"]},
    entry_points={
        "console_scripts": [
            "supply-chain=src.cli:main",
        ],
    },
)
