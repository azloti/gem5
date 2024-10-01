from m5.objects import *

# Set up CPU and Memory System
cpu = X86TimingSimpleCPU()

# TLB Configuration for Instruction and Data TLB
# You can set different page sizes and number of entries here
cpu.itb = X86TLB(size=64, entry_type='instruction')  # 64-entry instruction TLB
cpu.dtb = X86TLB(size=64, entry_type='data')  # 64-entry data TLB
cpu.isa = [X86ISA()]

cpu.createInterruptController()




# Set the virtual memory system parameters
# Assuming you're setting a page size of 4KB (default)
system = System(cpu=cpu,
                mem_mode='timing',  # Use 'timing' mode for detailed simulation
                mem_ranges=[AddrRange('512MB')])  # Physical memory size

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# You can experiment with different page sizes by modifying the TLB
# For example, using a 2MB page size:
# cpu.itb.page_size = '2MB'
# cpu.dtb.page_size = '2MB'

# The rest of your system configuration follows


# Set the binary to run as the workload (e.g., 'tests/test-progs/hello/bin/x86/linux/hello')
system.workload = SEWorkload.init_compatible("hello")

process = Process()
process.cmd = ["hello"]
# Set the cpu to use the process as its workload and create thread contexts
cpu.workload = process
cpu.createThreads()  # Create threads for the CPU (important)

# Memory system (DDR3 or any other memory model)
system.membus = SystemXBar()
system.system_port = system.membus.cpu_side_ports

cpu.interrupts[0].pio = system.membus.mem_side_ports
cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Add cache configuration here if needed (L1, L2, etc.)

# Set up the system clock and run the simulation
root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting simulation...")
exit_event = m5.simulate()

print("Simulation finished after", exit_event.getCause())
