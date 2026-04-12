from setuptools import setup, find_packages

setup(
    name="awesome-tui",
    version="0.1.0",
    description="Browse awesome lists in the terminal",
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
    author="Your Name",
    author_email="your@email.com",
)
