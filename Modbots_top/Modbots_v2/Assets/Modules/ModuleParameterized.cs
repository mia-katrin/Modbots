using System.Collections.Generic;
using Unity.MLAgents;
using UnityEngine;

public class ModuleParameterized : MonoBehaviour
{
    [Tooltip("Drag all gameobjects whose transform represents the connection sites to child modules")]
    [SerializeField] public List<GameObject> connectionSites;
    [Tooltip("Drag a gameobject whose transform represents the connection site to the parent")]
    [SerializeField] public GameObject parentConnectionSite;
    [Tooltip("Drag all gameobjects that contain joints that will be adjusted here")]
    [SerializeField] public List<ConfigurableJoint> joints;
    [Tooltip("This is the joint that should be connected to the parent object")]
    [SerializeField] public ConfigurableJoint attachmentJoint;

    private float originalFemaleDisplacement;
    public int index = -1;
    public float scale = 1f;

    public void SetIndex(int i)
    {
        index = i;
        ColorBasedOnIndex(i);
    }

    public void ColorBasedOnIndex(int i)
    {
        float max = 14;
        Color color = Color.Lerp(Color.magenta, Color.yellow, i / max);

        for (int j = 0; j < transform.GetChild(0).childCount; j++)
        {
            if (transform.GetChild(0).GetChild(j).name.StartsWith("ConnectionSite"))
            {
                transform.GetChild(0).GetChild(j).gameObject.GetComponent<Renderer>().material.color = color;
            }
        }
        transform.GetChild(1).GetChild(1).gameObject.GetComponent<Renderer>().material.color = color;
    }

    public void SetColor(bool torque, float controlValue)
    {
        Color color;
        if (torque == true)
        {
            color = Color.Lerp(Color.blue, Color.red, (3f + controlValue) / 6f);
        }
        else
        {
            color = Color.Lerp(Color.green, Color.magenta, (1f + controlValue) / 2f);
        }

        for (int j = 0; j < transform.GetChild(0).childCount; j++)
        {
            if (transform.GetChild(0).GetChild(j).name.StartsWith("ConnectionSite"))
            {
                transform.GetChild(0).GetChild(j).gameObject.GetComponent<Renderer>().material.color = color;
            }
        }
    }

    private void Awake()
    {
        GameObject collider1 = transform.GetChild(0).gameObject;
        originalFemaleDisplacement = collider1.transform.localPosition.y;
    }

    // MUST BE CALLED!
    public void SetSize(float xSize)
    {
        scale = xSize;
        // Get both colliders
        GameObject collider1 = transform.GetChild(0).gameObject;
        GameObject collider2 = transform.GetChild(1).gameObject;

        if (xSize < 1.0f)
        {
            connectionSites.Remove(collider1.transform.GetChild(0).gameObject);
            connectionSites.Remove(collider1.transform.GetChild(1).gameObject);

            connectionSites.TrimExcess();
            //Debug.Log(connectionSites.Count);

            // Save children
            var childrenToKeep = new List<Transform>();
            var childrenToDelete = new List<Transform>();
            for (int i = 0; i < collider1.transform.childCount; i++)
            {
                if (i == 2 || i == 3)
                {
                    childrenToKeep.Add(collider1.transform.GetChild(i));
                }
                else
                {
                    childrenToDelete.Add(collider1.transform.GetChild(i));
                }
            }

            collider1.transform.DetachChildren();

            foreach (var child in childrenToDelete)
            {
                Destroy(child.gameObject);
            }

            // Reattach children
            foreach (var child in childrenToKeep)
            {
                child.SetParent(collider1.transform);
            }

            childrenToDelete.Clear();
            childrenToKeep.Clear();
        }

        // Save local positions
        Vector3 desiredCol1Trans = originalFemaleDisplacement * (xSize - 1) * Vector3.up;

        // Unparent them
        transform.DetachChildren();

        // delete all rigidbody and configurablejoint first
        // Pre-done

        // Move the bits
        collider1.transform.Translate(desiredCol1Trans);
        Transform cubeHolder = collider2.transform.GetChild(0);
        cubeHolder.localScale += Vector3.up * (xSize - 1);

        // Add rigidbodies and joints, configure them correctly
        // Here

        // Reparent
        collider1.transform.SetParent(transform, worldPositionStays: true);
        collider2.transform.SetParent(transform, worldPositionStays: true);

        // Or here
        AddJoints(collider1, collider2, xSize);

        // Configutr stuff
        joints.Add(collider1.GetComponent<ConfigurableJoint>());
        attachmentJoint = collider2.GetComponent<ConfigurableJoint>();
    }

