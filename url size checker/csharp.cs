using System;
using System.Net;
using System.IO;

class Program
{
  static void Main()
  {
    string filePath = "links.txt";

    long totalSize = 0;

    foreach (string url in File.ReadAllLines(filePath))
    {
      HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
      long size = long.Parse(request.GetResponse().Headers["Content-Length"]);
      totalSize += size;
      Console.WriteLine($"Downloaded {url} - {size} bytes");
    }

    Console.WriteLine($"Total size: {totalSize} bytes");
  }
}