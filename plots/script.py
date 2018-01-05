import json, glob, ast
import matplotlib.pyplot as plt
import numpy as np
import pandas
import difflib
ewma = pandas.stats.moments.ewma

def compatibleMatrix(data, minor):
    reshaped_data = np.array([d[:minor] for d in data])
    return reshaped_data

def workersMeanReward(path, game):
    total_rewards = list()
    files = glob.glob(path+'*/*/*/*')
    for f in files:
        total_rewards.append(getData(f, 0))
    return avgNestedLists(total_rewards)

def workersLength(path, game):
    total_length = list()
    files = glob.glob(path+'*/*/*/*')

    for f in files:
        print f
        total_length.append(getLength(f, 1))
    return avgNestedLists(total_length, True)

def fix_name(paths):
    return [(name.split('/')[-2]) for name in paths]

def getMin(data):
    mini = [len(x)  for x in data]
    #print mini
    mini = min(mini)
    return mini

def plotData(data, length, game2plot, lines, colors, axis, from_where, L, C):
    #mini = getMin(length)

    name = game2plot

    ax = plt.subplot(L, C, axis)
    ax.set_title(name+' with '+from_where, fontsize=10, style='italic')
    for k, (d, l) in enumerate(zip(data, length)):
        plt.plot(l, d)
    #plt.xlim((0, mini))
    plt.grid()

def getData(path, key):
    with open(path, 'r') as f:
        #data = json.load(f)
        total = 0
        rewards = list()
        for k, line in enumerate(f):
            if k == 0 or k == 1:
                continue
            #break
            elements = line.split(',')
            rewards.append(float(elements[key]))
        return np.array(rewards)

def getLength(path, key):
    with open(path, 'r') as f:
        #data = json.load(f)
        total = 0
        length = list()
        prev = 0
        for k, line in enumerate(f):
            if k == 0 or k == 1:
                continue
            #break

            elements = line.split(',')
            if float(elements[key]) < 0:
                print("NEEEGAAATIVE")
            total+=float(elements[key])
            #if prev > total:
            #    print("WRONG")
            length.append(total)
            prev = total
        #print np.array(length).shape
        return length

def avgNestedLists(nested_vals, val=False):
    """
    Averages a 2-D array and returns a 1-D array of all of the columns
    averaged together, regardless of their dimensions.
    """
    output = []
    maximum = 0
    for lst in nested_vals:
        if len(lst) > maximum:
            maximum = len(lst)
    for index in range(maximum): # Go through each index of longest list
        temp = []
        for lst in nested_vals: # Go through each list
            if index < len(lst): # If not an index error
                temp.append(lst[index])
        if index !=0 and output[index-1] > np.nanmean(temp, axis=0) and val == True:
            #print "WRONG", output[index-1], temp
            aux = output[index-1] + 100
            #output[index-1] = np.nanmean(temp, axis=0)
            output.append(aux)
        else:
            output.append(np.nanmean(temp, axis=0))
    return output

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def check(data, length):
    print(len(data), len(length))
    print("### DATA STUFF ###", type(data))

    for d in data:
        print(d.shape)

    print("### LENGTH STUFF ###", type(length))
    print(length)
    for l in length:
        print(l.shape)
        past = 0
        for node in l:
            if node < past:
                pass
                #print past, node
                #print "wrong"
            past = node
