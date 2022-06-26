using UnityEngine;

public class JointController : MonoBehaviour
{
    public float amplitude, frequency, phase, offset;
    public ConfigurableJoint joint;
    private float timePassed = 0;

    public int fixedUpdatesToWait = 100;
    private int updatesExperienced = 0;

    public void SetControlValues(float[] vals)
    {
        amplitude = vals[0];
        frequency = vals[1];
        phase = vals[2];
        offset = vals[3];
    }

    private float ClampToValid(float newRotation)
    {
        if (newRotation < -90)
        {
            newRotation = -90;
        }
        else if (newRotation > 90)
        {
            newRotation = 90;
        }
        return newRotation;
    }

    private void FixedUpdate()
    {
        if (joint != null)
        {
            Quaternion tr = joint.targetRotation;
            tr.x = ClampToValid(amplitude * Mathf.Sin(frequency * timePassed + phase) + offset);
            joint.targetRotation = tr;
        }

        if (updatesExperienced >= fixedUpdatesToWait)
        {
            timePassed += Time.fixedDeltaTime;
        }
        updatesExperienced += 1;
    }
}
