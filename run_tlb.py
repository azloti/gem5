from gem5.utils.requires import requires
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (MESITwoLevelCacheHierarchy,)
from gem5.isas import ISA
from gem5.components.processors.cpu_types import CPUTypes
from gem5.resources.resource import Resource
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent
from gem5.components.processors.simple_processor import SimpleProcessor

from m5.objects import *
from pathlib import Path

# Here we setup a MESI Two Level Cache Hierarchy.
cache_hierarchy = MESITwoLevelCacheHierarchy(
    l1d_size="32KiB",
    l1d_assoc=8,
    l1i_size="32KiB",
    l1i_assoc=8,
    l2_size="256kB",
    l2_assoc=16,
    num_l2_banks=1,
)

memory = SingleChannelDDR3_1600("2GiB")

processor = SimpleProcessor(cpu_type=CPUTypes.TIMING, isa=ISA.X86, num_cores=1)

onlyCore = processor.cores[0].get_simobject()

# Set the TLB sizes: 64 entries
onlyCore.mmu.dtb = X86TLB(size=128, entry_type='data')  # Data TLB (64 entries, 4-way set associative)
onlyCore.mmu.itb = X86TLB(size=128, entry_type='instruction')  # Instruction TLB (64 entries, 4-way set associative)

# Here we setup the board. The X86Board allows for Full-System X86 simulations.
board = X86Board(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Run ps -o min_flt,maj_flt 1 to get the number of minor and major page faults

command = "echo 'Started, calculating page fault rate:';" \
        + "var=$(ps -o min_flt,maj_flt 1;);" \
        + "echo $var;" \
        + "m5 exit;"


board.set_kernel_disk_workload(
    kernel=Resource("x86-linux-kernel-5.4.49",),
    disk_image=Resource("x86-ubuntu-18.04-img"),
    readfile_contents=command,
    # checkpoint=Path("output/timing_cpu_checkpoint")
)

simulator = Simulator(
    board=board,
)
simulator.run()