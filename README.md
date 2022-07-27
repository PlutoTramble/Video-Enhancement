# Auto Video Enhancer
A script written in Python that automates the process of enhancing digital videos with the help of a few AIs. When the video is under a resolution of 960x540 it will double the resolution with SRMD. Also, if the video's frame per second is under 50, it will run the interpolation 2 times, and the rest of the time it will be only one time.


## About RIFE and SRMD
### RIFE - Real time video interpolation
RIFE is used to interpolate videos.
For more information, feel free to go on hzwer's repository: https://github.com/hzwer/arXiv2020-RIFE
Also, make sure to ckeck out nihui's for vulkan support: https://github.com/nihui/rife-ncnn-vulkan

### SRMD
SRMD is used to add more resolution when needed.
For more information, feel free to go on cszn's repository: https://github.com/cszn/SRMD
Also, make sure to ckeck out nihui's for vulkan support: https://github.com/nihui/srmd-ncnn-vulkan

## Installation
### Dependencies
* Has only have been tested on Ubuntu and its derivative
* Python 3.8.6
  * opencv2
* ffmpeg
* A relativaly fast GPU and CPU

### Where to put stuff
* Copy or move your video in the input directory.
* unpack the latest release https://github.com/nihui/rife-ncnn-vulkan/releases into the "AIs" directory
* unpack the latest release https://github.com/nihui/srmd-ncnn-vulkan/releases into the "AIs" directory

