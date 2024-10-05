with open('m5out_64_128/stats.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if "board.processor.cores.core.mmu.dtb.rdMisses" in line:
            rdMisses = int(line.split()[1].strip())
        if "board.processor.cores.core.mmu.dtb.rdAccesses" in line:
            rdAccesses = int(line.split()[1].strip())
        if "board.processor.cores.core.mmu.dtb.wrMisses" in line:
            wrMisses = int(line.split()[1].strip())
        if "board.processor.cores.core.mmu.dtb.wrAccesses" in line:
            wrAccesses = int(line.split()[1].strip())
    print("Read Cache Hit Rate: ", 1 - rdMisses / rdAccesses)
    print("Write Cache Hit Rate: ",  1 - wrMisses / wrAccesses)