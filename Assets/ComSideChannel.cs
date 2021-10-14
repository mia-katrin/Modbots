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
    public static event Action RecordingRequested;

    public ComSideChannel()
    {
        ChannelId = new Guid("621f0a70-4f87-11ea-a6bf-784f4387d1f7");
    }

    protected override void OnMessageReceived(IncomingMessage msg)
    {
        connectionEstablished = true;
        var receivedString = msg.ReadString();
        //Debug.LogError($"Got {receivedString}");
        if (receivedString == "Hello")
        {
            SendMessage("Hello back!");
        }
        else if (receivedString == "Record")
        {
            RecordingRequested.Invoke();
        }
        else
        {
            //SendMessage($"Got ping");
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