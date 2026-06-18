import os.path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def ratioFunction(num1, num2):

    ratio12 = round(float(num1/num2), 2)
    return ratio12

def build_fb(values):
    y = np.array(values)
    mycolors = ["#47b9b2", "#ffd000"]
    plt.figure(figsize = (24, 24))
    plt.pie(y, normalize=True, startangle=90, colors = mycolors)

    plt.savefig(os.path.join('images', 'fb.png'), transparent=True)


def build_pb(values):
    y = np.array(values)
    mycolors = ["#003e43", "#d8d8d8"]
    plt.figure(figsize=(24, 24))
    plt.pie(y, normalize=True, startangle=90, colors=mycolors)

    plt.savefig(os.path.join('images', 'pb.png'), transparent=True)

