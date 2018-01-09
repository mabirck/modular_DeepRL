import os
import types

import numpy as np
import torch
from torch.autograd import Variable
from baselines.common.vec_env.dummy_vec_env import DummyVecEnv
from baselines.common.vec_env.vec_normalize import VecNormalize

from envs import make_env
from utils import process_file

def evaluate(actor_critic, ob_rms, env_name, act_func, seed, k):

    num_stack=1
    log_interval = 1
    load_dir='./trained_models/ppo/'
    #sd = np.random.randint(1000, size=1)
    sd =[1]

    env = make_env(env_name, int(sd[0]), 0, './tmp/test/'+str(seed)+'_'+act_func+'_')
    env = DummyVecEnv([env])


    #actor_critic, ob_rms = \
    #            torch.load(os.path.join(load_dir, 'ppo_'+env_name+'_'+act_func+ '_'+str(seed)+".pt"))


    if len(env.observation_space.shape) == 1:
        env = VecNormalize(env, ret=False)
        env.ob_rms = ob_rms

        # An ugly hack to remove updates
        def _obfilt(self, obs):
            if self.ob_rms:
                obs = np.clip((obs - self.ob_rms.mean) / np.sqrt(self.ob_rms.var + self.epsilon), -self.clipob, self.clipob)
                return obs
            else:
                return obs
        env._obfilt = types.MethodType(_obfilt, env)
        render_func = env.venv.envs[0].render
    else:
        render_func = env.envs[0].render

    obs_shape = env.observation_space.shape
    obs_shape = (obs_shape[0] * num_stack, *obs_shape[1:])
    current_obs = torch.zeros(1, *obs_shape)
    states = torch.zeros(1, actor_critic.state_size)
    masks = torch.zeros(1, 1)


    def update_current_obs(obs):
        shape_dim0 = env.observation_space.shape[0]
        obs = torch.from_numpy(obs).float()
        if num_stack > 1:
            current_obs[:, :-shape_dim0] = current_obs[:, shape_dim0:]
        current_obs[:, -shape_dim0:] = obs


    #render_func('human')
    obs = env.reset()
    update_current_obs(obs)

    if env_name.find('Bullet') > -1:
        import pybullet as p

        torsoId = -1
        for i in range(p.getNumBodies()):
            if (p.getBodyInfo(i)[0].decode() == "torso"):
                torsoId = i

    for i in range(5000):
        value, action, _, states = actor_critic.act(Variable(current_obs, volatile=True),
                                                    Variable(states, volatile=True),
                                                    Variable(masks, volatile=True),
                                                    deterministic=True)
        #if i % 1000 == 0:
        #    print("STEP: ", i)
        states = states.data
        cpu_actions = action.data.squeeze(1).cpu().numpy()
        # Obser reward and next obs
        obs, reward, done, _ = env.step(cpu_actions)

        masks.fill_(0.0 if done else 1.0)

        if current_obs.dim() == 4:
            current_obs *= masks.unsqueeze(2).unsqueeze(2)
        else:
            current_obs *= masks
        update_current_obs(obs)

        if env_name.find('Bullet') > -1:
            if torsoId > -1:
                distance = 5
                yaw = 0
                humanPos, humanOrn = p.getBasePositionAndOrientation(torsoId)
                p.resetDebugVisualizerCamera(distance, yaw, -20, humanPos)

        #render_func('human')

        #print(dir(env.envs[0]))

    process_file(env_name, act_func, sd[0], seed, k)
