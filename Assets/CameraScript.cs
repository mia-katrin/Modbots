using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraScript : MonoBehaviour
{
    // singleton
    private static CameraScript instance;
    public static CameraScript Instance { get { return instance; } }

    public ModularRobot target;
    public Vector3 relativeCamPos = new Vector4(3f, 3f, 3f);
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
            transform.LookAt(new Vector3(modPos.x, relativeCamPos.y, modPos.z));

            transform.RotateAround(modPos, Vector3.up, angle);
        }
        else
        {
            Debug.Log("Camera has no target");
        }
    }
}
