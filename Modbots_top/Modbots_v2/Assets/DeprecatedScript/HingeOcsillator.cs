using UnityEngine;
using System.Collections;

public class HingeOcsillator : MonoBehaviour
{
    public bool increase;
    public float speed;
    public float targetVelocity;

    // Use this for initialization
    void Start()
    {
        increase = true;
        targetVelocity = 0;
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void FixedUpdate()
    {
        
        HingeJoint hinge;
        bool exists = gameObject.TryGetComponent<HingeJoint>(out hinge);
        if (exists)
        {
            JointMotor motor = hinge.motor;

            if (increase)
            {
                targetVelocity += speed/100;
                increase = (targetVelocity <= speed);
            } else
            {
                targetVelocity -= speed;
                increase = (targetVelocity <= -speed);
            }

            motor.targetVelocity = targetVelocity;
            hinge.motor = motor;
        }
    }
}