def main():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--log_dir', help='Log dir to plot', type=str, default='Breakout')
    parser.add_argument('--env', help='environments ID to plot', type=str, default='NoFrameskip-v4')
    args = parser.parse_args()

    # THREE GAMES FROM DEEP MIND #
    #############################

    # all_games =  ["DemonAttack", "Pong", "Qbert"]
    # joint_games =  ["Pong/Qbert", "DemonAttack/Qber", "DemonAttack/Pong"]
    #
    # all_paths = ["DemonAttack", "Pong", "Qbert"]
    # labels = ['A3C', 'A3C_multitask', 'A3C_multitask_maxout', 'A3C_multitask_lwta']
    # L = 3
    # C = 1


    # all_games =  ["Qbert"]
    # joint_games =  ["DemonAttack/Pong"]
    #
    # all_paths = ["Qbert"]
    # labels = ['A3C', 'A3C_multitask', 'A3C_multitask_maxout']
    # L = 1
    # C = 1

    #
    # all_games =  ["DemonAttack"]
    # joint_games =  ["DemonAttack/Pong"]
    #
    # all_paths = ["DemonAttack"]
    # labels = ['A3C', 'A3C_multitask', 'A3C_multitask_maxout']
    # L = 1
    # C = 1
    #
    # all_games =  ["Pong"]
    # joint_games =  ["DemonAttack/Pong"]
    #
    # all_paths = ["Pong"]
    # labels = ['A3C', 'A3C_multitask', 'A3C_multitask_maxout']
    # L = 1
    # C = 1


    ####################### TRANSFER #########################################
    # all_games =  ["NameThisGame"]
    # joint_games =  ["DemonAttack/Pong"]
    #
    # all_paths = ["NameThisGame"]
    # labels = ['A3C', 'A3C_att', "A3C_multitask_att_transfer"]
    # L = 1
    # C = 1

    # all_games =  ["UpNDown"]
    # joint_games =  ["DemonAttack/Pong"]
    #
    # all_paths = ["UpNDown"]
    # labels = ['A3C', 'A3C_att', "A3C_multitask_att_transfer"]
    # L = 1
    # C = 1

    # all_games =  ["Reacher"]
    # joint_games =  ["Pong/Qbert"]
    #
    # all_paths = ["Reacher"]
    # labels = ['PPO', 'PPO_att', 'A3C_multitask', "A3C_multitask_att", "1step_att", "10step_att_5e5", "7_att_Demo_1e-5"]
    # L = 1
    # C = 1

    ###################################### PPO #############################
    # all_games =  ["Humanoid"]
    # joint_games =  ["Matter?"]
    #
    # all_paths = ["Humanoid"]
    # labels = ['PPO','PPO_maxout', 'PPO_multitask', "PPO_multitask_maxout"]
    # L = 1
    # C = 1

    # all_games =  ["Humanoid"]
    # joint_games =  ["Matter?"]
    #
    # all_paths = ["Humanoid"]
    # labels = ['PPO_multitask', "PPO_multitask_maxout"]
    # L = 1
    # C = 1

    # all_games =  ["HumanoidFlag"]
    # joint_games =  ["Matter?"]
    #
    # all_paths = ["HumanoidFlag"]
    # labels = ['PPO_multitask', "PPO_multitask_maxout", "1step_att", "10step_att_5e5", "7_att_Demo_5e-5"]
    # L = 1
    # C = 1

    all_games =  ["Humanoid", "HumanoidFlag", "HumanoidFlagHarder"]
    joint_games =  ["Matter?", "Matter?", "Matter?"]

    all_paths = ["Humanoid", "HumanoidFlag", "HumanoidFlagHarder"]
    labels = ['PPO_multitask', "PPO_multitask_maxout", "PPO_multitask_lwta"]
    L = 3
    C = 1



    colors = ["black", "gray", "blue", "red"]
    lines = [':', '-.', '--', '-']
    fig = plt.figure()
    for axis, (current, game2plot) in enumerate(zip(all_paths, all_games)):
        print(current)
        paths = glob.glob("./data/{}/".format(current+'/*/'))
        paths = sorted(paths)
        data = list()
        length = list()
        log_dir = args.log_dir.split('/')[0]
        for game in paths:
            print(game)
            data.append(ewma(np.array(workersMeanReward(game, game2plot+args.env)), 15))
            length.append(np.array(workersLength(game, game2plot+args.env)))
        check(data, length)
        plotData(data, length, game2plot, lines, colors, axis+1, joint_games[axis], L, C)
    from matplotlib.font_manager import FontProperties

    fontP = FontProperties()
    fontP.set_size('small')
    #plt.legend(labels, loc='bottom',  shadow=True, ncol=8, prop=fontP, bbox_to_anchor=(0.5, -0.3))
    plt.legend(labels, loc='best')

    plt.tight_layout()
    fig.savefig("all"+'.pdf')
    plt.show()
if __name__ == '__main__':
    main()
