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
        Debug.LogError("We got here!");
        doneEpisode = false;
        List<Texture2D> frames = new List<Texture2D>();

        StartCoroutine(SaveFrames(frames, filename));
    }

    private IEnumerator SaveFrames(List<Texture2D> frames, string filename)
    {
        while (!doneEpisode)
        {
            // Method found at: https://docs.unity3d.com/ScriptReference/WaitForEndOfFrame.html

            // We should only read the screen buffer after rendering is complete
            yield return new WaitForEndOfFrame();

            // Read screen contents into the texture
            Texture2D tex = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0);
            frames.Add(tex);
            Debug.LogError("Getting images");
        }
        Debug.LogError("Completed getting images");

        for (int i = 0; i < frames.Count; i++)
        {
            frames[i].Apply();

            // Encode texture into PNG
            byte[] bytes = frames[i].EncodeToPNG();

            // Write to a file in a video folder
            // Path works on executable only
            File.WriteAllBytes(Application.dataPath + $"{filename}/frame{i}.png", bytes);
            Debug.LogError(Application.dataPath + $"{filename}/frame{i}.png");
        }
        for (int i = 0; i < frames.Count; i++)
        {
            Destroy(frames[i]);
        }
    }
}
