using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Threading;

class OficinaProLauncher
{
    static int Main(string[] args)
    {
        string baseDir = AppDomain.CurrentDomain.BaseDirectory;
        string composeFile = Path.Combine(baseDir, "docker-compose.yml");
        string envExample = Path.Combine(baseDir, ".env.example");
        string envFile = Path.Combine(baseDir, ".env");
        string appPort = "5000";
        string publicHost = "127.0.0.1";

        Console.Title = "OficinaPro";
        Console.WriteLine("OficinaPro - Inicializador");
        Console.WriteLine("=========================");
        Console.WriteLine();

        if (!File.Exists(composeFile))
        {
            Console.WriteLine("ERRO: docker-compose.yml nao encontrado na pasta do executavel.");
            Pause();
            return 1;
        }

        if (!File.Exists(envFile) && File.Exists(envExample))
        {
            File.Copy(envExample, envFile);
            Console.WriteLine("Arquivo .env criado.");
        }

        appPort = ReadEnvValue(envFile, "APP_HOST_PORT", appPort);
        publicHost = ReadEnvValue(envFile, "APP_PUBLIC_HOST", publicHost);
        string localUrl = "http://127.0.0.1:" + appPort;
        string publicUrl = "http://" + publicHost + ":" + appPort;

        if (!CommandWorks("docker", "--version"))
        {
            Console.WriteLine("ERRO: Docker nao foi encontrado.");
            Console.WriteLine("Instale e abra o Docker Desktop antes de executar o OficinaPro.");
            Pause();
            return 1;
        }

        if (!CommandWorks("docker", "compose version"))
        {
            Console.WriteLine("ERRO: Docker Compose nao foi encontrado.");
            Pause();
            return 1;
        }

        Console.WriteLine("Iniciando app e MySQL...");
        int exitCode = Run("docker", "compose up -d --build", baseDir);
        if (exitCode != 0)
        {
            Console.WriteLine("ERRO: nao foi possivel iniciar os containers.");
            Pause();
            return exitCode;
        }

        Console.WriteLine("Aguardando aplicacao responder...");
        if (!WaitForUrl(localUrl + "/login", 40))
        {
            Console.WriteLine("ERRO: aplicacao nao respondeu em tempo habil.");
            Console.WriteLine("Use Status_OficinaPro.cmd para consultar os logs.");
            Pause();
            return 1;
        }

        Console.WriteLine("OficinaPro iniciado com sucesso.");
        Console.WriteLine("Acesso local: " + localUrl);
        Console.WriteLine("Acesso na rede: " + publicUrl);
        Console.WriteLine("Login inicial: admin / admin123");
        OpenBrowser(publicUrl);
        return 0;
    }

    static string ReadEnvValue(string envFile, string key, string fallback)
    {
        try
        {
            if (!File.Exists(envFile)) return fallback;
            foreach (string rawLine in File.ReadAllLines(envFile))
            {
                string line = rawLine.Trim();
                if (line.Length == 0 || line.StartsWith("#")) continue;
                int equalsIndex = line.IndexOf('=');
                if (equalsIndex <= 0) continue;
                string lineKey = line.Substring(0, equalsIndex).Trim();
                if (!lineKey.Equals(key, StringComparison.OrdinalIgnoreCase)) continue;
                string value = line.Substring(equalsIndex + 1).Trim().Trim('"');
                return value.Length > 0 ? value : fallback;
            }
        }
        catch
        {
            return fallback;
        }
        return fallback;
    }

    static bool CommandWorks(string file, string args)
    {
        return Run(file, args, AppDomain.CurrentDomain.BaseDirectory, true) == 0;
    }

    static int Run(string file, string args, string workingDirectory, bool quiet = false)
    {
        try
        {
            ProcessStartInfo info = new ProcessStartInfo();
            info.FileName = file;
            info.Arguments = args;
            info.WorkingDirectory = workingDirectory;
            info.UseShellExecute = false;
            info.RedirectStandardOutput = true;
            info.RedirectStandardError = true;
            Process process = Process.Start(info);
            process.OutputDataReceived += (sender, e) => { if (!quiet && e.Data != null) Console.WriteLine(e.Data); };
            process.ErrorDataReceived += (sender, e) => { if (!quiet && e.Data != null) Console.WriteLine(e.Data); };
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();
            process.WaitForExit();
            return process.ExitCode;
        }
        catch (Exception ex)
        {
            if (!quiet) Console.WriteLine(ex.Message);
            return 1;
        }
    }

    static bool WaitForUrl(string url, int attempts)
    {
        for (int i = 0; i < attempts; i++)
        {
            try
            {
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
                request.Timeout = 5000;
                using (HttpWebResponse response = (HttpWebResponse)request.GetResponse())
                {
                    if ((int)response.StatusCode >= 200 && (int)response.StatusCode < 500)
                    {
                        return true;
                    }
                }
            }
            catch
            {
                Thread.Sleep(3000);
            }
        }
        return false;
    }

    static void OpenBrowser(string url)
    {
        try
        {
            ProcessStartInfo info = new ProcessStartInfo();
            info.FileName = url;
            info.UseShellExecute = true;
            Process.Start(info);
        }
        catch
        {
            Console.WriteLine("Abra manualmente: " + url);
        }
    }

    static void Pause()
    {
        Console.WriteLine();
        Console.WriteLine("Pressione ENTER para sair.");
        Console.ReadLine();
    }
}
