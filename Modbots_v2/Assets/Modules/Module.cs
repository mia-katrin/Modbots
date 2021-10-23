using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Module : MonoBehaviour
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
        if (connectionSiteNumber > connectionSites.Count)
        {
            Debug.LogError("Trying to get a connection site which is not present. Returning null");
            return null;
        }
        return connectionSites[connectionSiteNumber].transform;
    }

    public void RemoveFixedJoint()
    {
        Destroy(attachmentJoint);
    }
}
