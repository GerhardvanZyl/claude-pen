using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

// Batchmode shot renderer for the dev-loop-greybox skill. Renders every camera
// named Shot_<name> in the given scene to <shotsOut>/<name>.png.
// ponytail: fixed 1920x1080, no settings asset; add args if a brief ever needs another size.
public static class ShotCapture
{
    const string Prefix = "Shot_";
    const int Width = 1920;
    const int Height = 1080;

    public static void Run()
    {
        try
        {
            var args = Environment.GetCommandLineArgs();
            var scene = Arg(args, "-scene") ?? throw new ArgumentException("missing -scene <Assets/...unity>");
            var outDir = Arg(args, "-shotsOut") ?? throw new ArgumentException("missing -shotsOut <dir>");

            EditorSceneManager.OpenScene(scene, OpenSceneMode.Single);
            var cameras = Resources.FindObjectsOfTypeAll<Camera>()
                .Where(c => c.gameObject.scene.IsValid() && c.name.StartsWith(Prefix, StringComparison.Ordinal))
                .ToArray();
            if (cameras.Length == 0)
                throw new InvalidOperationException($"no {Prefix}* cameras in {scene}");
            var duplicate = cameras.GroupBy(c => c.name).FirstOrDefault(g => g.Count() > 1);
            if (duplicate != null)
                throw new InvalidOperationException($"duplicate shot camera name {duplicate.Key}");

            Directory.CreateDirectory(outDir);
            foreach (var camera in cameras)
                Render(camera, Path.Combine(outDir, camera.name.Substring(Prefix.Length) + ".png"));
            Debug.Log($"ShotCapture: wrote {cameras.Length} shots to {outDir}");
            EditorApplication.Exit(0);
        }
        catch (Exception e)
        {
            Debug.LogException(e);
            EditorApplication.Exit(1);
        }
    }

    static void Render(Camera camera, string path)
    {
        var target = new RenderTexture(Width, Height, 24);
        var image = new Texture2D(Width, Height, TextureFormat.RGB24, false);
        var previousTarget = camera.targetTexture;
        var previousActive = RenderTexture.active;
        try
        {
            camera.targetTexture = target;
            camera.Render();
            RenderTexture.active = target;
            image.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
            image.Apply();
            File.WriteAllBytes(path, image.EncodeToPNG());
        }
        finally
        {
            camera.targetTexture = previousTarget;
            RenderTexture.active = previousActive;
            UnityEngine.Object.DestroyImmediate(target);
            UnityEngine.Object.DestroyImmediate(image);
        }
    }

    static string Arg(string[] args, string name)
    {
        var i = Array.IndexOf(args, name);
        return i >= 0 && i + 1 < args.Length ? args[i + 1] : null;
    }
}
