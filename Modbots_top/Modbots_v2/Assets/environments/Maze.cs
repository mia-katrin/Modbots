using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class Maze
{
    private class Tile
    {
        public int[] coor;
        public List<Tile> children;
        public Tile parent;

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
            Random.InitState(seed);

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
        root.parent = null;
        end = setOfTiles[(N - 1) * M + M / 2];

        ConnectRecursive(root, setOfTiles);

        if (corridor) ShaveSolution(root);

        //MakeImg();
    }

    private void MakeImg()
    {
        Debug.Log("Beginning to make img");
        int res = 20;
        Texture2D texture = new Texture2D(N*res, M*res);

        for (int i = 0; i < N*res; i++)
        {
            for (int j = 0; j < M*res; j++)
            {
                texture.SetPixel(i, j, Color.black);
            }
        }
        Debug.Log("Colored black");

        Queue<Tile> queue = new Queue<Tile>();
        queue.Enqueue(root);

        while (queue.Count > 0)
        {
            Tile tile = queue.Dequeue();
            Vector3 pos = GetMidPos(tile);

            for (int i = 0; i < res; i++)
            {
                for (int j = 0; j < res; j++)
                {
                    float x = pos.x + (i - res/2f) / res * tileSize[0];
                    float z = pos.z + (j - res / 2f) / res * tileSize[2];

                    float fitness = GetFitness(new Vector3(x,0,z));

                    if (fitness == -1) Debug.LogError("Fitness fault");
                    while (fitness > 6) fitness -= 6;
                    texture.SetPixel(
                        tile.coor[0] * res + i,
                        tile.coor[1] * res + j,
                        Color.HSVToRGB(fitness / 6, 1f, 1f)
                    );
                }
            }

            foreach (var child in tile.children)
            {
                queue.Enqueue(child);
            }
        }

        // Save picture
        texture.Apply();
        byte[] bytes = texture.EncodeToPNG();
        File.WriteAllBytes($"/Users/mia-katrinkvalsund/Desktop/picture.png", bytes);
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
            child.parent = tile;
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
        // | x | x | r | x | x | 
        // | x | x | x | x | x | 
        // | x | x | x | x | x | 
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

    private Vector3 GetMidPos(Tile tile)
    {
        // Tile coordinate scaled by tilesize
        float xPos = tile.coor[0] * tileSize[0];

        // Important to note that this will hover above ground
        float yPos = floorPos + tileSize[1] / 2;

        // Tile coordinate scaled by tilesize
        float zPos = tile.coor[1] * tileSize[2];
        // Z position is offset in order to start in the middle of the row
        zPos = zPos + beginOffset * M * tileSize[2] + tileSize[2] / 2;

        return new Vector3(xPos, yPos, zPos);
    }

    private int GetCountOf(Tile tile)
    {
        int count = 1;
        while (tile.parent != null)
        {
            count++;
            tile = tile.parent;
        }

        return count;
    }

    public float GetFitness(Vector3 pos)
    {
        Tile tile = GetTile(pos);
        // Out of bounds
        if (tile == null) return -1;

        int tileNr = GetCountOf(tile);

        // Fitness is AT LEAST tileNr-1
        // Now to figure out how much more (float yknow)

        // find parent and child pos to interpolate between
        Vector3 childPos;
        Vector3 parPos;
        // At root we have no parent
        if (tile.parent == null)
        {
            parPos = GetMidPos(tile) - new Vector3(tileSize[0] / 2, 0, 0);
        }
        else
        {
            parPos = GetMidPos(tile.parent);
        }
        // At end we have no child
        if (tile.children.Count == 0)
        {
            childPos = GetMidPos(tile) + new Vector3(tileSize[0] / 2, 0, 0);
        }
        else
        {
            childPos = GetMidPos(tile.children[0]);
        }

        // Make sure we only interpolate in the xz plane
        parPos.y = 0;
        childPos.y = 0;
        pos.y = 0;

        // Find distances to interpolation points
        float distPar = (parPos - pos).magnitude;
        float distChi = (childPos - pos).magnitude;

        return tileNr-1 + 2*(distPar / (distPar + distChi));

        // Normalize against path end
    }

    private Tile GetTile(Vector3 pos)
    {
        Queue<Tile> queue = new Queue<Tile>();
        queue.Enqueue(root);

        Vector3 tileSizeVec3 = new Vector3(tileSize[0], tileSize[1], tileSize[2]);

        while (queue.Count > 0)
        {
            Tile tile = queue.Dequeue();
            Vector3 midPos = GetMidPos(tile);

            if (PosInCube(pos, midPos, tileSizeVec3/2f))
            {
                return tile;
            }
            else
            {
                foreach (var child in tile.children)
                {
                    queue.Enqueue(child);
                }
            }
        }

        return null;
    }

    private bool PosInCube(Vector3 pos, Vector3 midPos, Vector3 halfScale)
    {
        bool inX = pos.x >= midPos.x - halfScale.x && pos.x <= midPos.x + halfScale.x;
        bool inZ = pos.z >= midPos.z - halfScale.z && pos.z <= midPos.z + halfScale.z;

        return inX && inZ;
    }
}
