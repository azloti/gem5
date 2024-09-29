with open('m5out/stats.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if "system.cpu.mmu.dtb.rdMisses" in line:
            rdMisses = int(line.split()[1].strip())
        if "system.cpu.mmu.dtb.rdAccesses" in line:
            rdAccesses = int(line.split()[1].strip())
        if "system.cpu.mmu.dtb.wrMisses" in line:
            wrMisses = int(line.split()[1].strip())
        if "system.cpu.mmu.dtb.wrAccesses" in line:
            wrAccesses = int(line.split()[1].strip())
        if "system.mem_ctrl.requestorReadAvgLat::cpu.inst" in line:
            instructionRdAvgLat = float(line.split()[1].strip())
            print("Instruction Read Average Latency: ", instructionRdAvgLat)
        if "system.mem_ctrl.requestorReadAvgLat::cpu.data" in line:
            dataRdAvgLat = float(line.split()[1].strip())
            print("Data Read Average Latency: ", dataRdAvgLat)
        if "system.mem_ctrl.dram.avgMemAccLat" in line:
            avgMemAccLat = float(line.split()[1].strip())
            print("Average Memory Access Latency: ", avgMemAccLat) 
    print("Read Cache Hit Rate: ", 1 - rdMisses / rdAccesses)
    print("Write Cache Hit Rate: ",  1 - wrMisses / wrAccesses)