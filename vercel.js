{
  "installCommand": "apt-get update && apt-get install -y gcc default-jdk && pip install -r requirements.txt",
  "buildCommand": "gcc analysis.c -o analysis && javac ReportGenerator.java",
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
