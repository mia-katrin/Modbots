using System.Collections;
using System.Collections.Generic;
using System.IO;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using System.Linq;

public class ModularRobot : Agent
{
    // singleton
    private static ModularRobot instance;
    public static ModularRobot Instance { get { return instance; } }

    // lil data structure
    private class Node
    {
        public Node[] children = new Node[3] { null, null, null };
        public int angle = new int[4] { 0, 90, 180, 270 } [Random.Range(0, 3)];
        public float scale = Random.Range(0.1f, 3);
        public int index;
    }

    public GameObject modulePrefab;
    public GameObject rootGO;
    public List<GameObject> allModules;

    public static int staticIndex = 0;
    public int myIndex = 0;

    private void Start()
    {
        myIndex = staticIndex;
        //Debug.Log($"I'm MR {myIndex}");
        staticIndex += 1;
        if (instance != null && instance != this)
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.pythonCom.SendMessage($"I am MR {myIndex}, being destroyed");
            }
            this.gameObject.SetActive(false);
            Destroy(this.gameObject);
            return;
        }
        else if (instance == null)
        {
            instance = this;
        }
        DontDestroyOnLoad(gameObject);

        base.MaxStep = 10000;
    }

    public Vector3 GetPosition()
    {
        if (rootGO != null)
        {
            return rootGO.transform.GetChild(0).transform.position;
        }
        return Vector3.zero;
    }

    // mlagents functions
    public override void CollectObservations(VectorSensor sensor)
    {
        Vector3 pos = GetPosition();
        sensor.AddObservation(pos);
        RequestDecision();
    }

    private void FixedUpdate()
    {
        
    }

    public void DestroyContents()
    {
        for (int i = 0; i < allModules.Count; i++)
        {
            Destroy(allModules[i]);
        }
        allModules.Clear();
        Destroy(rootGO);
    }

    public void MakeRobot(string gene)
    {
        //GameManager.Instance.pythonCom.SendMessage("Modular Robot about to make robot");
        //Debug.Log($"Gene got {gene}");
        Node geneRoot = new Node();

        if (gene == "Random")
        {
            GenerateRandomNodes(geneRoot, depth:3);
        }
        else
        {
            string[] rootControl = gene.Substring(0, gene.IndexOf('|')).Split(',');
            geneRoot.scale = float.Parse(rootControl[0]);
            InterpretStringGene(gene, new Stack<Node>(), geneRoot);
            //GameManager.Instance.pythonCom.SendMessage("Modular Robot string interpreted");
        }

        SetIndex(geneRoot, 0);

        // Done reading the info given, now we must create the corresponding GameObject

        rootGO = Instantiate(modulePrefab);
        ModuleParameterized rootModule = rootGO.GetComponent<ModuleParameterized>();
        rootModule.SetIndex(geneRoot.index);
        DontDestroyOnLoad(rootGO);

        rootModule.SetSize(geneRoot.scale);
        rootModule.RemoveFixedJoint();

        BreadthFirstConstruct(geneRoot, rootGO);
        //GameManager.Instance.pythonCom.SendMessage("Modular robot made");
    }

    private void BreadthFirstConstruct(Node rootNode, GameObject rootGO)
    {
        allModules.Add(rootGO);

        Queue<Node> queue = new Queue<Node>();
        Queue<GameObject> parentQueue = new Queue<GameObject>();
        Queue<int> siteQueue = new Queue<int>();
        for (int i = 0; i < rootNode.children.Length; i++)
        {
            if (rootNode.children[i] != null)
            {
                queue.Enqueue(rootNode.children[i]);
                parentQueue.Enqueue(rootGO);
                siteQueue.Enqueue(i);
            }
        }

        while (queue.Count > 0)
        {
            Node toProcess = queue.Dequeue();
            GameObject parentGO = parentQueue.Dequeue();
            int site = siteQueue.Dequeue();

            GameObject toProcessGO = ConnectModuleTo(parentGO, site: site, toProcess.angle, toProcess.scale);
            if (toProcessGO == null)
            {
                Debug.Log("ChildGO was null");
                continue;
            }
            if (HasCollided(toProcessGO))
            {
                Destroy(toProcessGO);
                continue;
            }
            toProcessGO.GetComponent<ModuleParameterized>().SetIndex(toProcess.index);

            for (int i = 0; i < toProcess.children.Length; i++)
            {
                if (toProcess.children[i] != null)
                {
                    queue.Enqueue(toProcess.children[i]);
                    parentQueue.Enqueue(toProcessGO);
                    siteQueue.Enqueue(i);
                }
            }

            allModules.Add(toProcessGO);
        }
    }

    private void IterativeConstruct(Node geneNode, GameObject parentGO)
    {
        if (HasCollided(parentGO))
        {
            Destroy(parentGO);
            return;
        }

        allModules.Add(parentGO);

        for (int i = 0; i < geneNode.children.Length; i++)
        {
            if (geneNode.children[i] != null)
            {
                GameObject childGO = ConnectModuleTo(parentGO, site: i, geneNode.children[i].angle, geneNode.children[i].scale);
                if (childGO == null)
                {
                    Debug.Log("ChildGO was null");
                    return;
                }
                childGO.GetComponent<ModuleParameterized>().SetIndex(geneNode.children[i].index);

                IterativeConstruct(geneNode.children[i], childGO);
            }
        }
    }

    private int SetIndex(Node node, int index)
    {
        node.index = index;

        for (int i = 0; i < node.children.Length; i++)
        {
            if (node.children[i] != null)
            {
                index = SetIndex(node.children[i], index + 1);
            }
        }
        return index;
    }

    private void GenerateRandomNodes(Node node, int depth)
    {
        if (depth <= 0) return;

        for (int i = 0; i < node.children.Length; i++)
        {
            if (Random.Range(0.0f, 1.0f) < (depth / 4.0f))
            {
                node.children[i] = new Node();
                GenerateRandomNodes(node.children[i], depth - 1);
            }
        }
    }

    // Recursive
    // TODO: Change to json
    private void InterpretStringGene(string gene, Stack<Node> stack, Node parent)
    {
        int dividerPos = gene.IndexOf('|');
        Node child = parent;
        switch (gene[0])
        {
            case 'M':
                string[] nodeInfo = gene.Substring(1, dividerPos - 1).Split(',');
                child = new Node();
                parent.children[int.Parse(nodeInfo[0])] = child;
                child.angle = int.Parse(nodeInfo[1]);
                child.scale = float.Parse(nodeInfo[2]);
                break;
            case '[':
                stack.Push(parent);
                break;
            case ']':
                child = stack.Pop();
                break;
            default:
                break;
        }
        if (dividerPos + 1 < gene.Length)
        {
            InterpretStringGene(gene.Substring(dividerPos + 1, gene.Length - (dividerPos + 1)), stack, child);
        }
    }

    private bool HasCollided(GameObject module)
    {

        // check for collision
        // Check for number of child bodies. I assume all children are colliders. None should collide when created.

        List<Transform> colliderChildren = new List<Transform>
        {
            module.transform.GetChild(0).GetChild(3), // ConnectionSite
            module.transform.GetChild(0).GetChild(4), // ConnectionSite (1)
            module.transform.GetChild(0).GetChild(5), // ConnectionSite (2)
            module.transform.GetChild(1).GetChild(0).GetChild(0)//, // Cube
            //module.transform.GetChild(1).GetChild(1) // parent connection site
            // parent site is not checked for because it overlaps with parent
            // collider1 and cube no matter what, although I don't get why for the latter
        };

        foreach (var child in colliderChildren)
        {
            var collider = child.GetComponent<BoxCollider>();
            if (collider)
            {
                // The initial layer mask of a spawned module. Should be ignored first.
                var layerMask = 1 << 8; //LayerMask.GetMask("PreExisting");
                layerMask = ~layerMask;

                bool didWeCollide = false;
                if (collider.transform.position.y < -3.0f)
                {
                    didWeCollide = true;
                }
                else if (Physics.CheckBox(collider.transform.position, collider.bounds.extents, collider.transform.rotation, layerMask))
                {
                    Collider[] collidingBoxes = Physics.OverlapBox(collider.transform.position, collider.bounds.extents, collider.transform.rotation, layerMask);

                    foreach (var offenseCollider in collidingBoxes)
                    {
                        if (!colliderChildren.Contains(offenseCollider.gameObject.transform) && offenseCollider.gameObject.name != "ParentConnectionSite" && offenseCollider.gameObject.name != "Collider2")
                        {
                            Debug.Log($"{child} has collided with {offenseCollider.gameObject}");
                            //GameManager.Instance.pythonCom.SendMessage($"{child} has collided with {offenseCollider.gameObject}");
                            didWeCollide = true;
                        }
                    }
                }
                if (didWeCollide)
                {
                    return true;
                }
                collider.gameObject.layer = 6;
            }
        }

        return false;
    }

    private GameObject ConnectModuleTo(GameObject parentGO, int site, int angle, float scale)
    {
        // Get connection site transform of parent
        ModuleParameterized parentModule = parentGO.GetComponent<ModuleParameterized>();
        Transform connectionTransform = parentModule.GetConnectionSite(site);
        if (connectionTransform == null)
        {
            Debug.Log($"Could not attach to parent module because it does not support connection site {site}");
            return null; 
        }

        // Instantiate at site position, rotation, and with overseer agent transform as parent transform. Should parent be connection site transform instead? or parent module?
        GameObject childGO = Instantiate(modulePrefab, connectionTransform.position, connectionTransform.rotation, transform);

        // Rotate the new module by the angle parameter
        var newRobotComponentLocalEulerAngles = childGO.transform.localRotation.eulerAngles;
        newRobotComponentLocalEulerAngles.y += angle;
        childGO.transform.Rotate(Vector3.up, angle, Space.Self);

        // Set scale
        ModuleParameterized childModule = childGO.GetComponent<ModuleParameterized>();
        childModule.SetSize(scale);

        // Connect child's fixed joint to parent module's top collider's rigid body
        childModule.attachmentJoint.connectedBody = parentGO.transform.GetChild(0).gameObject.GetComponent<Rigidbody>();

        return childGO;
    }

    public override void OnActionReceived(float[] vectorAction)
    {
        if (rootGO != null)
        {
            foreach (var module in allModules)
            {
                ConfigurableJoint joint = module.transform.GetChild(0).GetComponent<ConfigurableJoint>();
                Quaternion tr = joint.targetRotation;
                tr.x = vectorAction[
                    module.GetComponent<ModuleParameterized>().index
                ];
                joint.targetRotation = tr;
            }
        }
    }

    public override void Heuristic(float[] actionsOut)
    {
        
    }
}
