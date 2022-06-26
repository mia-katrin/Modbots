using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

public class Recorder : MonoBehaviour
{
    private bool doneEpisode = false;

    // singleton
    private static Recorder instance;
    public static Recorder Instance { get { return instance; } }

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
        ComSideChannel.StopRecordingRequested += RecordingOver;
        ComSideChannel.RecordingRequested += StartRecording;
    }

    // To stop the corroutine
    void RecordingOver() { doneEpisode = true; }

    public void StartRecording(string filename)
    {
        doneEpisode = false;

        StartCoroutine(RecordFrames(filename));
    }

    private IEnumerator RecordFrames(string filename)
    {
        // We'll put our info in a list
        List<string> text = new List<string>();

        while (!doneEpisode)
        {
            // Waiting for the fixed update that'll sync the physics
            // This could be over or under the recording bit, I have no reason
            yield return new WaitForFixedUpdate();

            RecordBits(text);
        }
        SaveFrames(text.ToArray(), filename);
    }

    private void RecordBits(List<string> text)
    {
        // Some check to see if robot is made
        if (ModularRobot.Instance.RobotExists())
        {
            // Record the positions and rotations
            // Each line will have the format
            // posCollider1 v rotCollider1 / collider1scale v posCollider2 v rotCollider2 | ... |\n

            foreach (var module in ModularRobot.Instance.allModules)
            {
                Vector3 pos = module.transform.GetChild(0).transform.position;
                Quaternion rot = module.transform.GetChild(0).transform.rotation;
                // 0,0,0v0,0,0,0/
                text.Add($"{pos.x},{pos.y},{pos.z}v{rot.x},{rot.y},{rot.z},{rot.w}/");
                pos = module.transform.GetChild(1).transform.position;
                rot = module.transform.GetChild(1).transform.rotation;
                float scale = module.GetComponent<ModuleParameterized>().scale;
                // 1.0v0,0,0v0,0,0,0|
                text.Add($"{scale}v{pos.x},{pos.y},{pos.z}v{rot.x},{rot.y},{rot.z},{rot.w}|");
            }

            // 0,0,0v0,0,0,0/1.0v0,0,0v0,0,0,0|...|\n
            text.Add($"\n");
        }
    }

    private void SaveFrames(string[] lines, string filename)
    {
        using FileStream fs = new FileStream(filename
                                     , FileMode.OpenOrCreate
                                     , FileAccess.ReadWrite);
        StreamWriter tw = new StreamWriter(fs);
        foreach (var line in lines)
        {
            tw.Write(line);
        }
        tw.Flush();
    }
}
