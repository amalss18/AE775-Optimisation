import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


def write_run_info(
    x0,
    n,
    bounds,
    Tmax,
    Tmin,
    alpha,
    Markov_no,
    per_max,
    diameter,
    height,
    z_0,
    windspeed_array,
    theta_array,
    wind_prob,
    Ns,
):
    print("#" * 80)
    print("Run parameters")
    print("#" * 80)
    print("N", n)
    print("x\n", x0[::2])
    print("#" * 80)
    print("y\n", x0[1::2])
    print("#" * 80)
    print("bounds\n", bounds)
    print("#" * 80)
    print("diameter", diameter)
    print("height", height)
    print("z0", z_0)
    print("#" * 80)
    print("Tmax", Tmax)
    print("Tmin", Tmin)
    print("alpha", alpha)
    print("Markov no", Markov_no)
    print("Ns", Ns)
    print("per max", per_max)
    print("#" * 80)


def annealing(
    x0,
    fn_obj,
    bounds,
    Tmax,
    Tmin,
    alpha,
    Markov_no,
    per_max,
    diameter,
    height,
    z_0,
    windspeed_array,
    theta_array,
    wind_prob,
    Ns,
    restart=False,
):
    if not restart:
        x_best = x0.copy()
        x = x0.copy()
        T = Tmax

        cost = fn_obj(
            x0,
            bounds,
            diameter,
            height,
            z_0,
            windspeed_array,
            theta_array,
            wind_prob,
        )
        cost_best = cost
    else:
        print("#"*80, "\n\nRESTARTING SOLUTION\n\n")
        T, x, cost, x_best, cost_best = np.load("restart.npy", allow_pickle = True)
        print("from T= {}\ncost = {}\ncost_best = {}".format(T, cost, cost_best))
        print("#"*80)
        print("#"*80)

    xi = np.zeros_like(x0)

    n = len(x0)
    pert = per_max*np.ones(n)
    one_hot = np.eye(n)
    accept = np.zeros(n)
    n_iter = int(-np.log(T/Tmin)//np.log(alpha)) +1
    iter_no = 1

    print(n_iter)

    # with IncrementalBar("Sim_Anneal", max=n_iter, suffix="%(percent).1f%% time_elapsed:[%(elapsed)ds] estimated_time:[%(eta)ds]") as bar:
    try:
        for _ in tqdm(range(n_iter)):
            for lm in range(Ns):
                for i in range(Markov_no):
                    rand_nos = 2*pert*(2*np.random.random(n) -1 )
                    for k in range(n):
                        xi = x + one_hot[k]* rand_nos
                        cost_i = fn_obj(xi, bounds, diameter, height, z_0, windspeed_array, theta_array, wind_prob)
                        dcost = cost_i - cost

                        if dcost < 0:
                            x = xi.copy()
                            cost = cost_i
                            accept[k] += 1
                            # print("in 1")

                            if cost < cost_best:
                                cost_best = cost
                                x_best = x.copy()
                                print("Current Best", - cost_best/1e6, flush = True)
                        elif np.exp(-dcost / T) > np.random.random():
                            accept[k] += 1
                            x = xi.copy()
                            cost = cost_i
                    #end for k
                #end for i (Markov No)

                accepted_per = accept/(Markov_no)
                mh = accepted_per > 0.6
                ml = accepted_per <0.4
                mm = 1 - (mh+ml)
                pert = pert * ((1 + 2*(accepted_per-0.6)/0.4)*mh 
                    + ml/(1 + 2*(0.4-accepted_per)/0.4) + mm)
                print(accepted_per*100)
                accept.fill(0)
                # print(pert)

            #end for lm 
            iter_no +=1
            T = alpha * T
        #end for _ tqdm()
        print("T = ", T)
        return (x_best, cost_best)
    except KeyboardInterrupt:
        print("\n Oops....\n\tsaving current state")
        restart = np.array([T, x, cost, x_best, cost_best], dtype=object)
        np.save( "restart.npy", restart)
        print("created Restert file")
        return (x_best, cost_best)



if __name__ == "__main__":

    # from ..common.test_functions import Bohachevsky, himmel
    from ..common.layout import Layout, random_layout
    from ..common.cost import objective

    # from ..common.mosetti_cost import objective
    from ..common.windrose import read_windrose
    from ..common.wake_visualization import get_wake_plots
    import sys
    import time

    plt.style.use("dark_background")

    diameter = 82
    height = 80
    z_0 = 0.3
    xmax = 4000
    ymax = 3500

    # diameter = 40
    # height = 60
    # z_0 = 0.3
    # xmax = 2000
    # ymax = 2000

    n = 10
    xbound = [0, xmax]
    ybound = [0, ymax]
    bounds = np.array([xbound, ybound])


    filename = "siman_tejas_{}_{}".format(n, int(time.time()))
    grid = 20

    # windspeed_array, theta_array, wind_prob = read_windrose()
    windspeed_array = np.array([12])
    theta_array = np.array([0])
    wind_prob = np.array([1])

    # layout = Layout( np.ones(n)*1000, np.linspace(10, xmax, n), n).layout
    layout = random_layout(n, xbound, ybound, grid).layout
    # plt.plot(layout[::2], layout[1::2], "b*")
    cost_in = objective(
        layout,
        bounds,
        diameter,
        height,
        z_0,
        windspeed_array,
        theta_array,
        wind_prob,
    )

    # sim anneal related parameters
    alpha = 0.87
    pert_max = 1500
    Markov_no = 40
    Ns = 20
    Tmax = 1000 * np.abs(cost_in)
    Tmin = np.abs(cost_in) * 10e-10


    sys.stdout = open("./opti/results/"+filename+".txt", "w")
    write_run_info(
        layout,
        n,
        bounds,
        Tmax,
        Tmin,
        alpha,
        Markov_no,
        pert_max,
        diameter,
        height,
        z_0,
        windspeed_array,
        theta_array,
        wind_prob,
        Ns,
    )
    print("initial_cost = \t" + str(cost_in))
    #### Start Annealing #####
    a = time.time()
    xf, cb = annealing(
        layout,
        objective,
        bounds,
        Tmax,
        Tmin,
        alpha,
        Markov_no,
        pert_max,
        diameter,
        height,
        z_0,
        windspeed_array,
        theta_array,
        wind_prob,
        Ns,
        False,
    )
    

    b = time.time()
    time_required = b - a
    print("final cost =   \t" + str(cb))
    print("time required", time_required)
    sys.stdout.close()

    algo_data = [
        "Sim_anneal",
        "cost_model: {}\nMarkov: {}\nNS: {}\nTmax: {}\nTmin: {}".format(
            "Tejas",Markov_no, Ns, Tmax, Tmin
        ),
        "n_turb: {}\ndiameter: {}\nheight:{}\nprofit: {:.1f}\ntime: {:.3f}s".format(
            n, diameter, height, -cb , b-a
        ),
        filename,
    ]
    get_wake_plots(
        xf[::2],
        xf[1::2],
        bounds,
        diameter,
        height,
        z_0,
        windspeed_array,
        theta_array,
        wind_prob,
        algo_data
    )