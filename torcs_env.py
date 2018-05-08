"""
author: zj
file: torcs_env.py
time: 17-8-1
"""
import time

import scipy

#from Tool import torcs_tool
#import Tool
import math
import os
import numpy as np

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


class Env:
    def __init__(self, torcs_tool):
        self.tool = torcs_tool
        self.step_count = 0
        # os.system('torcs&')
        # time.sleep( 1 )
        # os.system( 'sh autoChangeTrack.sh practice' )
        self.begin_protection = 0
        self.control = {
            0: [type(self.tool).__dict__['steer'], 0.05],
            1: [type(self.tool).__dict__['steer'], -1],
            2: [type(self.tool).__dict__['steer'], 1],
            3: [type(self.tool).__dict__['accel'], 0.05],
            4: [type(self.tool).__dict__['accel'], 1],
            5: [type(self.tool).__dict__['brake'], 0.05],
            6: [type(self.tool).__dict__['brake'], 0.2]
        }
        # self.model = load_model("/home/zj/PycharmProjects/py3/self-driving/nvidia/final.h5")

    def reset(self):
        self.tool.restart()
        self.begin_protection = 0
        self.step_count = 0

    def steerControl(self, steer):
        # axis 0 left = -1 right = 1
        # axis 1 up = -1 down = 1
        axis_steer = steer
        if (math.fabs(axis_steer) > 0.8):  # steer
            ratio = 0.1
        else:
            ratio = 0.2
        self.tool.steer = clip(-1, self.tool.track_angle /
                               scipy.pi - ratio * axis_steer, 1)

    def reward(self, S, is_stuck):
        S = S[0]
        speed = S[SPEED_X] * 300
        angle = S[TRACK_ANGLE] * 3.1416
        track_pos = S[TRACK_POS]
        reward = speed * np.cos(angle) - np.abs(speed *
                                                np.sin(angle)) - speed * np.abs(track_pos)
        if is_stuck:
            reward = -200
        elif self.tool.is_hit_wall:
            reward = -10
        elif speed < 2:
            reward = - np.abs(track_pos)
        return reward

    def changeTrack(self):
        os.system('sh autoChangeTrack.sh change')

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

    def step_one_action(self, planning, action):

        # for plan ,ac in zip(planning,action):
        action = float(action)
        # print("planning: {}  action:{}".format(planning,action))

        control = self.control[planning]
        control[0].fset(self.tool, control[1] * 0.5)
        self.auto_shift()
        S = self.tool.get29Data
        is_stuck = self.tool.is_stuck
        is_finish = self.tool.is_finish

        self.step_count += 1
        _reward = self.reward(S, is_stuck)

        done = (is_stuck or is_finish) and self.begin_protection > 10
        self.begin_protection += 1

        return S, _reward, done, is_stuck

    def step(self, action):
        action = np.squeeze(action)

        self.tool.steer = action[0]
        self.tool.accel = action[1]
        self.tool.brake = action[2]
        # self.tool.gear = action['gear']

        self.auto_shift()
        # time.sleep(5e-5)
        # image = self.tool.image
        S = self.tool.get29Data
        is_stuck = self.tool.is_stuck
        is_finish = self.tool.is_finish

        # S = {
        #     # 'image': image,
        #     'angle': angle,
        #     'speed': speed}

        self.step_count += 1
        _reward = self.reward(S, is_stuck)
        # if self.step_count > 500 and _reward < 5:
        #     self.step_count = 0
        #     done = True
        #     return S , _reward , done
        done = (is_stuck or is_finish) and self.begin_protection > 10
        self.begin_protection += 1
        # print("stuck: {} finish: {} "
        #       "pos: {} angle: {}".format(is_stuck, is_finish , S[TRACK_POS],S[TRACK_ANGLE]))
        return S, _reward, done, is_stuck
