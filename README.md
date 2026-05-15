# 📦 Kubernetes AI Incident Analyzer (Ollama + Prometheus + Alertmanager)

### This project implements an AI-driven Kubernetes incident detection and resolution system using:

Kubernetes (EKS)
Prometheus + kube-prometheus-stack
Alertmanager
FastAPI AI Analyzer
Ollama (LLM for root cause analysis)
SMTP Email notifications

### 🚀 Architecture
Kubernetes Cluster
        │
        ▼
Prometheus (metrics + alerts)
        │
        ▼
Alertmanager
        │ (webhook)
        ▼
AI Analyzer (FastAPI)
        │
        ▼
Ollama LLM
        │
        ▼
Email Notification (SMTP)

### 📁 Project Structure
└── required-yaml

        ├── ai-analyzer-service.yaml

        ├── ai-analyzer.yaml

        ├── aiops.yaml

        ├── fail-pod.yaml
        
        ├── ollama-deployment.yaml

        ├── ollama-service.yaml

        ├── pod-alert.yaml

        ├── rbac.yaml

        ├── values-fargate.yaml

        ├── values.yaml

└── ai-analyzer

        ├── app.py

        ├── requirements.txt

        ├── Dockerfile

└── README.md


### ⚙️ Step 1 — Install Monitoring Stack
``` bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
```

### ⚙️ Step 2 — Deploy AI Analyzer
``` bash
kubectl create namespace aiops
kubectl apply -f ai-analyzer-deployment.yaml
kubectl apply -f ai-analyzer-service.yaml
```

### ⚙️ Step 3 — Deploy Ollama
``` bash
kubectl apply -f ollama-deployment.yaml
kubectl apply -f ollama-service.yaml
```
### ⚠️ Step 4 — Install LLM Model in Ollama
``` bash
kubectl exec -it -n aiops deploy/ollama -- ollama pull phi3
````

### Recommended models:
phi3 (lightweight, recommended)
tinyllama (very small footprint)

### ⚙️ Step 5 — Configure Alertmanager
Update Helm values:
``` bash
helm upgrade monitoring prometheus-community/kube-prometheus-stack -n monitoring -f values.yaml
``` 


### 📧 Step 6 — Configure Email (SMTP)
``` yaml
Inside app.py:

msg["From"] = "your_email@gmail.com"
msg["To"] = "your_email@gmail.com"

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login("your_email@gmail.com", "APP_PASSWORD")
```
Use Gmail App Password:
https://myaccount.google.com/apppasswords


### 🧠 Step 7 — AI Analyzer Flow
Alert triggered in Prometheus
Alertmanager sends webhook
AI Analyzer receives request
Ollama generates root cause analysis
Email is sent with resolution suggestion


###  🧪 Step 8 — How to Manually Verify Alert Trigger
####  8.1 Create a test workload
``` bash
kubectl run test-pod --image=nginx --restart=Never
```

#### 8.2 Delete pod to trigger alert condition
``` bash
kubectl delete pod test-pod
```

#### 8.3 Verify alert in Prometheus UI
Port forward Prometheus:
``` bash
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-stack-prometheus 9090:9090
```

Open:
http://localhost:9090/alerts
Check:
Alert state = FIRING

#### 8.4 Verify Alertmanager received alert

Port forward:
``` bash
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-alertmanager 9093:9093
```

Open:
http://localhost:9093

Check:
Alerts tab → should show active alerts

#### 8.5 Verify AI Analyzer received webhook
``` bash
kubectl logs -n aiops deploy/ai-analyzer -f
```
Expected log:
POST /analyze

#### 8.6 Verify Email delivery
Check mailbox configured in app.py.
