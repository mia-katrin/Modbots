using System.Collections.Generic;
using UnityEngine;

public class Maze
{
    private class Tile
    {
        public int[] coor;
        public List<Tile> children;

        public Tile(int[] c)
        {
            coor = c;
            children = new List<Tile>();
        }
    }

    private Tile root;
    private Tile end;
    public List<GameObject> wallColliders;

    [Range(3, 41)]
    private int N;
    [Range(3, 41)]
    private int M;

    // forward, up, left
    public float[] tileSize = new float[3] { 4, 4, 4 };
    public float wallWidth = 0.2f;
    public float floorPos = -3f;
    [Range(-1f,0f)]
    public float beginOffset = -0.5f;

    public Maze(int height, int width, bool corridor=false, int seed=-1)
    {
        // Take seed
        if (seed != -1)
            Random.seed = seed;

        N = height;
        M = width;

        List<Tile> setOfTiles = new List<Tile>();

        for (int x = 0; x < N; x++)
        {
            for (int y = 0; y < M; y++)
            {
                setOfTiles.Add(new Tile(new int[2] { x, y }));
            }
        }

        root = setOfTiles[M / 2];
        end = setOfTiles[(N - 1) * M + M / 2];

        ConnectRecursive(root, setOfTiles);

        if (corridor) ShaveSolution(root);
    }

    private bool ShaveSolution(Tile tile)
    {
        if (tile == end)
        {
            tile.children.Clear();
            return true;
        }

        foreach (var child in tile.children)
        {
            if (ShaveSolution(child))
            {
                tile.children.Clear();
                tile.children.Add(child);
                return true;
            }
        }
        return false;
    }

    private void ConnectRecursive(Tile tile, List<Tile> setOfTiles)
    {
        setOfTiles.Remove(tile);

        while (FindNeighbors(tile, setOfTiles).Count != 0)
        {
            List<Tile> neighbors = FindNeighbors(tile, setOfTiles);

            Tile child = neighbors[Random.Range(0, neighbors.Count)];
            tile.children.Add(child);
            ConnectRecursive(child, setOfTiles);
        }
    }

    private List<Tile> FindNeighbors(Tile start, List<Tile> setOfTiles)
    {
        List<Tile> neighbors = new List<Tile>();

        foreach (var tile in setOfTiles)
        {
            int diff = Mathf.Abs(tile.coor[0] - start.coor[0]) + Mathf.Abs(tile.coor[1] - start.coor[1]);
            if (diff == 1)
            {
                neighbors.Add(tile);
            }
        }

        return neighbors;
    }

    public void Draw()
    {
        wallColliders = new List<GameObject>();
        DrawRecursive(root, 0);
    }

    private void DrawRecursive(Tile tile, int cameFrom)
    {
        //    1
        //    __
        // 4 |__| 3
        //    2
        //
        //  x|__z

        List<int> childPositions = new List<int>();

        foreach (var child in tile.children)
        {
            if (tile.coor[0] - child.coor[0] == -1)
            {
                childPositions.Add(1);
                DrawRecursive(child, 2);
            } else if (tile.coor[0] - child.coor[0] == 1)
            {
                childPositions.Add(2);
                DrawRecursive(child, 1);
            } else if (tile.coor[1] - child.coor[1] == -1)
            {
                childPositions.Add(3);
                DrawRecursive(child, 4);
            }
            else if (tile.coor[1] - child.coor[1] == 1)
            {
                childPositions.Add(4);
                DrawRecursive(child, 3);
            }
        }

        if (cameFrom != 1 && !childPositions.Contains(1) && tile != end) MakeWall(tile, wallWidth, tileSize[2], tileSize[0]/2, 0f); 

        if (cameFrom != 2 && !childPositions.Contains(2)) MakeWall(tile, wallWidth, tileSize[2], -tileSize[0] / 2, 0f); 

        if (cameFrom != 3 && !childPositions.Contains(3)) MakeWall(tile, tileSize[0], wallWidth, 0f, tileSize[2] / 2); 

        if (cameFrom != 4 && !childPositions.Contains(4)) MakeWall(tile, tileSize[0], wallWidth, 0f, -tileSize[2] / 2);
    }

    private int wallNr = 0;
    private GameObject MakeWall(Tile tile, float xScale, float zScale, float xOffset, float zOffset)
    {
        GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cube.transform.localScale = new Vector3(xScale, tileSize[1], zScale);
        cube.transform.position = new Vector3(tile.coor[0]*tileSize[0] + xOffset, floorPos + tileSize[1] / 2, tile.coor[1] * tileSize[2] + zOffset + beginOffset*M*tileSize[2] + tileSize[2]/2);
        cube.name = $"Wall {wallNr}";
        wallNr++;

        // Store the colliders next to the spawn point
        // x | r | x
        // x | x | x
        if (Mathf.Abs(tile.coor[0] - root.coor[0]) <= 2 && Mathf.Abs(tile.coor[1] - root.coor[1]) <= 2)
        {
            wallColliders.Add(cube);
        }

        return cube;
    }

    public bool CollisionCheck(BoxCollider boxCollider)
    {
        if (Physics.CheckBox(boxCollider.transform.position, boxCollider.bounds.extents))
        {
            Collider[] collidingBoxes = Physics.OverlapBox(boxCollider.transform.position, boxCollider.bounds.extents);

            foreach (var offenseCollider in collidingBoxes)
            {
                if (wallColliders.Contains(offenseCollider.gameObject)) return true;
            }
        }
        return false;
    }
}
