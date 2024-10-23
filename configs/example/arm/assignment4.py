import argparse
import os
import shlex

import m5
from m5.objects import *
from m5.util import addToPath

m5.util.addToPath("../..")

import devices
from common import (
    MemConfig,
)
from common.cores.arm import (
    O3_ARM_v7a,
)

class MemOptions:
    def __init__(self):
        self.mem_type = "DDR3_1600_8x8"
        self.mem_channels = 2

def get_processes(cmd):
    cwd = os.getcwd()
    argv = shlex.split(cmd[0])

    process = Process(pid=100, cwd=cwd, cmd=argv, executable=argv[0])
    process.gid = os.getgid()

    return [process]

def create(args):
    cpu_class = O3_ARM_v7a.O3_ARM_v7a_3
    mem_mode = cpu_class.memory_mode()

    system = devices.SimpleSeSystem(
        mem_mode=mem_mode,
    )

    num_cores = 1

    # Add CPUs to the system. A cluster of CPUs typically have
    # private L1 caches and a shared L2 cache.
    system.cpu_cluster = devices.ArmCpuCluster(
        system,
        num_cores,
        "512MHz",
        "1.2V",
        O3_ARM_v7a.O3_ARM_v7a_3,
        O3_ARM_v7a.O3_ARM_v7a_ICache,
        O3_ARM_v7a.O3_ARM_v7a_DCache,
        O3_ARM_v7a.O3_ARM_v7aL2,
    )

    # Create a cache hierarchy for the cluster. We are assuming that
    # clusters have core-private L1 caches and an L2 that's shared
    # within the cluster.
    system.addCaches(True, last_cache_level=2)

    # Tell components about the expected physical memory ranges. This
    # is, for example, used by the MemConfig helper to determine where
    # to map DRAMs in the physical address space.
    system.mem_ranges = [AddrRange(start=0, size="256MB")]

    # Configure the off-chip memory system.
    MemConfig.config_mem(MemOptions(), system)

    # Wire up the system's memory system
    system.connect()

    # Parse the command line and get a list of Processes instances
    # that we can pass to gem5.
    processes = get_processes(args.commands_to_run)
    if len(processes) != num_cores:
        print(
            "Error: Cannot map %d command(s) onto %d CPU(s)"
            % (len(processes), args.num_cores)
        )
        sys.exit(1)

    system.workload = SEWorkload.init_compatible(processes[0].executable)

    # Assign one workload to each CPU
    for cpu, workload in zip(system.cpu_cluster.cpus, processes):
        cpu.workload = workload

    return system


def main():
    parser = argparse.ArgumentParser(epilog=__doc__)

    parser.add_argument(
        "commands_to_run",
        metavar="command(s)",
        nargs="*",
        help="Command(s) to run",
    )
    
    args = parser.parse_args()

    root = Root(full_system=False)
    root.system = create(args)

    m5.instantiate()
    event = m5.simulate()

    print(f"{event.getCause()} ({event.getCode()}) @ {m5.curTick()}")

if __name__ == "__m5_main__":
    main()
