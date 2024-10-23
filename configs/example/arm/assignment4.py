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

def get_process(cmd):
    cwd = os.getcwd()
    argv = shlex.split(cmd[0])

    process = Process(pid=100, cwd=cwd, cmd=argv, executable=argv[0])
    process.gid = os.getgid()

    return process

# Config options
enable_superscalar = False
enable_branch_pred = False
enable_smt = False

class MyCustomCPU(O3_ARM_v7a.O3_ARM_v7a_3):
    issueWidth = enable_superscalar and 8 or 1
    decodeWidth = enable_superscalar and 3 or 1
    commitWidth = enable_superscalar and 8 or 1
    squashWidth = enable_superscalar and 8 or 1
    fetchWidth = enable_superscalar and 3 or 1
    renameWidth = enable_superscalar and 3 or 1
    wbWidth = enable_superscalar and 8 or 1
    dispatchWidth = enable_superscalar and 6 or 1

def create(args):
    cpu_class = MyCustomCPU
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
        cpu_class,
        O3_ARM_v7a.O3_ARM_v7a_ICache,
        O3_ARM_v7a.O3_ARM_v7a_DCache,
        O3_ARM_v7a.O3_ARM_v7aL2,
    )

    system.addCaches(True, last_cache_level=2)

    system.mem_ranges = [AddrRange(start=0, size="256MB")]

    MemConfig.config_mem(MemOptions(), system)

    system.connect()

    process = get_process(args.commands_to_run)
    system.workload = SEWorkload.init_compatible(process[0].executable)

    my_cpu = system.cpu_cluster.cpus[0]
    my_cpu.workload = process[0]

    # Enable SMT
    if enable_smt: # Enable SMT
        my_cpu.numThreads = 2
        my_cpu.smtNumFetchingThreads = 2


    if not enable_branch_pred:
        my_cpu.branchPred = LocalBP() # Modified to disable branch prediction

    print("Current branch predictor: ", my_cpu.branchPred.__class__)

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
