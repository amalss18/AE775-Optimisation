import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon

def get_turbine_lines(x, y, wind):
    normal = np.array([-wind[1]/(wind[0]+np.finfo(float).eps), 1])
    normal = normal/np.linalg.norm(normal)
    R = 41

    Z_H = 80  # Hub height of rotor in m
    Z_0 = 0.3  # Hub height of rotor in m
    alpha = 0.5 / (np.log(Z_H / Z_0))


    x_lines, y_lines = [], []
    for i in range(len(x)):
        turbine_pos = np.array([x[i], y[i]])

        pos1 = turbine_pos + np.array([0, R])
        pos2 = turbine_pos - np.array([0, R])

        plt.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]])

        dist = 150*R
        rl = alpha*dist + R

        pos4 = turbine_pos + np.array([dist, rl])
        pos3 = turbine_pos - np.array([0, rl]) + np.array([dist, 0])

        x_pos = [pos1[0], pos2[0], pos3[0], pos4[0]]
        y_pos = [pos1[1], pos2[1], pos3[1], pos4[1]]

        plt.fill(x_pos, y_pos, facecolor='lightsalmon', edgecolor='orangered', alpha=0.25)


def get_wake_plots(x, y, wind_dir=[12, 0]):
    """
    x, y: 1D arays are turbines coordinates
    wind: 1x2 array of x and y components of the wind.
    """

    get_turbine_lines(x, y, wind_dir)
    plt.scatter(x, y)
    plt.xlim(0, 4000)
    plt.ylim(0, 3500)
    plt.show()
    # plt.plot(x_lines, y_lines)


if __name__ == "__main__":
    x = np.random.random(5) * 1000
    y = np.random.random(5) * 1000

    get_wake_plots(x, y, wind_dir=[12, 0])

