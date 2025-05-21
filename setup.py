#!/usr/bin/env python3
import os
import setuptools
from setuptools.command.build_py import build_py

# Хак для тимчасових директорій
tmp_dir = os.path.join(os.getcwd(), '.tmp')
try:
    os.makedirs(tmp_dir, exist_ok=True)
    os.environ['TMPDIR'] = tmp_dir
    os.environ['TMP'] = tmp_dir
    os.environ['TEMP'] = tmp_dir
    import tempfile
    tempfile.tempdir = tmp_dir
    print(f"setup.py: Using temp directory {tmp_dir}")
except Exception as e:
    print(f"setup.py: Failed to set up temp dir: {e}")

class CustomBuildPy(build_py):
    def run(self):
        # Повторюємо патч перед запуском
        tmp_dir = os.path.join(os.getcwd(), '.tmp')
        try:
            os.makedirs(tmp_dir, exist_ok=True)
            os.environ['TMPDIR'] = tmp_dir
            os.environ['TMP'] = tmp_dir
            os.environ['TEMP'] = tmp_dir
            import tempfile
            tempfile.tempdir = tmp_dir
        except:
            pass
        super().run()

setuptools.setup(
    name="smaystr-bot",
    version="1.0.8",
    author="smaystr",
    author_email="smaystr@example.com",
    description="Telegram bot with temporary directory fixes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    cmdclass={
        'build_py': CustomBuildPy,
    },
) 