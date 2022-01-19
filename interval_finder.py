import os

configs = {}

for name in os.listdir("experiments"):
    if name.startswith("run") and name[3] == "6" and 631 <= int(name[3:]) <= 660:
        runNr = int(name[3:])
        for files in os.listdir("experiments/" + name):
            if files.endswith(".cfg"):
                if files not in configs.keys():
                    configs[files] = []
                configs[files].append(runNr)

print(configs)
