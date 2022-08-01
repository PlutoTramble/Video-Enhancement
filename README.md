# Auto Video Enhancer
A script written in Python that automates the process of enhancing digital videos with the help of a few AIs. When the video is under a resolution of 720x480, or depending your options, it will double the resolution with SRMD. Also, you can set a target frames per second in the options and ifrnet will interpolate it.


## About ifrnet and SRMD
### ifrnet
ifrnet is used to interpolate videos.
For more information, feel free to go on ltkong218's repository: https://github.com/ltkong218/IFRNet
Also, make sure to ckeck out nihui's for vulkan support: https://github.com/nihui/ifrnet-ncnn-vulkan

### SRMD
SRMD is used to add more resolution when needed.
For more information, feel free to go on cszn's repository: https://github.com/cszn/SRMD
Also, make sure to ckeck out nihui's for vulkan support: https://github.com/nihui/srmd-ncnn-vulkan

## How to use
To get help
```bash
$ python3 main.py -h

main.py -i <input-file/folder> -o <output-file/folder>
-h to show argument help
-t to indicate where you want to create your temporary directory (To reduce wear on your storage)
-f to target a specific framerate. Defaults at 60. Can't go more than 180.
-r if the specified resolution is under what you wrote in this format : <number>x<number> it will double the resolution. Defaults at 720x480
```

## Installation
### Dependencies
* Has only have been tested on Ubuntu and its derivative
* Python 3
  * opencv2
* ffmpeg
* A relativaly fast GPU and CPU

### Where to put stuff
* unpack the latest release https://github.com/nihui/ifrnet-ncnn-vulkan/releases into the "AIs" directory
* unpack the latest release https://github.com/nihui/srmd-ncnn-vulkan/releases into the "AIs" directory

