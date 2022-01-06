using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;

public class CameraScript : MonoBehaviour
{
    // singleton
    private static CameraScript instance;
    public static CameraScript Instance { get { return instance; } }

    public ModularRobot target;
    public Vector3 relativeCamPos = new Vector3(3f, 3f, 3f);
    private float angle = 0;
    private float distance;

    public void Start()
    {
        // Make sure there is only one instance 
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

        var envParameters = Academy.Instance.EnvironmentParameters;
        float envEnum = envParameters.GetWithDefault("envEnum", 0.0f);

        switch (envEnum)
        {
            case 0.0f:
                Debug.LogError("Floor cam");
                relativeCamPos = new Vector3(0f, 0.01f, -8f);
                break;
            case 3f:
                Debug.LogError("Corridor cam");
                relativeCamPos = new Vector3(0f, 0.01f, -8f);
                break;
            case 1f:
                Debug.LogError("Maze cam");
                relativeCamPos = new Vector3(0f, 7f, -5f);
                break;
            case 2f:
                Debug.LogError("Stair cam");
                relativeCamPos = new Vector3(0f, 7f, -5f);
                break;
            default:
                break;
        }

        distance = relativeCamPos.magnitude;
    }

    // Update is called once per frame
    void Update()
    {
        if (target != null)
        {
            if (Input.GetKey(KeyCode.LeftArrow))
            {
                angle += 1f;
            }
            else if (Input.GetKey(KeyCode.RightArrow))
            {
                angle -= 1f;
            }
            else if (Input.GetKey(KeyCode.DownArrow))
            {
                distance += 0.1f;
                relativeCamPos = relativeCamPos.normalized * distance;
            }
            else if (Input.GetKey(KeyCode.UpArrow))
            {
                distance -= 0.1f;
                relativeCamPos = relativeCamPos.normalized * distance;
            }

            Vector3 modPos = target.GetPosition();

            transform.position = new Vector3(modPos.x + relativeCamPos.x, relativeCamPos.y, modPos.z + relativeCamPos.z);

            // Look at
            transform.LookAt(new Vector3(modPos.x, 0f, modPos.z));

            transform.RotateAround(modPos, Vector3.up, angle);
        }
        else
        {
            Debug.Log("Camera has no target");
        }
    }
}
