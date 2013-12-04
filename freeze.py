import sys
from cx_Freeze import setup, Executable

include_files = (
    "config.txt",
    "eu4cd/txt/",
    )

build_exe_options = {
    'optimize' : 2,
    'compressed' : True,
    'create_shared_zip' : True,
    'include_files' : include_files,
    }

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name = "eu4cd",
      version = "1.0",
      description = "My GUI application!",
      options = {"build_exe": build_exe_options},
      executables = [Executable("eu4cd.py", base=base)])
