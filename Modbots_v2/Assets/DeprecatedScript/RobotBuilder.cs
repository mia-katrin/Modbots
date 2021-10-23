using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.SideChannels;
using System.Text;
using System;

public class RobotBuilder
{
    public static GameObject MakeRobot(string gene)
    {
        // Return root of new robot
        GameObject root = GameObject.CreatePrimitive(PrimitiveType.Cube);
        root.transform.Translate(Vector3.up * 2);

        IterativeRead(0, gene, root, new Stack<GameObject>());

        root.AddComponent<Rigidbody>();
        AddArticulation(root);

        return root;
    }

    private static void IterativeRead(int readPosition, string gene, GameObject p, Stack<GameObject> stack)
    {
        char allele = gene[readPosition];
        switch (allele)
        {
            case 'F':
                p = FCase(ref readPosition, gene, p);
                break;
            case 'C':
                p = CCase(ref readPosition, gene, p);
                break;
            case 'T':
                p = TCase(ref readPosition, gene, p);
                break;
            case 'H':
                p = HCase(ref readPosition, gene, p);
                break;
            case '[':
                stack.Push(p);
                break;
            case ']':
                if (stack.Count > 0) p = stack.Pop();
                break;
            default:
                break;

        }

        readPosition += 1;
        if (readPosition < gene.Length)
        {
            IterativeRead(readPosition, gene, p, stack);
        }
    }

    private static GameObject FCase(ref int readPosition, string gene, GameObject p)
    {
        GameObject child = GameObject.CreatePrimitive(PrimitiveType.Cube);
        child.transform.SetParent(p.transform, worldPositionStays: false);
        child.transform.Translate(Vector3.forward * 3);

        child.tag = "fixed";

        Color boxColor = new Color(readPosition / (float)gene.Length, 0.5f, 0.8f);
        child.GetComponent<Renderer>().material.color = boxColor;

        return child;
    }

    private static GameObject CCase(ref int readPosition, string gene, GameObject p)
    {
        string num = ReadParanthesis(ref readPosition, gene);
        float n = float.Parse(num);

        List<Transform> children = DetachChildren(p.transform);
        p.transform.Rotate(Vector3.up, n);
        ReattachChildren(children, p.transform);

        return p;
    }

    private static GameObject TCase(ref int readPosition, string gene, GameObject p)
    {
        string num = ReadParanthesis(ref readPosition, gene);
        float n = float.Parse(num);

        List<Transform> children = DetachChildren(p.transform);
        p.transform.Rotate(Vector3.left, n);
        ReattachChildren(children, p.transform);

        return p;
    }

    private static GameObject HCase(ref int readPosition, string gene, GameObject p)
    {
        p.tag = "hinge";

        HingeOcsillator hinge = p.AddComponent<HingeOcsillator>();
        hinge.speed = float.Parse(ReadParanthesis(ref readPosition, gene));

        return p;
    }

    private static string ReadParanthesis(ref int readPosition, string gene)
    {
        string num = "";
        readPosition += 2;
        char allele = gene[readPosition];
        while (allele != ')')
        {
            num += allele;
            readPosition += 1;
            allele = gene[readPosition];
        }
        return num;
    }

    private static List<Transform> DetachChildren(Transform parent)
    {
        List<Transform> children = new List<Transform>();
        foreach (Transform child in parent.transform)
        {
            child.parent = null;
            children.Add(child);
        }
        return children;
    }

    private static void ReattachChildren(List<Transform> children, Transform parent)
    {
        foreach (Transform child in children)
        {
            child.SetParent(parent.transform, worldPositionStays: true);
        }
    }

    private static void AddArticulation(GameObject node)
    {
        foreach (Transform childTrans in node.transform)
        {
            GameObject child = childTrans.gameObject;
            child.AddComponent<Rigidbody>();

            switch (child.tag)
            {
                case "fixed":
                    FixedJoint joint = child.AddComponent<FixedJoint>();
                    joint.connectedBody = node.GetComponent<Rigidbody>();
                    break;
                case "hinge":
                    HingeJoint hinge = child.AddComponent<HingeJoint>();
                    hinge.connectedBody = node.GetComponent<Rigidbody>();
                    JointMotor motor = hinge.motor;
                    hinge.useMotor = true;
                    motor.force = 80;
                    motor.targetVelocity = 0;
                    motor.freeSpin = false;
                    hinge.motor = motor;
                    break;
                default:
                    break;
            }

            AddArticulation(child);
        }
    }
}
