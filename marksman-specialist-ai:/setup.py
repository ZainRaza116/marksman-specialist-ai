from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README.md if available
this_dir = Path(__file__).parent
readme_file = this_dir / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")
else:
    long_description = "Especialista en análisis de Markdown usando Marksman LSP"

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
    license="MIT",
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
    keywords="markdown lsp specialist analysis documentation",
    python_requires=">=3.8,<4",
    install_requires=[
        "pyyaml>=6.0",
    ],
    extras_require={
        # GUI extras (replace 'tkinter' with a pip-installable GUI lib if needed)
        "gui": ["customtkinter>=5.0.0"],

        # Development & testing
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black",
            "flake8",
        ],

        # Enhanced features
        "enhanced": [
            "ruamel.yaml>=0.17.0",
            "python-magic>=0.4.0",
            "colorama>=0.4.0",
        ],
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
    project_urls={
        "Bug Tracker": "https://github.com/marksman-ai/specialist/issues",
        "Documentation": "https://github.com/marksman-ai/specialist/wiki",
        "Source Code": "https://github.com/marksman-ai/specialist",
    },
)
