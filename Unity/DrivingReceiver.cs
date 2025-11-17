using UnityEngine;
using System;

public class DrivingReceiver : MonoBehaviour
{
    public int port = 5007;  // separate port if desired
    private Receiver receiver;

    public float moveSpeed = 2f;   // m/s forward speed
    public float turnSpeed = 90f;  // degrees per second

    private string latestCommand = null;
    private readonly object lockObj = new object();

    void Start()
    {
        receiver = new Receiver(port);
        receiver.OnMessageReceived += HandleMessage;
        receiver.Start();
    }

    private void HandleMessage(string msg)
    {
        msg = msg.Trim().ToLower();

        lock (lockObj)
            latestCommand = msg;
    }

    void Update()
    {
        string cmd = null;

        lock (lockObj)
        {
            if (latestCommand != null)
            {
                cmd = latestCommand;
                latestCommand = null;
            }
        }

        if (cmd != null)
            ExecuteCommand(cmd);
    }

    private void ExecuteCommand(string cmd)
    {
        if (cmd == "forward")
        {
            transform.Translate(Vector3.forward * moveSpeed * Time.deltaTime);
        }
        else if (cmd == "stop")
        {
            transform.Translate(Vector3.forward * 0.0f);
        }
        else if (cmd.StartsWith("turn"))
        {
            float angle = ExtractAngle(cmd);    // supports "turn 30" or "turn -45"
            transform.Rotate(Vector3.up, angle * Time.deltaTime);
        }
        else
        {
            Debug.Log($"Unknown command: {cmd}");
        }
    }

    private float ExtractAngle(string text)
    {
        string[] parts = text.Split(' ');
        if (parts.Length == 2 && float.TryParse(parts[1], out float angle))
            return angle;

        return turnSpeed;  // default turn rate
    }

    void OnApplicationQuit()
    {
        receiver?.Stop();
    }
}

