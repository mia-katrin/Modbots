import matplotlib.pyplot as plt
import matplotlib.colors as mc
import numpy as np
from tqdm import tqdm

N = 64
TILES = 4

img = np.zeros((N*TILES,N*TILES,3))

x0 = N // 2 - 1
y0 = N // 2 - 1

maks = N

def random_tile(threshold):
    tile = np.zeros((TILES, TILES, 3))
    rands = np.random.normal(0.8, 0.4, (TILES, TILES))
    for x in range(TILES):
        for y in range(TILES):
            if rands[x,y] <= threshold:
                tile[x,y] = [255,255,255]
            else:
                tile[x,y] = [0,0,0]
    return tile

for r in tqdm(range(N*3//4, 0, -1)):
    for x in range(N):
        for y in range(N):
            if (x - x0)**2 + (y - y0)**2 <= r**2:
                img[x*TILES:x*TILES+TILES,y*TILES:y*TILES+TILES] = random_tile(r/(N/2))

plt.imshow(img.astype(np.uint8), vmin=0, vmax=255, cmap="gray")
plt.show()
plt.imsave("plane.png", img.astype(np.uint8))