    private void AddJoints(GameObject collider1, GameObject collider2, float scale)
    {
        collider1.AddComponent<Rigidbody>();
        collider2.AddComponent<Rigidbody>();
        collider1.AddComponent<ConfigurableJoint>();
        collider2.AddComponent<ConfigurableJoint>();

        // Configure rigidbodies
        Rigidbody rb = collider1.GetComponent<Rigidbody>();
        rb.angularDrag = 0;
        rb.mass = 5;

        Rigidbody rb2 = collider2.GetComponent<Rigidbody>();
        rb2.angularDrag = 0.05f;
        rb2.mass = 1 + scale*4; // 25 * (0.1f + scale / (scale + 2)); // Non-linear scaling using sigmoid

        // Configure joint collider 1
        ConfigurableJoint cj = collider1.GetComponent<ConfigurableJoint>();
        cj.connectedBody = collider2.GetComponent<Rigidbody>();
        cj.anchor = new Vector3(0, 0, 0);

        cj.xMotion = ConfigurableJointMotion.Locked;
        cj.yMotion = ConfigurableJointMotion.Locked;
        cj.zMotion = ConfigurableJointMotion.Locked;
        if (scale < 1.0f) cj.angularXMotion = ConfigurableJointMotion.Locked;
        else cj.angularXMotion = ConfigurableJointMotion.Limited;
        cj.angularYMotion = ConfigurableJointMotion.Locked;
        cj.angularZMotion = ConfigurableJointMotion.Locked;

        // Angular x drive
        JointDrive angularXdrive = new JointDrive
        {
            maximumForce = 10,
            positionSpring = 0,
            positionDamper = 1e10f,
        };

        var envParameters = Academy.Instance.EnvironmentParameters;
        float torque = envParameters.GetWithDefault("torque", 1.0f);

        if (torque == 1.0)
        {
            angularXdrive.positionSpring = 0;
            angularXdrive.positionDamper = 500;
        }
        else
        {
            angularXdrive.positionSpring = 200;
            angularXdrive.positionDamper = 5;
        }

        angularXdrive.maximumForce = 3.402823e+38f;
        cj.angularXDrive = angularXdrive;

        // Angular limits
        SoftJointLimit highLimit = cj.highAngularXLimit;
        highLimit.limit = 90;
        cj.highAngularXLimit = highLimit;
        SoftJointLimit lowLimit = cj.lowAngularXLimit;
        lowLimit.limit = -90;
        cj.lowAngularXLimit = lowLimit;

        // Collider 2
        ConfigurableJoint cj2 = collider2.GetComponent<ConfigurableJoint>();
        cj2.anchor = new Vector3(0, 2.5f, 0);
        cj2.xMotion = ConfigurableJointMotion.Locked;
        cj2.yMotion = ConfigurableJointMotion.Locked;
        cj2.zMotion = ConfigurableJointMotion.Locked;
        cj2.angularXMotion = ConfigurableJointMotion.Locked;
        cj2.angularYMotion = ConfigurableJointMotion.Locked;
        cj2.angularZMotion = ConfigurableJointMotion.Locked;

        // Angular x drive collider 2
        JointDrive angularXdrive2 = cj2.angularXDrive;
        angularXdrive2.positionSpring = 20;
        angularXdrive2.positionDamper = 2;
        angularXdrive2.maximumForce = 3.402823e+38f;
        cj2.angularXDrive = angularXdrive2;
    }

    public List<Transform> GetConnectionSites()
    {
        var list = new List<Transform>();
        foreach (var site in connectionSites)
        {
            list.Add(site.transform);
        }
        return list;
    }

    public Transform GetConnectionSite(int connectionSiteNumber)
    {
        // CS3 transform (top) must be first in list for this to work
        if (connectionSiteNumber >= connectionSites.Count)
        {
            //Debug.Log("Trying to get a connection site which is not present. Returning null");
            return null;
        }
        return connectionSites[connectionSiteNumber].transform;
    }

    public void RemoveFixedJoint()
    {
        Destroy(attachmentJoint);
    }

    private void FixedUpdate()
    {

        CollectSensorData();
    }

    // Debug values
    public static Color[] colors = new Color[3] {Color.red, Color.blue, Color.green };
    public float[] sensorValues;
    public float[] CollectSensorData()
    {
        float[] sensorMeasurements = new float[3] { -1f, -1f, -1f };

        for (int i = 0; i < connectionSites.Count; i++)
        {
            // Make a ray outwards
            // 0:green 1:red 2:-red
            Vector3 dir = connectionSites[i].transform.up;
            Vector3 origin = connectionSites[i].transform.position - dir/10;
            Ray outwardsRay = new Ray(origin, dir);

            // Check if ray hit anything
            RaycastHit hit;
            if (Physics.Raycast(outwardsRay, out hit))
            {
                //Debug.Log($"Site {i} detects object {hit.distance} with collider {hit.collider}");
                sensorMeasurements[i] = hit.distance;
            }
            Debug.DrawRay(origin, dir, colors[i], duration:0.5f, depthTest:true);
        }
        sensorValues = sensorMeasurements;
        return sensorMeasurements;
    }
}
