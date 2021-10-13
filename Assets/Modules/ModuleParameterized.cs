using System.Collections;
using System.Collections.Generic;
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

    public bool collisionEntered = false;
    private float originalFemaleDisplacement;

    public int index = -1;

    public void SetIndex(int i)
    {
        index = i;

        float r = i / 15f;
        float g = (15 - i) / 15f;
        float b = (15 - i) / 15f;
        transform.GetChild(0).GetChild(3).gameObject.GetComponent<Renderer>().material.color = new Color(r, g, b);
        transform.GetChild(0).GetChild(4).gameObject.GetComponent<Renderer>().material.color = new Color(r, g, b);
        transform.GetChild(0).GetChild(5).gameObject.GetComponent<Renderer>().material.color = new Color(r, g, b);
    }

    private void Awake()
    {
        GameObject collider1 = transform.GetChild(0).gameObject;
        originalFemaleDisplacement = collider1.transform.localPosition.y;
    }

    // MUST BE CALLED!
    public void SetSize(float xSize)
    {
        // Get both colliders
        GameObject collider1 = transform.GetChild(0).gameObject;
        GameObject collider2 = transform.GetChild(1).gameObject;

        if (xSize < 1.0f)
        {
            connectionSites.Remove(collider1.transform.GetChild(0).gameObject);
            connectionSites.Remove(collider1.transform.GetChild(1).gameObject);

            connectionSites.TrimExcess();
            Debug.Log(connectionSites.Count);

            Destroy(collider1.transform.GetChild(0).gameObject); // CS1
            Destroy(collider1.transform.GetChild(1).gameObject); // CS2
            // Leave connection site CS3 and ConnectionSite
            Destroy(collider1.transform.GetChild(4).gameObject); // ConnectionSite (1)
            Destroy(collider1.transform.GetChild(5).gameObject); // ConnectionSite (2)
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
        rb.mass = 10;

        Rigidbody rb2 = collider2.GetComponent<Rigidbody>();
        rb2.angularDrag = 0.05f;
        rb2.mass = 10 * (0.5f + scale/(scale + 1)); // Non-linear scaling using sigmoid

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
        JointDrive angularXdrive = cj.angularXDrive;
        angularXdrive.positionSpring = 1000;
        angularXdrive.positionDamper = 10;
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
            Debug.Log("Trying to get a connection site which is not present. Returning null");
            return null;
        }
        return connectionSites[connectionSiteNumber].transform;
    }

    public void RemoveFixedJoint()
    {
        Destroy(attachmentJoint);
    }
}
