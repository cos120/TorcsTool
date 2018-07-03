"""
author: zj
file: torcs_env.py
time: 17-8-1
"""
import time
import copy
import scipy
from . import Tool
from .constant import *
import math
import os
import numpy as np
import subprocess
from itertools import count
from easydict import EasyDict as ed
from glob import glob
import random
# from keras.models import load_model
SPEED_X = -8
SPEED_Y = 1
SPEED_Z = 2
STEER = 3
BRAKE = 4
ACCEL = 5
# GEAR = 6
# CLUTCH = 7
TRACK_ANGLE = 0
TRACK_POS = 20
RPM = -1
RADIUS = 9


def clip(lo, x, hi):
    """

    :param lo:
    :param x:
    :param hi:
    :return: x -> [lo , hi]
    """
    return lo if x <= lo else hi if x >= hi else x
class TorcsEnv:
    terminal_judge_start = 100  # If after 100 timestep still no progress, terminated
    termination_limit_progress = 5  #
    def __init__(self,torcs_path,grab_img = True,memory_key = None):

        assert memory_key, 'you must specific shared memory key'
        torcs_path = '/home/bst2017/zj/software/bin'
        rel = '/home/bst2017/zj/software/torcs-1.3.7/data'
        self.track_category_name = track_category_name
        self.all_track_name = all_track_names
        os.system('ipcrm -M {}'.format(memory_key))
        command = '{}/torcs --key {}'.format(torcs_path, memory_key)
        self.torcs_proc = subprocess.Popen([command], shell=True, preexec_fn=os.setsid)
        time.sleep(1)
        self.tool = Tool.torcs_tool(grab_shot=grab_img ,key=memory_key)
        time.sleep(0.5)
        os.system('sh /home/bst2017/zj/projects/back_up_ddpg/autostart.sh')
        time.sleep(0.5)
        self.time_step = 0
        self.begin_protection = 0
        self.norm_factory = self.norm()

    def norm(self):
        norm = ed()
        norm.focus = 200.
        norm.speedX = 300.0
        norm.speedY = 300.0
        norm.speedZ = 300.0
        norm.angle = 3.1416
        norm.damage  = None
        norm.opponents = 200.
        norm.rpm = 10000.
        norm.track = 200.
        norm.trackPos = None
        norm.wheelSpinVel = 100.
        norm.radius = None
        norm.toleft = None
        norm.toright = None
        return norm

    def auto_shift(self):
        if 0 <= self.tool.speed < 40:
            self.tool.gear = 1
        elif 40 < self.tool.speed <= 80:
            self.tool.gear = 2
        elif 80 < self.tool.speed <= 120:
            self.tool.gear = 3
        elif 120 < self.tool.speed <= 160:
            self.tool.gear = 4
        elif 160 < self.tool.speed <= 200:
            self.tool.gear = 5
        elif 200 < self.tool.speed:
            self.tool.gear = 6

    def make_obs(self,obs):
        for k,v in self.norm_factory.items():
            setattr(obs,k,obs[k] / v if v else obs[k])
        # INFO
        # uncomment to scale angle to (0,1)
        #obs.angle = obs.angle / 2. + 0.5
        return obs

    def change_track(self,index = None,category = None):
        if index:
            track = self.all_track_name[index % len(self.all_track_name)]
        else:
            track = random.choice(self.all_track_name)
        self.tool.changeTrack(track.encode('utf-8'))
        self.tool.changeTrackOk('1'.encode('utf-8'))
        return track
        #self.tool.changeTrack('tracks/dirt/dirt-1/dirt-1.xml'.encode('utf-8'))

    #def change_track_ok(self):
    #    self.tool.changeTrackOk('1'.encode('utf-8'))

    def make_obs_origin(self):
        obs = ed()
        t = self.tool.get29Data
        for k,v in self.norm_factory.items():
            setattr(obs,k,t[k])
        return obs
    def restart(self):
        #self.change_track()
        self.tool.changeTrackOk('0'.encode('utf-8'))
        self.tool.restart()
        self.time_step = 0
        return self.make_obs_origin()

    def reset(self):
        origin = self.restart()
        return self.make_obs(origin)

    def step(self,actions):
        self.tool.steer, self.tool.accel ,self.tool.brake = actions
        self.auto_shift()
        is_stuck = self.tool.is_stuck
        is_finish = self.tool.is_finish

        self.time_step += 1
        obs = self.make_obs_origin()
        obs_pre = copy.deepcopy(obs)
        done = False
        track = obs['track']
        trackPos = obs['trackPos']
        sp = obs['speedX']
        damage = obs['damage']
        rpm = obs['rpm']
        progress = sp * np.cos(obs['angle']) - np.abs(sp * np.sin(obs['angle'])) - sp * np.abs(obs['trackPos'])
        reward = progress

        # collision detection
        if obs['damage'] - obs_pre['damage'] > 0:
            reward = -1
        if (abs(track.any()) > 1 or abs(trackPos) > 1):  # Episode is terminated if the car is out of track
            reward = -200
            done = True

        if self.terminal_judge_start < self.time_step: # Episode terminates if the progress of agent is small
           if progress < self.termination_limit_progress:
               print("No progress")
               done = True

        if np.cos(obs['angle']) < 0: # Episode is terminated if the agent runs backward
            done = True
        #done = (is_stuck or is_finish) and self.begin_protection > 10
        self.begin_protection += 1
        if is_finish:
            done = True
        #if self.begin_protection < 100:
        #    done = False
        return self.make_obs(obs), reward, done, {}

if __name__ == '__main__':
    env = TorcsEnv(None,memory_key=1234)

