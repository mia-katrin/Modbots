from modbots.creature_types.configurable_individual import Individual
from config_util import get_config_from_folder, get_config_no_args
from modbots.evaluate import get_env, evaluate, close_env, set_env_variables

import matplotlib.pyplot as plt
import numpy as np
import multiprocessing
import matplotlib as mpl
from skimage.color import hsv2rgb

def spawn(ind, env, side_channel):
    ind.prepare_for_evaluation()
    side_channel.send_string(ind.body_to_str())

    env.reset()
    for i in range(1):
        env.step()

def get_coordinates(ind):
    config = get_config_no_args()
    config.experiment.headless = True

    # Evaluate
    set_env_variables(config=config)

    env, side_channel, param_channel = get_env()
    spawn(ind, env, side_channel)

    return side_channel.coordinates

def get_center_of_mass(coordinates):
    return np.sum(coordinates, axis=0) #/ len(coordinates)

def plot_coordinates3D(coordinates):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    coordinates = np.array(coordinates)

    ax.scatter(
        coordinates[:,0],
        coordinates[:,1],
        coordinates[:,2]
    )

    ax.set_xlabel('X Accumulated')
    ax.set_ylabel('Y Accumulated')
    ax.set_zlabel('Z Accumulated')

def unique_coordinates_count(coordinates):
    counts = {}
    for coordinate in coordinates:
        coordinate = tuple(coordinate) # so it can be hashed and used as dict key
        counts.setdefault(coordinate, 0) # add coordinate to dict
        counts[coordinate] += 1 # increment count for coordinate
    uniques = list(counts.keys())

    return len(uniques)

scaler = 2
x_start = -70 // scaler
x_end = 71 // scaler
y_start = -70 // scaler
y_end = 71 // scaler
z_start = -20 // scaler
z_end = 90 // scaler

N = x_end + abs(x_start)
M = y_end + abs(y_start)
O = z_end + abs(z_start)

def plot_voxels(coordinates, brain):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    image = np.zeros((N, M, O))

    for i in range(len(coordinates)):
        fit = coordinates[i][1] if coordinates[i][1] < 30 else 30

        x, y, z = np.round(coordinates[i][0] / scaler)
        x, y, z = int(x+abs(x_start)), int(y+abs(y_start)), int(z+abs(z_start))

        if x < 0 or y < 0 or z < 0:
            print("Ah O")

        image[x, y, z] = fit if fit > image[x, y, z] else image[x, y, z]

        coordinates[i] = coordinates[i][0]

    cmap = plt.cm.get_cmap("viridis", 31)
    colors = np.zeros((N, M, O, 4))

    for i in range(0, 31):
        colors[np.where(image >= i)] = cmap.colors[i]

    ax.voxels(
        image,
        facecolors=colors
    )

    ax.set_xlabel('X Accumulated')
    ax.set_ylabel('Y Accumulated')
    ax.set_zlabel('Z Accumulated')

    ax.set_xticks(list(np.arange(0,N,10/scaler)))
    ax.set_yticks(list(np.arange(0,M,10/scaler)))
    ax.set_zticks(list(np.arange(0,O,10/scaler)))

    ax.set_xticklabels(list(range(x_start*scaler,x_end*scaler,10)))
    ax.set_yticklabels(list(range(y_start*scaler,y_end*scaler,10)))
    ax.set_zticklabels(list(range(z_start*scaler,z_end*scaler,10)))

    print(
        brain.title(),
        np.sum(np.where(image > 0, 1, 0)),
        unique_coordinates_count(coordinates)
    )

def return_collapse_fits_image(coordinates):
    image = np.zeros((N, O))

    for i in range(len(coordinates)):
        fit = coordinates[i][1] if coordinates[i][1] < 30 else 30

        x, y, z = np.round(coordinates[i][0] / scaler)
        x, y, z = int(x+abs(x_start)), int(y+abs(y_start)), int(z+abs(z_start))

        image[x, z] = fit if fit > image[x, z] else image[x, z]

    return image

def plot_coordinates2D(coordinates):

    img = np.zeros((60,60))

    for coor, fit in coordinates:
        x = 33 + int(round(coor[0]))
        y = 10 + int(round(coor[2]))

        if x < 0 or y < 0:
            raise IndexError(f"Index out of range {x}, {y}")
        if fit > img[x, y]:
            img[x, y] = fit

    plt.figure()
    plt.imshow(img)


def get_center_coor(ind):
    return get_center_of_mass(get_coordinates(ind))

pool = None
def get_run_coor(folder):
    global pool
    config = get_config_from_folder(folder)

    all_inds = []
    for indNr in range(0,500):
        ind = Individual.unpack_ind(
            folder + f"/bestInd{indNr}",
            config
        )
        all_inds.append(ind)

    if pool == None:
        pool = multiprocessing.Pool(10)
    res = pool.map(get_center_coor, all_inds)

    return res

if __name__ == "__main__":
    runNrs = [
        "run16166"
    ]

    coordinates = []
    for runNr in runNrs:

        path = f"remote_results/experiments500/{runNr}" # run13966 # run13326
        for indNr in range(499,500):
            ind = Individual.unpack_ind(path + f"/bestInd{indNr}", get_config_from_folder(path))

            """center = get_center_of_mass(get_coordinates(ind))
            coordinates.append((center, ind.fitness))"""
            coordinates = get_coordinates(ind)

    close_env()

    plot_coordinates3D(
        coordinates
    )
    plt.show()
