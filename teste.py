import gym, roboschool
import numpy as np
#ls = ["HalfCheetah-v1", "Hopper-v1", "InvertedDoublePendulum-v1", "InvertedPendulum-v1", "Reacher-v1", "Swimmer-v1", "Walker2d-v1"]
ls = ["RoboschoolAnt-v1", "RoboschoolHopper-v1", "RoboschoolHumanoidFlagrun-v1", "RoboschoolInvertedPendulumSwingup-v1",
      "RoboschoolReacher-v1", "RoboschoolPong-v1", "RoboschoolHumanoid-v1", "RoboschoolHalfCheetah-v1",
      "RoboschoolInvertedPendulum-v1", "RoboschoolHumanoidFlagrunHarder-v1", "RoboschoolInvertedDoublePendulum-v1",
      "RoboschoolWalker2d-v1", "RoboschoolAtlasForwardWalk-v1"]
for l in ls:
    env = gym.make(l)
    env.reset()
    #print(dir(env))
    print(l, " env.action_space.n:", env.action_space, env.observation_space)
