from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="marksman-specialist-ai",
    version="1.0.0",
    author="Marksman AI Team",
    author_email="contact@marksman-ai.com",
    description="Especialista en análisis de Markdown usando Marksman LSP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marksman-ai/specialist",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "pathlib2>=2.3.0",
    ],
    extras_require={
        "gui": ["tkinter"],
        "dev": ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "black", "flake8"],
        "enhanced": ["ruamel.yaml>=0.17.0", "python-magic>=0.4.0", "colorama>=0.4.0"],
    },
    entry_points={
        "console_scripts": [
            "marksman-ai=main:main",
            "marksman-gui=gui_interface:main",
            "marksman-cli=cli_interface:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.json", "examples/*", "templates/*"],
    },
)