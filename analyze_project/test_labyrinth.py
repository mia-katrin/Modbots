import matplotlib.pyplot as plt
import numpy as np

class Maze:
    class Tile:
        def __init__(self, coor):
            self.coor = coor
            self.children = []

    def __init__(self, N, M, scale):
        # Assuming odd numbers
        assert N%2 == 1 and M%2 == 1, "We only use odd numbers!"
        assert scale >= 3, "Scale can only be a number larger than 2"

        self.N, self.M = N, M
        self.scale = 10

        self._create_maze()

    def _create_maze(self):
        set_of_tiles = []

        for x in range(self.N):
            for y in range(self.M):
                set_of_tiles.append(self.Tile((x,y)))

        self.root = set_of_tiles[self.M//2]
        self.end = set_of_tiles[(self.N-1)*self.M + self.M//2]

        self.set_of_tiles = set(set_of_tiles)

        self._connect_recursive(self.root, self.set_of_tiles)
        self._make_solution()

    def _find_neighbors(self, start_tile):
        # Neighbors of (0, 3)
        # (0, 2)
        # (0, 4)
        # (1, 3)

        neighbors = []
        for tile in self.set_of_tiles:
            diff = abs(tile.coor[0] - start_tile.coor[0]) + abs(tile.coor[1] - start_tile.coor[1])
            if diff == 1:
                neighbors.append(tile)

        return neighbors

    def _connect_recursive(self, tile, set_of_tiles):
        set_of_tiles.remove(tile)

        while len(self._find_neighbors(tile)) != 0:
            neighbors = self._find_neighbors(tile)

            index = np.random.randint(0, len(neighbors))
            new_child = neighbors[index]
            tile.children.append(new_child)
            self._connect_recursive(new_child, set_of_tiles)

    def _make_solution(self):
        self.solution = []
        self._get_solution_recursive(self.root, self.solution)

    def _get_solution_recursive(self, tile, solution):
        if tile == self.end:
            solution.append(self.end)
            return True

        for child in tile.children:
            if self._get_solution_recursive(child, solution):
                solution.append(tile)
                return True

    def _color_horizontal(self, tile, t, offsetbegin, offsetend, color):
        row = tile.coor[0]*self.scale
        if tile.coor[1] < t.coor[1]:
            low = tile.coor[1]*self.scale + offsetbegin
            high = t.coor[1]*self.scale + offsetend
        else:
            low = t.coor[1]*self.scale + offsetbegin
            high = tile.coor[1]*self.scale + offsetend

        self.grid[
            row+offsetbegin : row + offsetend,
            low : high
        ] = color

    def _color_vertical(self, tile, t, offsetbegin, offsetend, color):
        column = tile.coor[1]*self.scale
        if tile.coor[0] < t.coor[0]:
            low = tile.coor[0]*self.scale + offsetbegin
            high = t.coor[0]*self.scale + offsetend
        else:
            low = t.coor[0]*self.scale + offsetbegin
            high = tile.coor[0]*self.scale + offsetend

        self.grid[
            low:high,
            column+offsetbegin : column + offsetend
        ] = color

    def _color_recursive(self, tile):
        self.grid[
            tile.coor[0]*self.scale+1 : tile.coor[0]*self.scale + self.scale-1,
            tile.coor[1]*self.scale+1 : tile.coor[1]*self.scale + self.scale-1
        ] = (255,255,255)

        for t in tile.children:
            if tile.coor[0] == t.coor[0]:
                self._color_horizontal(tile, t, 1, self.scale-1, (255,255,255))
            elif tile.coor[1] == t.coor[1]:
                self._color_vertical(tile, t, 1, self.scale-1, (255,255,255))
            else:
                print("OOps")
            self._color_recursive(t)

    def _color_solution(self):
        color = (255,0,255)

        for tile, tile2 in zip(self.solution[:-1], self.solution[1:]):

            if tile.coor[0] == tile2.coor[0]:
                self._color_horizontal(tile, tile2, self.scale//4+1, self.scale*3//4, color)
            elif tile.coor[1] == tile2.coor[1]:
                self._color_vertical(tile, tile2, self.scale//4+1, self.scale*3//4, color)

        self.grid[
            0 : self.scale//2,
            self.root.coor[1]*self.scale+self.scale//4+1 : self.root.coor[1]*self.scale + self.scale*3//4
        ] = color

        self.grid[
            (self.N-1)*self.scale + self.scale//2 : (self.N-1)*self.scale + self.scale,
            self.end.coor[1]*self.scale+self.scale//4+1 : self.end.coor[1]*self.scale + self.scale*3//4
        ] = color

    def get_maze_image(self, solution_colored=False):
        self.grid = np.zeros((self.N*self.scale,self.M*self.scale,3))
        self._color_recursive(self.root)

        if solution_colored:
            self._color_solution()

        self.grid = np.pad(self.grid, ((1,1),(1,1),(0,0)))

        self.grid[
            0:2,
            (self.M*self.scale)//2 - self.scale//2 + 2: (self.M*self.scale)//2 + self.scale//2
        ] = (255,255,255)

        self.grid[
            self.N*self.scale : self.N*self.scale+2,
            (self.M*self.scale)//2 - self.scale//2 + 2 : (self.M*self.scale)//2 + self.scale//2
        ] = (255,255,255)

        return self.grid

    def print_solution_stats(self):
        print("Solutions stats:")
        print("Nr tiles:", len(self.solution))

        nr_bad_roads = 0
        for tile in self.solution:
            nr_bad_roads += max(len(tile.children) - 1, 0)

        nr_bad_roads += len(tile.children)

        print("Nr bad roads:", nr_bad_roads)

if __name__ == "__main__":
    maze = Maze(11, 11, scale=10)
    maze.print_solution_stats()

    grid = maze.get_maze_image(solution_colored=True)
    plt.imshow(grid)
    plt.show()
