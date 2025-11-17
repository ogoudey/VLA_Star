using UnityEngine;
using System.Net.Sockets;
using System.Net;
using System.IO;

// Put on camera you want to stream

public class CameraStream : MonoBehaviour
{
    public string ip = "127.0.0.1";
    public int port = 5000;

    private Camera cam;
    private TcpClient client;
    private NetworkStream stream;
    private Texture2D texture;
    private RenderTexture rt;

    void Start()
    {
        cam = GetComponent<Camera>();

        rt = new RenderTexture(640, 480, 24);
        texture = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);

        client = new TcpClient();
        client.Connect(IPAddress.Parse(ip), port);
        stream = client.GetStream();
    }

    void OnDestroy()
    {
        stream?.Close();
        client?.Close();
        if (rt != null) rt.Release();
    }

    void LateUpdate()
    {
        // Render camera → Read into Texture2D
        cam.targetTexture = rt;
        cam.Render();

        RenderTexture.active = rt;
        texture.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
        texture.Apply();
        cam.targetTexture = null;

        // Encode frame
        byte[] pngBytes = texture.EncodeToPNG();

        // Prefix with length
        byte[] lengthBytes = System.BitConverter.GetBytes(pngBytes.Length);

        // Send length + frame
        stream.Write(lengthBytes, 0, lengthBytes.Length);
        stream.Write(pngBytes, 0, pngBytes.Length);
        stream.Flush();
    }
}
