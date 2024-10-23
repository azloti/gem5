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

class MyARMCPU(ArmO3CPU):
    LQEntries = 16
    SQEntries = 16
    LSQDepCheckShift = 0
    LFSTSize = 1024
    SSITSize = 1024
    decodeToFetchDelay = 1
    renameToFetchDelay = 1
    iewToFetchDelay = 1
    commitToFetchDelay = 1
    renameToDecodeDelay = 1
    iewToDecodeDelay = 1
    commitToDecodeDelay = 1
    iewToRenameDelay = 1
    commitToRenameDelay = 1
    commitToIEWDelay = 1
    fetchWidth = 3
    fetchBufferSize = 16
    fetchToDecodeDelay = 3
    decodeWidth = 3
    decodeToRenameDelay = 2
    renameWidth = 3
    renameToIEWDelay = 1
    issueToExecuteDelay = 1
    dispatchWidth = 6
    issueWidth = 8
    wbWidth = 8
    fuPool = O3_ARM_v7a.O3_ARM_v7a_FUP()
    iewToCommitDelay = 1
    renameToROBDelay = 1
    commitWidth = 8
    squashWidth = 8
    trapLatency = 13
    backComSize = 5
    forwardComSize = 5
    numPhysIntRegs = 128
    numPhysFloatRegs = 192
    numPhysVecRegs = 48
    numIQEntries = 32
    numROBEntries = 40

    switched_out = False
    branchPred = None

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

def create(args):
    cpu_class = MyARMCPU
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
        MyARMCPU,
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
    process = get_process(args.commands_to_run)

    system.workload = SEWorkload.init_compatible(process[0].executable)

    my_cpu = system.cpu_cluster.cpus[0]

    my_cpu.workload = process[0]


    # Here, optionally add branch prediction
    print("Current branch predictor: ", my_cpu.branchPred)
    # my_cpu.branchPred = O3_ARM_v7a.O3_ARM_v7a_BP()
    # print(my_cpu.branchPred)


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
