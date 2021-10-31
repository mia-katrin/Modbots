import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from skimage.color import hsv2rgb

def plot_voxels(image, title="Plotted voxels"):
    colors = np.where(image == 0, "#000000ff", "#ffffffff")
    hues = ["#000000ff"]
    for i in range(1, int(np.max(image))+1):
        hue = i/(np.max(image)) * 0.9 + 0.1
        rgb = hsv2rgb([[[hue, 1.0, 1.0]]])[0][0]*255
        rgb_hex = [hex(int(elem))[2:] for elem in rgb]
        for j in range(3):
            if len(rgb_hex[j]) == 1:
                rgb_hex[j] = '0' + rgb_hex[j]

        string = f"#{rgb_hex[0]}{rgb_hex[1]}{rgb_hex[2]}88"
        colors[np.where(image == i)] = string

        hues.append(string)

    fig, (ax1, ax2) = plt.subplots(1, 2, gridspec_kw = {'width_ratios':[19, 1]})

    ax = fig.add_subplot(1,2,1, projection='3d')
    ax.voxels(image, facecolors=colors, edgecolor='k')

    cmap = mpl.colors.ListedColormap(hues)
    norm = mpl.colors.Normalize(vmin=0, vmax=np.max(image))
    ax2 = fig.add_subplot(1,2,2)
    cb1 = mpl.colorbar.ColorbarBase(
        ax2, cmap=cmap,
        norm=norm,
        orientation='vertical'
    )
    fig.suptitle(title, fontsize=16)

def plot_hist(image, label=None, elim_0=True):
    bins, counts = np.unique(image, return_counts=True)
    if elim_0:
        counts = counts[1:]
        bins = bins[1:]
    plt.bar(bins, counts, label=label)
