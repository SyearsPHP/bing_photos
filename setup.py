from setuptools import setup, find_packages

setup(
    name="LRC Lyrics Downloader",
    version="1.0.0",
    description="Automatic LRC lyrics downloader for macOS with batch processing",
    author="Zony",
    packages=find_packages(),
    install_requires=[
        'PyQt6>=6.4.0',
        'mutagen>=1.45.0',
        'requests>=2.28.0',
        'unidecode>=1.3.0',
    ],
    entry_points={
        'console_scripts': [
            'lrc-downloader=main:main',
        ],
    },
    python_requires='>=3.7',
)
