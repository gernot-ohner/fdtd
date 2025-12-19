"""Test functions for FDTD simulations."""
import timeit
from typing import List, Callable

import common
import callers
import sources


def normal_test(params: List, pml_type: str) -> None:
    """
    Run a simulation using the specified PML implementation.
    
    Args:
        params: Parameter list [nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source]
        pml_type: PML type string ("no", "bpml", or "cpml")
    """
    nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source = params
    
    if pml_type == "no":
        history = callers.call_npml(nx, ny, nt, dx, dy, dt, p, source)
    elif pml_type == "bpml":
        history = callers.call_bpml(nx, ny, nt, dx, dy, dt, p, pmlc, source, 0)
    elif pml_type == "cpml":
        history = callers.call_cpml(nx, ny, nt, dx, dy, dt, p, pmlc, source)
    else:
        raise ValueError(f"Invalid PML type: {pml_type}. Must be 'no', 'bpml', or 'cpml'")
    
    common.plot_2d(history, nt)


def comparison_test(params: List) -> None:
    """
    Compare BPML and CPML implementations by plotting cut-throughs.
    
    Args:
        params: Parameter list [nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source]
    """
    nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source = params
    
    history_bpml = callers.call_bpml(nx, ny, nt, dx, dy, dt, p, pmlc, source)
    history_cpml = callers.call_cpml(nx, ny, nt, dx, dy, dt, p, pmlc, source)
    
    ny_half = int(ny / 2)
    b_snap = history_bpml[:, ny_half, -1]
    c_snap = history_cpml[:, ny_half, -1]
    
    names = ["BPML", "CPML"]
    labels = ["Space [Cells]", "Hz [V/m]"]
    snaps = [b_snap, c_snap]
    
    common.plot_snaps(names, labels, snaps)


def pml_test(params: List, pml_type: str) -> None:
    """
    Compare small and large simulations with PML.
    
    Runs simulation with original size and 3x size, plotting cut-throughs.
    
    Args:
        params: Parameter list [nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source]
        pml_type: PML type string ("bpml" or "cpml")
    """
    nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source = params
    
    big_nx = nx * 3
    big_ny = ny * 3
    
    s_nx_h = int(nx / 2)
    b_nx_h = int(big_nx / 2)
    b_ny_t1 = int(big_ny / 3)
    b_ny_t2 = int(2 * big_ny / 3)
    
    big_p = (p[0] * 3, p[1] * 3)
    
    if pml_type == "cpml":
        def run_sim(mx: int, my: int, q: tuple):
            return callers.call_cpml(mx, my, nt, dx, dy, dt, q, pmlc, source)
    elif pml_type == "bpml":
        def run_sim(mx: int, my: int, q: tuple):
            return callers.call_bpml(mx, my, nt, dx, dy, dt, q, pmlc, 0, source)
    else:
        raise ValueError(f"Invalid PML type: {pml_type}. Must be 'bpml' or 'cpml'")
    
    small_history = run_sim(nx, ny, p)
    big_history = run_sim(big_nx, big_ny, big_p)
    
    small_snap = small_history[s_nx_h, :, -1]
    big_snap = big_history[b_nx_h, b_ny_t1:b_ny_t2, -1]
    
    snaps = [small_snap, big_snap]
    labels = ["Space [Cells]", "Hz [V/m]"]
    names = ["Small simulation with PML", "Large simulation"]
    common.plot_snaps(names, labels, snaps)


def time_test(params: List, rep: int = 100, num: int = 1) -> None:
    """
    Benchmark different PML implementations.
    
    Executes simulations without PML, with BPML, and with CPML multiple times
    and compares computation times.
    
    Args:
        params: Parameter list [nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source]
        rep: Number of repetitions
        num: Number of times to run per repetition
    """
    nx, ny, lx, ly, dx, dy, dt, t, p, pmlc, source = params
    
    def berengercaller():
        callers.call_bpml(nx, ny, t, dx, dy, dt, p, pmlc, source)
    
    def cpmlcaller():
        callers.call_cpml(nx, ny, t, dx, dy, dt, p, pmlc, source)
    
    def nopmlcaller():
        callers.call_npml(nx, ny, t, dx, dy, dt, p, source)
    
    npml_times = timeit.repeat(nopmlcaller, repeat=rep, number=num)
    bpml_times = timeit.repeat(berengercaller, repeat=rep, number=num)
    cpml_times = timeit.repeat(cpmlcaller, repeat=rep, number=num)
    
    names = ["noPML", "BPML", "CPML"]
    results = common.compare([npml_times, bpml_times, cpml_times])
    for i, name in enumerate(names):
        print(f"{name}: min={results[i][0]:.4f}, mean={results[i][1]:.4f}, std={results[i][2]:.4f}")


def time_trivial(params: List, rep: int = 100, num: int = 1) -> None:
    """
    Benchmark source function overhead.
    
    Compares simulation with normal source vs null source to measure
    source function overhead.
    
    Args:
        params: Parameter list [nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source]
        rep: Number of repetitions
        num: Number of times to run per repetition
    """
    nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source = params
    
    def trivial_caller():
        callers.call_npml(nx, ny, nt, dx, dy, dt, p, sources.null_source)
    
    def nopmlcaller():
        callers.call_npml(nx, ny, nt, dx, dy, dt, p, source)
    
    trivial_times = timeit.repeat(trivial_caller, number=num, repeat=rep)
    nopml_times = timeit.repeat(nopmlcaller, number=num, repeat=rep)
    
    names = ["trivial", "nopml"]
    results = common.compare([trivial_times, nopml_times])
    for i, name in enumerate(names):
        print(f"{name}: min={results[i][0]:.4f}, mean={results[i][1]:.4f}, std={results[i][2]:.4f}")


def loss_test(params: List) -> None:
    """
    Test effect of different conductivity values.
    
    Runs simulations with different conductivity values and plots cut-throughs.
    
    Args:
        params: Parameter list [nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source]
    """
    nx, ny, lx, ly, dx, dy, dt, t, p, pmlc, source = params
    
    history1 = callers.call_bpml(nx, ny, t, dx, dy, dt, p, pmlc, source, 0.1)
    history2 = callers.call_bpml(nx, ny, t, dx, dy, dt, p, pmlc, source, 0.01)
    history3 = callers.call_bpml(nx, ny, t, dx, dy, dt, p, pmlc, source, 0.001)
    
    nyh = int(ny / 2)
    names = ["sigma = 0.1", "sigma = 0.01", "sigma = 0.001"]
    labels = ["Hz [V/m]", "Space / [Cells]"]
    snaps = [history1[:, nyh, 50], history2[:, nyh, 50], history3[:, nyh, 50]]
    common.plot_snaps(names, labels, snaps)
