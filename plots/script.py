import json, glob, ast
import matplotlib.pyplot as plt
import numpy as np
import pandas
import difflib
ewma = pandas.stats.moments.ewma

def compatibleMatrix(data):

    minor = [len(d) for d in data]
    print minor, "MINOOR"
    minor = min(minor)
    reshaped_data = np.array([d[:minor] for d in data])
    return reshaped_data

def workersMeanReward(path, game):
    #print path, game
    total_rewards = list()
    files = glob.glob(path+'*/*/*/*')
    #print files
    for f in files:
        total_rewards.append(getData(f, 0))
    print len(total_rewards)

    total_rewards = compatibleMatrix(total_rewards)
    total_rewards = np.array(total_rewards)
    total_rewards = np.average(total_rewards, axis=0)
    return total_rewards

def workersLength(path, game):
    total_rewards = list()
    files = glob.glob(path+'*/*/*/*')

    for f in files:
        #print f
        total_rewards.append(np.cumsum(getData(f, 1)))
        #print total_rewards

    #print "LENGTH ->>>>>>>>>", len(total_rewards)
    total_rewards = compatibleMatrix(total_rewards)
    total_rewards = np.array(total_rewards)
    total_rewards = np.average(total_rewards, axis=0)
    #print total_rewards
    return total_rewards

def fix_name(paths):
    return [(name.split('/')[-2]) for name in paths]

def getMin(data):
    mini = [x[-1] for x in data]
    #print mini
    return min(mini)

def plotData(data, length, game2plot, lines, colors, axis, from_where, L, C):
    #mini = getMin(length)

    name = game2plot

    ax = plt.subplot(L, C, axis)
    ax.set_title(name+' with '+from_where, fontsize=10, style='italic')
    print data, length
    for k, (d, l) in enumerate(zip(data, length)):
        print l, d, "GUUUUUYS"
        plt.scatter(l, d)
    plt.grid()

def getData(path, key):
    with open(path, 'r') as f:
        #print f
        #data = json.load(f)
        total = 0
        rewards = list()
        for k, line in enumerate(f):
            if k == 0 or k == 1:
                continue
            #print k, path
            #print line
            #break
            elements = line.split(',')
            #print(key[0], type(key[0]), "SHIIIIIT")

            rewards.append(float(elements[0]))

        return np.array(rewards)

def main():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--log_dir', help='Log dir to plot', type=str, default='Breakout')
    parser.add_argument('--env', help='environments ID to plot', type=str, default='NoFrameskip-v4')
    args = parser.parse_args()

    # THREE GAMES FROM DEEP MIND
    """all_games =  ["DemonAttack", "Pong", "Qbert"]
    joint_games =  ["Pong/Qbert", "DemonAttack/Qber", "DemonAttack/Pong"]

    all_paths = ["DemonAttack", "Pong", "Qbert"]
    labels = ['A3C_att', "A3C_multitask_att"]
    L = 3
    C = 1"""

    all_games =  ["Qbert"]
    joint_games =  ["DemonAttack/Pong"]

    all_paths = ["Qbert"]
    labels = ['A3C_att', "A3C_multitask_att"]
    L = 1
    C = 1


    colors = ["black", "gray", "blue", "red"]
    lines = [':', '-.', '--', '-']
    fig = plt.figure()
    for axis, (current, game2plot) in enumerate(zip(all_paths, all_games)):
        paths = glob.glob("./data/{}/".format(current+'/*/'))
        #print(paths)
        data = list()
        length = list()
        log_dir = args.log_dir.split('/')[0]
        print paths, "_____________________________________"
        for game in paths:
            #print("GAME", game)
            data.append(ewma(workersMeanReward(game, game2plot+args.env), 20))
            length.append(workersLength(game, game2plot+args.env))
            print("VOOOOLTEI")

        print len(data), len(length)
        print "LENGHTSSSSSSSSSSSSSSs", length
        plotData(data, length, game2plot, lines, colors, axis+1, joint_games[axis], L, C)

    plt.legend(labels, loc='best',  shadow=True, ncol=3)

    plt.tight_layout()
    fig.savefig("all"+'.pdf')
    plt.show()
if __name__ == '__main__':
    main()
