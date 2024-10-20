# Define the keys to search for
metrics = {
    "system.cpu_cluster.cpus.ipc": None,
    "system.cpu_cluster.cpus.cpi": None,
    "system.cpu_cluster.cpus.power_model.staticPower": None,
    "simSeconds": None,
    "system.cpu_cluster.cpus.icache.demandMissRate::total": None,
    "system.cpu_cluster.cpus.dcache.demandMissRate::total": None
}

# Path to the stats.txt file
file_path = 'm5out/stats.txt'

dynamic_power_values = []
highest_power = None
lowest_power = None

# Read the file and extract the values
with open(file_path, 'r') as file:
    for line in file:

        if line.startswith("system.cpu_cluster.cpus.power_model.dynamicPower"):
            dynamic_power_values.append(float(line.split()[1]))  # Add the dynamic power value
        else:
            for key in metrics:
                if line.startswith(key):
                    if metrics[key] is None:
                        metrics[key] = line.split()[1]  # Get the value after the key

if dynamic_power_values:
    average_dynamic_power = sum(dynamic_power_values) / len(dynamic_power_values)

    # Find the highest and lowest power values
    highest_power = max(dynamic_power_values)
    lowest_power = min(dynamic_power_values)
else:
    average_dynamic_power = None

# Print the extracted values
for key, value in metrics.items():
    if value is not None:
        print(f"{key}: {value}")
    else:
        print(f"{key}: Not found")

if average_dynamic_power is not None:
    print(f"Average dynamic power: {average_dynamic_power}")
    print(f"Highest power: {highest_power}")
    print(f"Lowest power: {lowest_power}")
else:
    print("No dynamic power values found")