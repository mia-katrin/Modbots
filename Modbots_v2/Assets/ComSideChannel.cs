using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.SideChannels;
using System.Text;
using System;

public class ComSideChannel : SideChannel
{
    private static readonly ComSideChannel instance = new ComSideChannel();
    public static ComSideChannel Instance
    {
        get { return instance; }
    }

    bool connectionEstablished = false;
    public static event Action<string> OnReceivedEncoding;
    public static event Action<string> RecordingRequested;
    public static event Action StopRecordingRequested;
    public static event Action<string> PlayRecording;

    public ComSideChannel()
    {
        ChannelId = new Guid("621f0a70-4f87-11ea-a6bf-784f4387d1f7");
    }

    protected override void OnMessageReceived(IncomingMessage msg)
    {
        connectionEstablished = true;
        var receivedString = msg.ReadString();

        if (receivedString == "Hello")
        {
            SendMessage("Hello back!");
        }
        else if (receivedString.StartsWith("Record"))
        {
            string filename = receivedString.Split(',')[1].Trim('_');
            RecordingRequested.Invoke(filename);
        }
        else if (receivedString == "Stop recording")
        {
            StopRecordingRequested.Invoke();
        }
        else if (receivedString.StartsWith("Play"))
        {
            string filename = receivedString.Split(',')[1].Trim('_');
            PlayRecording(filename);
        }
        else
        {
            OnReceivedEncoding.Invoke(receivedString);
        }
    }

    public void SendMessage(string message)
    {
        if (!connectionEstablished)
        {
            Debug.Log("There has not been previous communication from Python");
        }
        else
        {
            using (var msgOut = new OutgoingMessage())
            {
                msgOut.WriteString(message);
                QueueMessageToSend(msgOut);
            }
        }
    }
}