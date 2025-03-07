from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="agentic-ai",
    version="1.0.0",
    author="Agentic AI Team",
    author_email="team@agentic-ai.example.com",
    description="A powerful AI assistant platform that seamlessly integrates across Windows, macOS, VS Code, and Chrome",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xraisen/agentic-ai",
    project_urls={
        "Bug Tracker": "https://github.com/xraisen/agentic-ai/issues",
        "Documentation": "https://agentic-ai.example.com/docs/",
        "Source Code": "https://github.com/xraisen/agentic-ai",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "agentic-ai=agentic_ai.main:main",
        ],
        "gui_scripts": [
            "agentic-ai-gui=agentic_ai.gui:main",
        ],
    },
    package_data={
        "agentic_ai": [
            "assets/*",
            "config/*.json",
            "*.json",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="ai, assistant, automation, productivity, development",
    platforms=["Windows", "macOS", "Linux"],
    license="MIT",
    maintainer="Agentic AI Team",
    maintainer_email="team@agentic-ai.example.com",
    requires_python=">=3.8",
    provides=["agentic_ai"],
    scripts=["scripts/agentic-ai"],
    data_files=[
        ("share/applications", ["agentic-ai.desktop"]),
        ("share/doc/agentic-ai", ["README.md", "LICENSE", "CHANGELOG.md"]),
    ],
    options={
        "bdist_wheel": {
            "universal": True,
        },
    },
) 