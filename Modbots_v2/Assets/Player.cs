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

        string[] lineSplit = line.Split('|');

        foreach (var item in lineSplit)
        {
            if (item.Length > 0)
            {
                string[] coor = item.Split(',');
                GameObject sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                sphere.transform.position = new Vector3(float.Parse(coor[0]), float.Parse(coor[1]), float.Parse(coor[2]));
                spheres.Add(sphere);
            }
        }
    }
}
