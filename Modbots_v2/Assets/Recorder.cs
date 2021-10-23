using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

public class Recorder : MonoBehaviour
{
    private bool doneEpisode = false;

    // Use this for initialization
    void Awake()
    {
        //BasicAgent.EndFitnessReady += RecordingOver;
        ComSideChannel.RecordingRequested += StartRecording;
    }

    void RecordingOver(float fitness)
    {
        doneEpisode = true;
    }

    public void StartRecording()
    {
        doneEpisode = false;
        List<Texture2D> frames = new List<Texture2D>();

        StartCoroutine(SaveFrames(frames));
    }

    private IEnumerator SaveFrames(List<Texture2D> frames)
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
        }

        for (int i = 0; i < frames.Count; i++)
        {
            frames[i].Apply();

            // Encode texture into PNG
            byte[] bytes = frames[i].EncodeToPNG();

            // Write to a file in a video folder
            // Path works on executable only
            File.WriteAllBytes(Application.dataPath + $"/../../video/frame{i}.png", bytes);
        }
        for (int i = 0; i < frames.Count; i++)
        {
            Destroy(frames[i]);
        }
    }
}
