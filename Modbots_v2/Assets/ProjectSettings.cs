using UnityEngine;
using Unity.MLAgents;

namespace Unity.MLAgentsExamples
{
    /// <summary>
    /// A helper class for the ML-Agents example scenes to override various
    /// global settings, and restore them afterwards.
    /// This can modify some Physics and time-stepping properties, so you
    /// shouldn't copy it into your project unless you know what you're doing.
    /// </summary>
    public class ProjectSettings : MonoBehaviour
    {
        Vector3 originalGravity;
        float originalFixedDeltaTime;
        float originalMaximumDeltaTime;
        int originalSolverIterations;
        int originalSolverVelocityIterations;
        bool originalReuseCollisionCallbacks;

        [Tooltip("Increase or decrease the scene gravity. Use ~3x to make things less floaty")]
        public float gravityMultiplier = 1.0f;

        [Header("Advanced physics settings")]
        [Tooltip("The interval in seconds at which physics and other fixed frame rate updates (like MonoBehaviour's FixedUpdate) are performed.")]
        public float fixedDeltaTime = .02f;
        [Tooltip("The maximum time a frame can take. Physics and other fixed frame rate updates (like MonoBehaviour's FixedUpdate) will be performed only for this duration of time per frame.")]
        public float maximumDeltaTime = 1.0f / 3.0f;
        [Tooltip("Determines how accurately Rigidbody joints and collision contacts are resolved. (default 6). Must be positive.")]
        public int solverIterations = 6;
        [Tooltip("Affects how accurately the Rigidbody joints and collision contacts are resolved. (default 1). Must be positive.")]
        public int solverVelocityIterations = 1;
        [Tooltip("Determines whether the garbage collector should reuse only a single instance of a Collision type for all collision callbacks. Reduces Garbage.")]
        public bool reuseCollisionCallbacks = true;

        public void Awake()
        {
            // Save the original values
            originalGravity = Physics.gravity;
            originalFixedDeltaTime = Time.fixedDeltaTime;
            originalMaximumDeltaTime = Time.maximumDeltaTime;
            originalSolverIterations = Physics.defaultSolverIterations;
            originalSolverVelocityIterations = Physics.defaultSolverVelocityIterations;
            originalReuseCollisionCallbacks = Physics.reuseCollisionCallbacks;

            // Override
            Physics.gravity *= gravityMultiplier;
            Time.fixedDeltaTime = fixedDeltaTime;
            Time.maximumDeltaTime = maximumDeltaTime;
            Physics.defaultSolverIterations = solverIterations;
            Physics.defaultSolverVelocityIterations = solverVelocityIterations;
            Physics.reuseCollisionCallbacks = reuseCollisionCallbacks;
            Debug.Log(Time.maximumDeltaTime);
            // Make sure the Academy singleton is initialized first, since it will create the SideChannels.
            Academy.Instance.EnvironmentParameters.RegisterCallback("gravity", f => { Physics.gravity = new Vector3(0, -f, 0); });
        }

        public void OnDestroy()
        {
            Physics.gravity = originalGravity;
            Time.fixedDeltaTime = originalFixedDeltaTime;
            Time.maximumDeltaTime = originalMaximumDeltaTime;
            Physics.defaultSolverIterations = originalSolverIterations;
            Physics.defaultSolverVelocityIterations = originalSolverVelocityIterations;
            Physics.reuseCollisionCallbacks = originalReuseCollisionCallbacks;
        }
    }
}
