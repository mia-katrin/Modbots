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
        public int angle = new int[4] { 0, 90, 180, 270 } [Random.Range(0, 4)];
        public float scale = new float[2] { 1.0f, Random.Range(0.1f, 1.0f)} [Random.Range(0, 1)]; // Should be 2
        public int index;
    }

    public GameObject modulePrefab;
    public GameObject rootGO;
    public List<GameObject> allModules;
    public List<int> destroyedIndexes;
    private Node geneRoot;

    public static int staticIndex = 0;
    public int myIndex = 0;

    public float torque = 0.0f;

    private void Start()
    {
        myIndex = staticIndex;
        //Debug.Log($"I'm MR {myIndex}");
        staticIndex += 1;
        if (instance != null && instance != this)
        {
            if (GameManager.Instance != null)
            {
                //GameManager.Instance.pythonCom.SendMessage($"I am MR {myIndex}, being destroyed");
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

        float[] sensorValues = Enumerable.Repeat(0.0f, 150).ToArray();

        if (allModules.Count > 0)
        {
            foreach (var moduleGO in allModules)
            {
                ModuleParameterized m = moduleGO.GetComponent<ModuleParameterized>();
                float[] data = m.CollectSensorData();
                sensorValues[m.index * 3] = data[0];
                sensorValues[m.index * 3 + 1] = data[1];
                sensorValues[m.index * 3 + 2] = data[2];
            }
        }
        sensor.AddObservation(sensorValues);

        RequestDecision();
    }

    public override void OnActionReceived(float[] vectorAction)
    {
        //weirdSine += 0.01f;

        if (rootGO != null)
        {
            if (torque == 1.0f)
            {
                Debug.LogError("Using velocity");
                foreach (var module in allModules)
                {
                    ConfigurableJoint joint = module.transform.GetChild(0).GetComponent<ConfigurableJoint>();
                    Vector3 tr = joint.targetAngularVelocity;
                    
                    tr.x = vectorAction[
                        module.GetComponent<ModuleParameterized>().index
                    ];
                    //tr.x = Mathf.Sin(weirdSine);
                    joint.targetAngularVelocity = tr;
                }
            }
            else
            {
                Debug.LogError("Using target rotation");
                foreach (var module in allModules)
                {
                    ConfigurableJoint joint = module.transform.GetChild(0).GetComponent<ConfigurableJoint>();
                    Quaternion tr = joint.targetRotation;
                    tr.x = vectorAction[
                        module.GetComponent<ModuleParameterized>().index
                    ];
                    //tr.x = Mathf.Sin(weirdSine);
                    joint.targetRotation = tr;
                }
            }
        }
    }

    public override void Heuristic(float[] actionsOut)
    {

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

        geneRoot = null;

        destroyedIndexes.Clear();
    }

    public void MakeRobot(string gene)
    {
        var envParameters = Academy.Instance.EnvironmentParameters;
        torque = envParameters.GetWithDefault("torque", 0.0f);
        //GameManager.Instance.pythonCom.SendMessage("Modular Robot about to make robot");
        //Debug.Log($"Gene got {gene}");
        geneRoot = new Node();

        if (gene == "Random")
        {
            GenerateRandomNodes(geneRoot, depth:3);
        }
        else
        {
            string[] rootInfo = gene.Substring(0, gene.IndexOf('|')).Split(',');
            geneRoot.scale = float.Parse(rootInfo[0]);
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
                //Debug.Log("ChildGO was null");
                continue;
            }
            //if (HasCollided(toProcessGO))
            //{
            //    Destroy(toProcessGO);
            //    continue;
            //}
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

    public void PruneCollisions()
    {
        // allModules was constructed breadth first, meaning the last nodes are the bottom layer
        // indexes are like this:
        //     0
        //    /|\
        //   1 2 3

        if (allModules.Count == 0) return;
        var module = allModules[allModules.Count - 1];
        int i = allModules.Count - 1;
        while (module != null)
        {
            if (HasCollided(module))
            {
                destroyedIndexes.Add(module.GetComponent<ModuleParameterized>().index);
                allModules.Remove(module);
                DestroyConnectedChildren(module);
                Destroy(module);
            }

            i--;
            if (i > 0)
                module = allModules[i];
            else
                module = null;
        }
    }

    private void DestroyConnectedChildren(GameObject module)
    {
        foreach (var child in FindMyChildren(module))
        {
            destroyedIndexes.Add(child.GetComponent<ModuleParameterized>().index);
            DestroyConnectedChildren(child);
            allModules.Remove(child);
            Destroy(child);
        }
    }

    private List<GameObject> FindMyChildren(GameObject module)
    {
        List<GameObject> children = new List<GameObject>();

        // Get gene node to module
        Node moduleNode = GetNode(module);

        // Find node's gene children
        foreach (Node node in moduleNode.children)
        {
            if (node != null)
            {
                foreach (var mod in allModules)
                {
                    if (mod.GetComponent<ModuleParameterized>().index == node.index)
                    {
                        children.Add(mod);
                    }
                }
            }
        }

        return children;
    }

    private Node GetNode(GameObject module)
    {
        Queue<Node> queue = new Queue<Node>();
        queue.Enqueue(geneRoot);

        while (queue.Count > 0)
        {
            Node node = queue.Dequeue();

            if (node.index == module.GetComponent<ModuleParameterized>().index)
            {
                return node;
            }
            foreach (var child in node.children)
            {
                if (child != null)
                {
                    queue.Enqueue(child);
                }
            }
        }
        return null;
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
                    //Debug.Log("ChildGO was null");
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

    private GameObject GetModuleGameObject(Transform child)
    {
        ModuleParameterized moduleParameterized = child.GetComponent<ModuleParameterized>();
        while (moduleParameterized == null)
        {
            child = child.parent;
            moduleParameterized = child.GetComponent<ModuleParameterized>();
        }
        return moduleParameterized.gameObject;
    }

    private int GetIndex(Transform child)
    {
        ModuleParameterized moduleParameterized = child.GetComponent<ModuleParameterized>();
        while (moduleParameterized == null)
        {
            Transform saved = child;
            child = child.parent;
            if (child == null) Debug.LogError(saved);
            moduleParameterized = child.GetComponent<ModuleParameterized>();
        }
        return moduleParameterized.index;
    }

    private bool HasCollided(GameObject module)
    {
        // check for collision
        // Check for number of child bodies. I assume all children are colliders. None should collide when created.

        List<Transform> colliderChildren;
        if (module.GetComponent<ModuleParameterized>().connectionSites.Count > 1)
        {
            colliderChildren = new List<Transform>
            {
                module.transform.GetChild(0).GetChild(3), // ConnectionSite
                module.transform.GetChild(0).GetChild(4), // ConnectionSite (1)
                module.transform.GetChild(0).GetChild(5), // ConnectionSite (2)
                module.transform.GetChild(1).GetChild(0).GetChild(0) // Cube
            };
        }
        else
        {
            colliderChildren = new List<Transform>
            {
                module.transform.GetChild(0).GetChild(1), // ConnectionSite
                module.transform.GetChild(1).GetChild(0).GetChild(0) // Cube
            };
        }

        foreach (var child in colliderChildren)
        {
            var collider = child.GetComponent<BoxCollider>();
            if (collider)
            {
                // The initial layer mask of a spawned module. Should be ignored first.
                var layerMask = 1 << 8; //LayerMask.GetMask("PreExisting");
                layerMask = ~layerMask;

                bool didWeCollide = false;
                if (EnvironmentBuilder.Instance.CollisionCheck(collider))
                {
                    didWeCollide = true;
                }
                else if (Physics.CheckBox(collider.transform.position, collider.bounds.extents))
                {
                    Collider[] collidingBoxes = Physics.OverlapBox(collider.transform.position, collider.bounds.extents);

                    foreach (var offenseCollider in collidingBoxes)
                    {
                        Debug.Log($"Collider {offenseCollider} is up for review against {child}. " +
                            $"Offense: {offenseCollider.transform.position} {offenseCollider.bounds.extents}, " +
                            $"Child: {collider.transform.position} {collider.bounds.extents}");
                        if (GetIndex(offenseCollider.transform) != GetIndex(child) && ! destroyedIndexes.Contains(GetIndex(offenseCollider.transform)))
                        {
                            Debug.Log($"My ({GetIndex(child)}) {child} has collided with someones's ({GetIndex(offenseCollider.transform)}) {offenseCollider.gameObject} {offenseCollider.bounds.size} {collider.bounds.size} {offenseCollider.transform.position} {child.transform.position}");
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
    
    /*private void OnDrawGizmos()
    {
        Gizmos.color = Color.green;
        foreach (var module in allModules)
        {
            List<Transform> colliderChildren;
            if (module.GetComponent<ModuleParameterized>().connectionSites.Count > 1)
            {
                colliderChildren = new List<Transform>
                {
                    module.transform.GetChild(0).GetChild(3), // ConnectionSite
                    module.transform.GetChild(0).GetChild(4), // ConnectionSite (1)
                    module.transform.GetChild(0).GetChild(5), // ConnectionSite (2)
                    module.transform.GetChild(1).GetChild(0).GetChild(0) // Cube
                };
            }
            else
            {
                colliderChildren = new List<Transform>
                {
                    module.transform.GetChild(0).GetChild(1), // ConnectionSite
                    module.transform.GetChild(1).GetChild(0).GetChild(0) // Cube
                };
            }

            foreach (var child in colliderChildren)
            {
                BoxCollider collider = child.GetComponent<BoxCollider>();

                Gizmos.DrawWireCube(collider.transform.position, collider.bounds.size);
                Debug.Log(collider.bounds.size);
            }
        }
    }*/

    private GameObject ConnectModuleTo(GameObject parentGO, int site, int angle, float scale)
    {
        // Get connection site transform of parent
        ModuleParameterized parentModule = parentGO.GetComponent<ModuleParameterized>();
        Transform connectionTransform = parentModule.GetConnectionSite(site);
        if (connectionTransform == null)
        {
            //Debug.Log($"Could not attach to parent module because it does not support connection site {site}");
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
}
