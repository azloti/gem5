# Import m5 library and available SimObjects
import m5
from m5.objects import *

# Add the caches scripts to our path
m5.util.addToPath("../")

from learning_gem5.part1.caches import *

import argparse

parser = argparse.ArgumentParser(description='A simple system with 2-level cache.')
parser.add_argument("--l1i_size",
                    help=f"L1 instruction cache size. Default: 16kB.")
parser.add_argument("--l1d_size",
                    help="L1 data cache size. Default: Default: 64kB.")
parser.add_argument("--l2_size",
                    help="L2 cache size. Default: 256kB.")

options = parser.parse_args()

# Create the system, setup clock and power for clock
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Memory configuration
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("8192MB")]

# CPU configuration (using ArmTimingSimpleCPU for ARM) and Memory bus
system.cpu = ArmTimingSimpleCPU()
system.membus = SystemXBar()

# Create cache and connect it to the System CPU
system.cpu.icache = L1ICache(options)
system.cpu.dcache = L1DCache(options)
# system.cpu.icache.assoc = 8                   # Change associativity of icache
# system.cpu.dcache.assoc = 8                   # Change associativity of dcache
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Create an L2 bus to connect L1 caches to the L2 cache
system.l2bus = L2XBar()

system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

# Create L2 cache and connect it to the L2 bus and the memory bus.
system.l2cache = L2Cache(options)
# system.l2cache.assoc = 16                     # Change associativity of l2cache
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)

# Connecting PIO and interrupt port to membus (Necessary for X86)
system.cpu.createInterruptController()

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# Connect the CPU MMU to the membus
# system.cpu.mmu = ARMMMU()
# system.cpu.mmu.itb.size = 2                     # Change TLB size
# system.cpu.mmu.dtb.size = 2                     # Change TLB size
# system.cpu.mmu.connectWalkerPorts(system.membus.cpu_side_ports, system.membus.cpu_side_ports)

# Setting up memory controller to connect to the membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

thispath = os.path.dirname(os.path.realpath(__file__))
binary = os.path.join(
    thispath,
    "../../",
    "tests/test-progs/hello/bin/arm/linux/hello",
)

# Setting up workload
system.workload = SEWorkload.init_compatible(binary)
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

# Simulation Configuration
root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()

print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")