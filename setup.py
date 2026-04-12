from setuptools import setup, find_packages

setup(
    name="awesome-tui",
    version="0.1.0",
    description="A curated collection of TUI applications, frameworks, and libraries",
    packages=find_packages(),
    install_requires=[
        "textual>=0.1.0",
        "httpx>=0.25.0",
    ],
    entry_points={
        "console_scripts": [
            "awesome=awesome_tui.app:main",
        ],
    },
    python_requires=">=3.10",
    author="12britz",
    author_email="",
    url="https://github.com/12britz/awesome-tui",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Terminal",
        "License :: OSI Approved :: MIT License",
    ],
)
