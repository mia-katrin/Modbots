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

    // Prefabs of parts that need animating
    // Should not have any physics components
    // Maybe having a collider is fine, but no rigidbodies
    public GameObject collider1Prefab;
    public GameObject collider2Prefab;

    List<GameObject> animatedObjects;

    void Awake()
    {
        // Singleton enforce pattern begin
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
        // Singleton enforce pattern end

        // Listen to events issued by the Unity-side side schannel
        ComSideChannel.PlayRecording += PlayRecording;
    }

    private void PlayRecording(string filename)
    {
        animatedObjects = new List<GameObject>();
        StartCoroutine(ReadFile(filename));
    }

    private IEnumerator ReadFile(string filename)
    {
        StreamReader inputStream = new StreamReader(filename);

        while (!inputStream.EndOfStream)
        {
            yield return new WaitForFixedUpdate();

            // Reading one line per fixed update
            string line = inputStream.ReadLine();
            TreatLine(line);
        }

        inputStream.Close();
    }

    private void TreatLine(string line)
    {
        // Likely a better solution to just move the objects instead of spawning
        // them and deleting them
        // But here I delete them all
        // Performance bad, slow? Fix this :)
        foreach (var obj in animatedObjects)
        {
            Destroy(obj);
        }
        animatedObjects.Clear();

        // 1,1,1v2,2,2,2/0.1v3,3,3v4,4,4,4|...|\n => "1,1,1v2,2,2,2/0.1v3,3,3v4,4,4,4" , "..."
        string[] lineSplit = line.Split('|');

        foreach (var item in lineSplit)
        {
            // Dunno how C# split works, but in python the last | will create a "" str
            if (item.Length > 0)
            {
                // 1,1,1v2,2,2,2/0.1v3,3,3v4,4,4,4 => "1,1,1v2,2,2,2" , "0.1v3,3,3v4,4,4,4"
                string[] part1and2 = item.Split('/');

                // Make the different parts
                GameObject collider1 = MakeCol1(part1and2[0]);
                float scale = MakeCol2(part1and2[1]);

                // Adjust the model after the info
                if (scale < 1f)
                {
                    Destroy(collider1.transform.GetChild(0).GetChild(0).GetChild(0).gameObject);
                    Destroy(collider1.transform.GetChild(0).GetChild(0).GetChild(1).gameObject);
                }
            }
        }
    }

    private GameObject MakeCol1(string info)
    {
        // 1,1,1v2,2,2,2 => "1,1,1" , "2,2,2,2"
        string[] part1 = info.Split('v');

        GameObject collider1 = Instantiate(collider1Prefab);
        collider1.transform.SetPositionAndRotation(
                SplitTransformVec3(part1[0]),
                SplitTransformQuat(part1[1]));
        animatedObjects.Add(collider1);

        return collider1;
    }

    private float MakeCol2(string info)
    {
        // 0.1v3,3,3v4,4,4,4 => "0.1" , "3,3,3" , "4,4,4,4"
        string[] part2 = info.Split('v');

        GameObject collider2 = Instantiate(collider2Prefab);
        collider2.transform.SetPositionAndRotation(
                SplitTransformVec3(part2[1]),
                SplitTransformQuat(part2[2]));
        float scale = float.Parse(part2[0]);
        collider2.transform.GetChild(0).transform.GetChild(0).localScale += Vector3.up * (scale - 1);
        animatedObjects.Add(collider2);

        return scale;
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
