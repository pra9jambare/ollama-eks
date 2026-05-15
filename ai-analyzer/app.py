from fastapi import FastAPI, Request
from kubernetes import client, config
import requests
import smtplib
from email.mime.text import MIMEText

app = FastAPI()

config.load_incluster_config()

v1 = client.CoreV1Api()

OLLAMA_URL = "http://ollama.aiops.svc.cluster.local:11434/api/generate"

@app.post("/analyze")
async def analyze(request: Request):

    data = await request.json()

    alert = data["alerts"][0]

    pod = alert["labels"].get("pod", "")
    namespace = alert["labels"].get("namespace", "default")

    logs = ""

    try:
        logs = v1.read_namespaced_pod_log(
            name=pod,
            namespace=namespace,
            tail_lines=100
        )
    except Exception as e:
        logs = str(e)

    prompt = f"""
You are a Kubernetes SRE expert.

Analyze this issue.

Alert:
{alert}

Pod Logs:
{logs}

Provide:
1. Root cause
2. Fix steps
3. kubectl commands
4. Prevention
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    answer = response.json()["response"]

    send_email(answer)

    return {"status": "success"}

def send_email(body):

    msg = MIMEText(body)

    msg["Subject"] = "Kubernetes Incident"
    msg["From"] = "panavpanoti@gmail.com"
    msg["To"] = "jambapranav@gmail.com"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(
        "YOUR_EMAIL",
        "APP_PASSWORD"
    )

    server.send_message(msg)

    server.quit()
