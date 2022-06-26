using UnityEngine;
using Unity.MLAgents;
using System;
using System.Collections.Generic;

public class EnvironmentBuilder : MonoBehaviour
{
    // singleton
    private static EnvironmentBuilder instance;
    public static EnvironmentBuilder Instance { get { return instance; } }

    public GameObject floor;
    public GameObject bumpyGround;
    public GameObject stairs;
    public Maze maze;
    public Maze corridor;

    public void Awake()
    {
        if (instance != null && instance != this)
        {
            this.gameObject.SetActive(false);
            Destroy(this.gameObject);
            return;
        }
        else if (instance == null)
        {
            instance = this;
        }
        DontDestroyOnLoad(gameObject);
    }

    public List<GameObject> testColliders;
    public void BuildEnvironment()
    {

        var envParameters = Academy.Instance.EnvironmentParameters;
        float envEnum = envParameters.GetWithDefault("envEnum", 0.0f);
        int seed = (int)envParameters.GetWithDefault("seed", 42.0f);

        // The environment is always gone at the start, so instantiate and
        // activate what needs to be there

        switch (envEnum)
        {
            case (0.0f):
                Instantiate(floor);
                break;
            case (1.0f):
                Instantiate(floor);
                corridor = new Maze(5, 5, corridor: true, seed: seed);
                corridor.Draw();
                break;
            case (2.0f):
                Instantiate(floor);
                maze = new Maze(5, 5, seed: seed);
                maze.Draw();
                testColliders = maze.wallColliders;
                break;
            case (3.0f):
                Instantiate(floor);
                Instantiate(stairs);
                break;
            default:
                break;
        }
    }

    public bool FloorCollision(BoxCollider boxCollider)
    {
        // Find lowest point of collider
        float yDim = boxCollider.bounds.size.y;
        float yPos = boxCollider.transform.position.y;

        // Find if lowest point is lower than floor
        return yPos - yDim <= -3.0f;
    }

    public bool CollisionCheck(BoxCollider boxCollider)
    {
        var envParameters = Academy.Instance.EnvironmentParameters;
        float envEnum = envParameters.GetWithDefault("envEnum", 0.0f);

        switch (envEnum)
        {
            case (0.0f): // Floor
                return FloorCollision(boxCollider);
            case (1.0f): // Corridor
                return FloorCollision(boxCollider) || corridor.CollisionCheck(boxCollider);
            case (2.0f): // Maze
                return FloorCollision(boxCollider) || maze.CollisionCheck(boxCollider);
            case (3.0f): // Stairs
                return FloorCollision(boxCollider);
            default:
                break;
        }
        return false;
    }

    internal float GetMazeFitness(Vector3 pos)
    {
        throw new NotImplementedException();
    }

    public float GetCorridorFitness(Vector3 pos)
    {
        if (corridor == null) return 0.0f;
        float fitness = corridor.GetFitness(pos);
        Debug.Log($"Fitness {fitness}");
        return fitness;
    }

    private void Start()
    {
        
    }

    private void Update()
    {
        
    }
}
