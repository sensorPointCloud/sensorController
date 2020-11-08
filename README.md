**Usage**
- Code tested with ST NUCLEO-F767ZI board
- Board running MicroPython. https://micropython.org/, install and flash board according to instructions

**Running on Linux (Ubuntu)**
- After connecting the board, make sure it has the right permissions, e.g. sudo chmod 666 /dev/ttyACM*
- Install Remote MicroPython shell: _pip install rshell_
- Install serial terminal Picocom: _sudo apt-get install picocom_
- Use script to copy files and connect to board: _source copy_files_and_connect_
- It is now possible to import libraries and call functions