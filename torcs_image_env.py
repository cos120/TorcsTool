import TorcsTool.torcs_env as e
import copy
import numpy as np
import threading
import operator
import cv2
import os
class torcs_img_env(e.TorcsEnv):
    def __init__(self,torcs_path,grab_img = True,memory_key = None,indicator_model=None):
        '''
        inherent from torcs_env,
        :param torcs_path:
        :param grab_img:
        :param memory_key:
        :param indicator_model: image to indicator model, you need expose inference
                                api named 'inference'
        '''
        self.inference = indicator_model
        super(torcs_img_env,self).__init__(torcs_path,
                                           grab_img=grab_img,
                                           memory_key=memory_key)
        self.path = '/home/bst2017/zj/dataset/torcs/{}'.format(memory_key)
        try:
            os.mkdir(self.path)
        except:
            pass

        self.norm_factory = self.norm()

        self.get_data_list = ['angle', 'rpm', 'speedX', 'speedY', 'speedZ', 'wheelSpinVel', 'trackPos',
                              'toright', 'toleft','radius', 'track' ]

    def get_save_data(self,index):
        obs = self.make_obs_origin()
        data = np.hstack(operator.attrgetter(*self.get_data_list)(obs))
        img = obs.img[:,:,::-1]
        np.savetxt('{}/{}.txt'.format(self.path,str(index).zfill(5)),data,fmt='%4f',delimiter=' ')
        cv2.imwrite('{}/{}.png'.format(self.path,str(index).zfill(5)),img)

    def save(self):
        index = 0
        while True:
            while not self.tool.is_finish:
                self.get_save_data(index)
                index +=1
            self.change_track()
            self.tool.restart()
    def step(self,actions):
        self.tool.steer, self.tool.accel ,self.tool.brake = actions
        self.auto_shift()
        is_stuck = self.tool.is_stuck
        is_finish = self.tool.is_finish

        self.time_step += 1
        obs = self.make_obs_origin()
        obs_pre = copy.deepcopy(obs)
        #img = obs.img
        #indicators = self.indicator_model.ddpg_inference(img)
        #indicators = self.inference(img)
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
        #if self.begin_protection < 100:
        #    done = False
        return self.make_obs(obs), reward, done, {}

    def make_obs(self,obs):
        '''
        add indi to obs
        :param obs:
        :return:
        '''
        obs = super().make_obs(obs)
        obs.inds_t = self.inference(obs.img)

        return obs

    def norm(self):
        '''
        add img or obs won't return img
        :return:
        '''
        norm = super().norm()
        norm.img = None
        return norm
def save_data(key):
    env = torcs_img_env(None,memory_key=1234+key,indicator_model=None)
    env.save()
if __name__ == '__main__':
    from multiprocessing import Process
    ps = [Process(target=save_data,args=(i,)) for i in range(4)]
    for p in ps:
        p.start()

    for p in ps:
        p.join()
