# modularReinforcementLearning

# CONTINUOUS TASKS

#A2C
python3 main.py --env-name "RoboschoolHumanoid-v1" "RoboschoolHumanoidFlagrun-v1" "RoboschoolHumanoidFlagrunHarder-v1" --num-stack 1 --num-frames 1000000 --act_func "maxout"

#PPO
python3 main.py --env-name "RoboschoolHumanoid-v1" "RoboschoolHumanoidFlagrun-v1" "RoboschoolHumanoidFlagrunHarder-v1" --algo ppo --use-gae --vis-interval 1  --log-interval 1 --num-stack 1 --num-steps 2048 --num-processes 1 --lr 3e-4 --entropy-coef 0 --ppo-epoch 10 --num-mini-batch 32 --gamma 0.99 --tau 0.95 --num-frames 5000000 --act_func "tanh" --annealing_factor 1.0 --drop 0.5 --anneal
