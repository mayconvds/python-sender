import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "includes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for
# a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Sender",
    version="0.1",
    description="Sender xDxD",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py",
                            copyright="Copyright (C) 2021 Sender",
                            base=base,
                            icon="4990671.ico",
                            shortcutName="Sender"
                            )]
)
