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

        ComSideChannel.StopRecordingRequested += RecordingOver;
        ComSideChannel.RecordingRequested += StartRecording;
    }

    void RecordingOver() { doneEpisode = true; }

    public void StartRecording(string filename)
    {
        doneEpisode = false;

        StartCoroutine(RecordFrames(filename));
    }

    private IEnumerator RecordFrames(string filename)
    {
        List<string> text = new List<string>();
        while (!doneEpisode)
        {
            yield return new WaitForFixedUpdate();
            if (ModularRobot.Instance.rootGO != null)
            {
                Vector3 pos = ModularRobot.Instance.rootGO.transform.GetChild(0).transform.position;
                Quaternion rot = ModularRobot.Instance.rootGO.transform.GetChild(0).transform.rotation;
                foreach (var module in ModularRobot.Instance.allModules)
                {
                    pos = module.transform.GetChild(0).transform.position;
                    rot = module.transform.GetChild(0).transform.rotation;
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
                GameManager.Instance.pythonCom.SendMessage("State written");
            }
        }
        GameManager.Instance.pythonCom.SendMessage("Done, about to save frames");
        SaveFrames(text.ToArray(), filename);
    }

    private void SaveFrames(string[] lines, string filename)
    {
        GameManager.Instance.pythonCom.SendMessage($"Using file {filename}");
        using FileStream fs = new FileStream(filename
                                     , FileMode.OpenOrCreate
                                     , FileAccess.ReadWrite);
        GameManager.Instance.pythonCom.SendMessage("New streamwriter");
        StreamWriter tw = new StreamWriter(fs);
        GameManager.Instance.pythonCom.SendMessage("About to write");
        foreach (var line in lines)
        {
            tw.Write(line);
        }
        GameManager.Instance.pythonCom.SendMessage("File written");
        GameManager.Instance.pythonCom.SendMessage("About to close file");
        tw.Flush();
        GameManager.Instance.pythonCom.SendMessage("File is closed");
    }
}
