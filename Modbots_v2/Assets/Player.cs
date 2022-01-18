using UnityEngine;
using System.IO;
using System.Collections;
using System;
using System.Collections.Generic;

public class Player : MonoBehaviour
{
    // singleton
    private static Player instance;
    public static Player Instance { get { return instance; } }

    public GameObject collider1Prefab;
    public GameObject collider2Prefab;

    List<GameObject> spheres;

    // Use this for initialization
    void Awake()
    {
        // Singleton enforce
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

        ComSideChannel.PlayRecording += PlayRecording;
        ComSideChannel.Instance.SendMessage("Subscribed");
    }

    private void PlayRecording(string filename)
    {
        ComSideChannel.Instance.SendMessage("Start playing");
        spheres = new List<GameObject>();
        StartCoroutine(ReadFile(filename));
        ComSideChannel.Instance.SendMessage("Coroutine started");
    }

    // Update is called once per frame
    private IEnumerator ReadFile(string filename)
    {
        ComSideChannel.Instance.SendMessage("About to make input stream");
        StreamReader inputStream = new StreamReader(filename);

        ComSideChannel.Instance.SendMessage("About to read from file");
        while (!inputStream.EndOfStream)
        {
            yield return new WaitForFixedUpdate();

            string line = inputStream.ReadLine();
            TreatLine(line);
        }

        inputStream.Close();
        ComSideChannel.Instance.SendMessage("Closed stream");
    }

    private void TreatLine(string line)
    {
        foreach (var sphere in spheres)
        {
            Destroy(sphere);
        }
        spheres.Clear();

        // 1,1,1v2,2,2,2/0.1v3,3,3v4,4,4,4|...|\n => "1,1,1v2,2,2,2/0.1v3,3,3v4,4,4,4" , "..."
        string[] lineSplit = line.Split('|');

        foreach (var item in lineSplit)
        {
            // Dunno how C# split works, but in python the last | will create a "" str
            if (item.Length > 0)
            {
                // 1,1,1v2,2,2,2/0.1v3,3,3v4,4,4,4 => "1,1,1v2,2,2,2" , "0.1v3,3,3v4,4,4,4"
                string[] part1and2 = item.Split('/');

                // 1,1,1v2,2,2,2 => "1,1,1" , "2,2,2,2"
                string[] part1 = part1and2[0].Split('v');
                GameObject collider1 = Instantiate(collider1Prefab);
                collider1.transform.SetPositionAndRotation(
                        SplitTransformVec3(part1[0]),
                        SplitTransformQuat(part1[1]));
                spheres.Add(collider1);

                // 0.1v3,3,3v4,4,4,4 => "0.1" , "3,3,3" , "4,4,4,4"
                string[] part2 = part1and2[1].Split('v');

                GameObject collider2 = Instantiate(collider2Prefab);
                collider2.transform.SetPositionAndRotation(
                        SplitTransformVec3(part2[1]),
                        SplitTransformQuat(part2[2]));
                float scale = float.Parse(part2[0]);
                collider2.transform.GetChild(0).transform.GetChild(0).localScale += Vector3.up * (scale - 1);
                spheres.Add(collider2);

                if (scale < 1f)
                {
                    Destroy(collider1.transform.GetChild(0).GetChild(0).GetChild(0).gameObject);
                    Destroy(collider1.transform.GetChild(0).GetChild(0).GetChild(1).gameObject);
                }
            }
        }
    }

    private Vector3 SplitTransformVec3(string stringRepresentation)
    {
        // "3,3,3" => Vector3(3,3,3)
        string[] commaList = stringRepresentation.Split(',');
        return new Vector3(
            float.Parse(commaList[0]),
            float.Parse(commaList[1]),
            float.Parse(commaList[2])
        );
    }

    private Quaternion SplitTransformQuat(string stringRepresentation)
    {
        // "4,4,4,4" => Quaternion(4,4,4,4)
        string[] commaList = stringRepresentation.Split(',');
        return new Quaternion(
            float.Parse(commaList[0]),
            float.Parse(commaList[1]),
            float.Parse(commaList[2]),
            float.Parse(commaList[3])
        );
    }
}
