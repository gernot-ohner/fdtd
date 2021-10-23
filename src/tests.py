import timeit

import common
import callers
import source as src


def normal_test(params, pml):
    """
    Runs a simulation described by "params" using the implementation chosen by the value of "pml".
    :param params: List[int, int, float, float, float, float, float, Tuple(float,float),
                        Tuple(float, float, float), function]
    :param pml: String
    """
    nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source = params

    if pml == "no":
        history = callers.call_npml(nx, ny, nt, dx, dy, dt, p, source)
    elif pml == "bpml":
        history = callers.call_bpml(nx, ny, nt, dx, dy, dt, p, pmlc, source, 0)
    elif pml == "cpml":
        history = callers.call_cpml(nx, ny, nt, dx, dy, dt, p, pmlc, source)
    else:
        print("Call this funtion with an argument specifying a PML implementation")

    common.plot_2d(history, nt)


def comparison_test(params):
    """
    Compares the behavior of the Berenger PML and the convolutional PML by runnning the simulation
    described by "params" with both implementations and plotting a cutthrough of each.
    :param params: List[int, int, float, float, float, float, float, Tuple(float,float),
                        Tuple(float, float, float), function]
    """
    nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source = params

    history_bpml = callers.call_bpml(nx, ny, nt, dx, dy, dt, p, pmlc, source)
    history_cpml = callers.call_cpml(nx, ny, nt, dx, dy, dt, p, pmlc, source)

    ny = int(params[1] / 2)
    b_snap = history_bpml[:, ny, -1]
    c_snap = history_cpml[:, ny, -1]

    names = ["BPML", "CPML"]
    labels = ["Space [Cells]", "Hz [V/m]"]
    snaps = [b_snap, c_snap]

    common.plot_snaps(names, labels, snaps)


def pml_test(params, pml):
    """
    Runs a simulation described by "params" using the implementation chosen by the value of "pml"
    once with the simulation size (nx, ny) determined in "params and once with (3*nx, 3*ny).
    Both are plotted in a cutthrough of the size of the smaller simulation.
    :param params: List[int, int, float, float, float, float, float, Tuple(float,float),
                        Tuple(float, float, float), function]
    :param pml: string
    """
    nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source = params

    big_nx = nx * 3
    big_ny = ny * 3

    s_nx_h = int(nx / 2)
    b_nx_h = int(big_nx / 2)
    b_ny_t1 = int(big_ny / 3)
    b_ny_t2 = int(2 * big_ny / 3)

    big_p = (p[0] * 3, p[1] * 3)

    if pml == "cpml":
        def thing(mx, my, q):
            return callers.call_cpml(mx, my, nt, dx, dy, dt, q, pmlc, source)
    elif pml == "bpml":
        def thing(mx, my, q):
            return callers.call_bpml(mx, my, nt, dx, dy, dt, q, pmlc, 0, source)
    else:
        print("This function needs to be called with an argument specifying the PML implementation.")

    small_history = thing(nx, ny, p)
    big_history = thing(big_nx, big_ny, big_p)

    small_snap = small_history[s_nx_h, :, -1]
    big_snap = big_history[b_nx_h, b_ny_t1:b_ny_t2, -1]

    snaps = [small_snap, big_snap]
    labels = ["Space [Cells]", "Hz [V/m]"]
    names = ["Small simulation with PML", "Large simulation"]
    common.plot_snaps(names, labels, snaps)


def time_test(params, rep=100, num=1):
    """
    Executes simulations without a PML, with a Berenger PML and a convolutional PML for "rep" times.
    Computes minimum, mean and standard deviation of the computation times using the minimum time of
    the PML-less implementation as a base case and representing all values of multiples of that.
    :param params: List[int, int, float, float, float, float, float, Tuple(float,float),
                        Tuple(float, float, float), function]
    :param rep: int
    :param num: int
    """
    nx, ny, lx, ly, dx, dy, dt, t, p, pmlc = params

    def berengercaller():
        callers.call_bpml(nx, ny, t, dx, dy, dt, p, pmlc)

    def cpmlcaller():
        callers.call_cpml(nx, ny, t, dx, dy, dt, p, pmlc)

    def nopmlcaller():
        callers.call_npml(nx, ny, t, dx, dy, dt, p)

    npml_times = timeit.repeat(nopmlcaller, repeat=rep, number=num)
    bpml_times = timeit.repeat(berengercaller, repeat=rep, number=num)
    cpml_times = timeit.repeat(cpmlcaller, repeat=rep, number=num)

    names = ["noPML", "BPML", "CPML"]
    results = common.compare([npml_times, bpml_times, cpml_times])
    for i in range(len(names)):
        print(names[i], ": ", results[i])


def time_trivial(params, rep=100, num=1):
    """
    Executes simulations without a normal source determined by "source" and a dummy "null source" for "rep" times.
    Computes minimum, mean and standard deviation of the computation times using the minimum time of
    the trivial simulation as a base case and representing all values of multiples of that.
    :param params: List[int, int, float, float, float, float, float, Tuple(float,float),
                        Tuple(float, float, float), function]
    :param rep: int
    :param num: int
    """
    nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source = params

    def trivial_caller():
        callers.call_npml(nx, ny, nt, dx, dy, dt, p, src.null_source)

    def nopmlcaller():
        callers.call_npml(nx, ny, nt, dx, dy, dt, p, source)

    trivial_times = timeit.repeat(trivial_caller, number=num, repeat=rep)
    nopml_times = timeit.repeat(nopmlcaller, number=num, repeat=rep)

    names = ["trivial", "nopml"]
    results = common.compare([trivial_times, nopml_times])
    for i in range(len(names)):
        print(names[i], ": ", results[i])


def loss_test(params):
    """
    Calls 3 simulations described by the parameters "params" with different conductivities on the entire domain.
    Plots cut-throughs of the results at time step 50.
    :param params: List[int, int, float, float, float, float, float, Tuple(float,float),
                        Tuple(float, float, float), function]
    """
    nx, ny, lx, ly, dx, dy, dt, t, p, pmlc, source = params

    history1 = callers.call_bpml(nx, ny, t, dx, dy, dt, p, pmlc, 0.1, source)
    history2 = callers.call_bpml(nx, ny, t, dx, dy, dt, p, pmlc, 0.01, source)
    history3 = callers.call_bpml(nx, ny, t, dx, dy, dt, p, pmlc, 0.001, source)

    nyh = int(ny / 2)
    names = ["sigma = 0", "sigma = 0.01", "sigma = 0.001"]
    labels = ["Hz [V/m]", "Space / [Cells]"]
    snaps = [history1[:, nyh, 50], history2[:, nyh, 50], history3[:, nyh, 50]]
    common.plot_snaps(names, labels, snaps)
