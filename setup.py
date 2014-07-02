from cx_Freeze import setup, Executable


exe = Executable(script='trip of life.py',
                 base='Win32Gui')

includefiles = []
includes = []
excludes = []
packages = []
bin_path_excludes = []

setup(version='0',
      description='A game of life clone',
      author='YOU',
      name='Trip of life',
      options={'build_exe': {'compressed': False,
                             'excludes': excludes,
                             'packages': packages,
                             'include_files': includefiles,
                             'bin_excludes': bin_path_excludes}},
      executables=[exe])
