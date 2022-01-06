using UnityEngine;
using System.Collections;
using Unity.MLAgents;
using System;

public class MyEnvironmentParameters : MonoBehaviour
{
    // singleton
    private static MyEnvironmentParameters instance;
    public static MyEnvironmentParameters Instance { get { return instance; } }

    public event Action<float> EnvEnumSet;

    public float envEnum = 0.0f;

    public void Awake()
    {
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

        Academy.Instance.EnvironmentParameters.RegisterCallback("envEnum", EnvEnumSet);

        EnvEnumSet += EnvEnumSetHandling;
    }

    private void EnvEnumSetHandling(float envEnumNew)
    {
        envEnum = envEnumNew;
    }
}
