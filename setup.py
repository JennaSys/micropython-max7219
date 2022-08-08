import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
from setuptools import setup
sys.path.append("..")
import sdist_upip

setup(name='micropython-max7219',
      version='0.2.1',
      description='MicroPython driver for MAX7219 with 7-segment modules',
      long_description=open('README.md').read(),
      url='https://github.com/JennaSys/micropython-max7219',
      author='John Sheehan',
      author_email='jennasyseng@gmail.com',
      licence='MIT',
      cmdclass={'sdist': sdist_upip.sdist},
      py_modules=['max7219', 'seven_segment_ascii']
)