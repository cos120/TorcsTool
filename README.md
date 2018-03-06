# Welcome to TorcsTool

TorcsTool is a torcs client for reinforcement learning like [gym_torcs](https://github.com/ugo-nama-kun/gym_torcs). The client developed by udp has some delay when I grab images from Torcs, so TorcsTool develped by shared memory.

**This repo is for [torcs-1.3.7](http://sourceforge.net/projects/torcs/files/all-in-one/1.3.7/torcs-1.3.7.tar.bz2/download).**

 ## Getting Started

1. Download [torcs-1.3.7](http://sourceforge.net/projects/torcs/files/all-in-one/1.3.7/torcs-1.3.7.tar.bz2/download).

2. Create git repo, and apply patch.

   ```sh
   git apply --ignore-space-change --ignore-whitespace  torcs.patch
   ```

3. Compile and install torcs

4. Compile  and install `scr-server`  in your torcs folder.

5. Compile shared library.

   ```sh
   cd path/to/TorcsTool && make
   ```

6. Run `tool.py` and `torcs`

##  Api 

### get29Data

return 29 track data collected from scr_server.

1. angle: angle between track and car.
2. track: distance from car to track edge in 19 direction. You can modify direction in `src_server.cpp` about line 246 in my case.
3. speed(x|y|z): speed in x,y,z axis.
4. wheelSpinVel: rad speed of wheel
5. rpm: rpm

### image

return images of torcs. Default grab speed is 10 images per second. You can change grab speed by modifying count in `src/libs/raceengineclient/raceengine.cpp` about 767 line in my case.

### accel/steer/brake/clutch/gear

control car, just set the value.

### restart

restart game.

### is_stuck/is_hit_wall/is_finish

check car status. You can modity `ReOneStep` function in `src/libs/raceengineclient/raceengine.cpp` to change the status trigger.

## Dependency

1. torcs-1.3.7
2. python3
3. see `requirement.txt`

## License

TorcsTool is released under the [MIT License](https://opensource.org/licenses/MIT).

