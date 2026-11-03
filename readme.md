# 🤖 Agentic ChatBot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/LangGraph-Agent%20Workflow-4B8BF5" alt="LangGraph">
  <img src="https://img.shields.io/badge/FAISS-Vector%20Search-00A7A7" alt="FAISS">
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/Cloud-AWS%20EC2-FF9900?logo=amazonaws&logoColor=white" alt="AWS">
</p>

**Live Application:** [https://chatpilot.duckdns.org](https://chatpilot.duckdns.org)

An AI-powered agentic chatbot built using Streamlit, LangChain, LangGraph, and Ollama Cloud. It supports independent chat threads, persistent conversation memory, real-time response streaming, PDF-based Retrieval-Augmented Generation (RAG), web search, and Human-in-the-Loop (HITL) tool approval.

The application is containerized using Docker and deployed to AWS EC2 through an automated GitHub Actions CI/CD pipeline.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Local Development Setup](#local-development-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Docker Configuration](#docker-configuration)
- [CI/CD Pipeline](#cicd-pipeline)
- [AWS EC2 Deployment](#aws-ec2-deployment)
- [Domain Configuration with DuckDNS](#domain-configuration-with-duckdns)
- [Nginx Reverse Proxy](#nginx-reverse-proxy)
- [HTTPS Configuration](#https-configuration)
- [Application Usage](#application-usage)
- [Persistence and Data Management](#persistence-and-data-management)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)
- [License](#license)
- [Author](#author)

---

## Overview

Agentic ChatBot is a conversational AI application designed to demonstrate how agentic workflows can be integrated into a practical application.

Instead of relying only on a basic LLM conversation, the application uses LangGraph to manage conversation state, invoke tools, retrieve information from uploaded documents, and pause for human approval when required.

The application supports:

- Multiple independent conversations.
- Persistent conversation history.
- Real-time streaming responses.
- PDF document ingestion and semantic retrieval.
- External web search through Tavily.
- Human approval before executing configured tool calls.
- Docker-based deployment.
- Automated CI/CD using GitHub Actions.
- Cloud hosting on AWS EC2.
- HTTPS through Nginx and Let's Encrypt.

## Features

### 1. Multi-threaded Chat

- Create multiple independent conversations.
- Switch between previous conversations.
- Rename and delete chat threads.
- Maintain separate conversation histories.

### 2. Persistent Conversation Memory

- SQLite-based thread metadata management.
- LangGraph checkpointing for conversation persistence.
- Conversation history survives application restarts when stored in the persistent Docker volume.

### 3. Real-time Streaming

- Stream LLM responses instead of waiting for the complete answer.
- Display generated content progressively in Streamlit.

### 4. PDF-based RAG

- Upload PDF documents.
- Extract and split document content into chunks.
- Generate embeddings.
- Store vectors in FAISS.
- Retrieve relevant passages using semantic similarity.
- Answer questions using retrieved document context.

### 5. Tool Calling and Web Search

- Integrate external tools into the LangGraph workflow.
- Use Tavily Search for external information.
- Allow the agent to decide when a configured tool is needed.

### 6. Human-in-the-Loop (HITL)

- Pause execution before configured tool calls.
- Display tool names and arguments for review.
- Allow users to approve or reject execution.
- Resume the graph after the human decision.

### 7. Docker and Cloud Deployment

- Containerized application.
- Docker Compose for application management.
- GitHub Container Registry for image storage.
- GitHub Actions for automated build, publishing, and deployment.
- AWS EC2 hosting.
- DuckDNS custom domain.
- Nginx reverse proxy and HTTPS.

---

## Architecture

The application uses LangGraph to coordinate the LLM, retrieval system, tools, and conversation state.

### Application Architecture

```text
                    User
                     |
                     v
              Streamlit Interface
                     |
                     v
                LangGraph Agent
                     |
                     v
                 LLM
              Ollama Cloud
                     |
          +----------+----------+
          |          |          |
          v          v          v
       RAG Tool   Tavily     HITL
          |       Search   Approval
          v          |          |
        FAISS        |       Human Decision
          |          |          |
          +----------+----------+
                     |
                     v
              Final Response
                     |
                     v
             Streamlit Streaming
```

### Deployment Architecture

```text
                 Developer
                     |
                     v
                GitHub Repo
                     |
                     v
              GitHub Actions
                     |
           +---------+---------+
           |                   |
           v                   v
       Build Docker       Run Checks
           |
           v
      Publish Image
           |
           v
     GitHub Container
        Registry
           |
           v
       SSH Deployment
           |
           v
        AWS EC2
           |
           v
       Docker Compose
           |
           v
      Streamlit App
       Port 8501
           |
           v
       Nginx Proxy
           |
           v
    Let's Encrypt HTTPS
           |
           v
  https://chatpilot.duckdns.org
```

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Chat user interface |
| LangChain | LLM and tool integration |
| LangGraph | Agent workflow orchestration |
| Ollama Cloud | Hosted LLM inference |
| FAISS | Vector similarity search |
| FastEmbed | Embedding generation, if configured |
| PyPDF | PDF document processing |
| SQLite | Thread metadata and checkpoint persistence |
| Tavily | External web search |
| Docker | Application containerization |
| Docker Compose | Container orchestration |
| GitHub Actions | CI/CD automation |
| GitHub Container Registry | Docker image storage |
| AWS EC2 | Cloud hosting |
| Nginx | Reverse proxy |
| DuckDNS | Free domain name |
| Let's Encrypt | Free SSL/TLS certificates |
| Certbot | Certificate installation and renewal |

---

## Project Structure

```text
agentic-chatbot/
│
├── .github/
│   ├── workflows/
│   │   └── cicd.yaml
│   │
│   └── scripts/
│       └── deploy-ec2.sh
│
├── app.py
├── agentic_bot_back.py
├── rag_pipeline.py
├── thread_db.py
│
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .gitignore
├── .env.example
├── readme.md
│
├── chat_bot_workflow.ipynb
│
├── uploads/
├── faiss_index/
├── chat_memory.db
└── indexed_files.json
```

**Important:** Runtime files such as `.env`, uploaded documents, SQLite databases, and FAISS indexes should not be committed to Git. Their actual locations may be managed through Docker volumes.

---

# Local Development Setup

## 1. Prerequisites

Install the following:

- Python 3.10 or newer.
- Git.
- Docker Desktop (for containerized development).
- An Ollama Cloud API key.
- A Tavily API key.
- An embedding provider/API configuration supported by your RAG pipeline.

## 2. Clone the repository

```bash
git clone https://github.com/saurabhNibble/agentic-ChatBot.git

cd agentic-ChatBot
```

## 3. Create a virtual environment

```bash
python -m venv .venv
```

Activate it.

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

## 4. Install dependencies

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

---

# Environment Configuration

Create a `.env` file in the project root.

```env
OLLAMA_API_KEY=your_ollama_cloud_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Configure your model and endpoint in `agentic_bot_back.py`.

For example, the hosted Ollama Cloud OpenAI-compatible endpoint can be configured using:

```python
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    model="gpt-oss:20b",
    base_url="https://ollama.com/v1",
    api_key=os.getenv("OLLAMA_API_KEY"),
    temperature=0,
    streaming=True
)
```

Use the model and endpoint supported by your Ollama Cloud account.

**Security:** Never commit `.env` or expose API keys in source code, screenshots, logs, or GitHub Actions output.

---

# Running the Application

Run the Streamlit application:

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

# Docker Configuration

Docker packages the application and its dependencies into a portable image.

This helps ensure that the application behaves consistently across development and deployment environments.

## 1. Create the Dockerfile

A typical Dockerfile for this application:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health')"

CMD ["streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501"]
```

Adjust the Python version to match the version tested by your project.

## 2. Create `.dockerignore`

```text
.venv
__pycache__
*.pyc
.git
.env
uploads
faiss_index
*.db
```

Add or remove runtime directories according to your Docker volume configuration. Do not exclude files required to build the application.

## 3. Configure Docker Compose

Example configuration:

```yaml
services:
  app:
    build: .
    image: agentic-chatbot
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - chatbot-data:/app/data
    restart: unless-stopped

volumes:
  chatbot-data:
```

Ensure the application stores its SQLite database, uploads, and FAISS data in the persistent volume path. Update the volume mount to match the actual paths used in your Python code.

For the EC2 deployment behind Nginx, consider binding the host port only to localhost:

```yaml
ports:
  - "127.0.0.1:8501:8501"
```

This prevents direct public access to Streamlit while allowing Nginx on the same EC2 instance to reach it.

## 4. Build and run

```bash
docker compose up --build -d
```

Check running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Stop the application:

```bash
docker compose down
```

The named Docker volume remains after `docker compose down`.

**Warning:** Running `docker compose down --volumes` removes the named volume and its stored data.

---

# CI/CD Pipeline

The project uses GitHub Actions to automate testing, Docker image building, image publishing, and deployment.

## Pipeline stages

| Stage | Responsibility |
|---|---|
| Validate | Check Python syntax, Compose configuration, and Docker build |
| Build | Build the application Docker image |
| Publish | Push the image to GHCR |
| Deploy | Connect to EC2 and deploy the published image |
| Verify | Wait for the application health check |

### Step 1: Configure GitHub repository

Push your project to GitHub:

```bash
git add .

git commit -m "Prepare application for CI/CD"

git push origin main
```

### Step 2: Configure GitHub Actions secrets

Open:

`GitHub Repository → Settings → Secrets and variables → Actions`

Create these repository secrets:

| Secret | Description |
|---|---|
| `EC2_HOST` | EC2 public IP or DNS |
| `EC2_USER` | SSH username, usually `ubuntu` |
| `EC2_SSH_PRIVATE_KEY` | Private SSH key for GitHub Actions |
| `EC2_KNOWN_HOSTS` | Verified EC2 SSH host-key entry |

The EC2 application `.env` is configured separately on the server. Do not upload it through GitHub Actions.

### Step 3: GitHub Actions workflow

The workflow is stored at:

```text
.github/workflows/cicd.yaml
```

Its responsibilities are:

1. Trigger on pushes to `main`, pull requests, and configured version tags.
2. Validate the project.
3. Build the Docker image.
4. Authenticate to GitHub Container Registry.
5. Publish the image using `GITHUB_TOKEN`.
6. Connect to EC2 using SSH.
7. Copy the Compose configuration.
8. Execute the deployment script.
9. Verify application health.

The image is published to:

```text
ghcr.io/<owner>/<repository>
```

For example:

```text
ghcr.io/saurabhnibble/agentic-chatbot
```

Images can be tagged using the branch, version, commit SHA, and `latest` tags.

### Step 4: Deployment script

The deployment script is stored at:

```text
.github/scripts/deploy-ec2.sh
```

It should perform these operations:

1. Navigate to `/home/ubuntu/agentic-chatbot`.
2. Authenticate to GHCR using the workflow's short-lived package access token.
3. Pull the newly published image.
4. Start or recreate the service using Docker Compose.
5. Wait for the health check.
6. Report deployment success or failure.

The script must not overwrite the server's `.env` file.

**Security note:** Use a least-privilege package permission such as `packages: read` for deployment. Keep SSH restricted to a trusted static runner egress IP or use a more restricted deployment method such as AWS Systems Manager. Do not expose SSH to the entire internet just to accommodate changing GitHub-hosted runner addresses.

---

# AWS EC2 Deployment

The application is hosted on an Ubuntu EC2 instance.

## Step 1: Create an EC2 instance

In AWS Console:

1. Open EC2.
2. Launch an instance.
3. Select Ubuntu Server.
4. Choose an instance type appropriate for your workload.
5. Configure the key pair.
6. Configure the security group.
7. Launch the instance.

For this deployment, the EC2 public IP is:

```text
13.238.141.186
```

## Step 2: Configure inbound security rules

Configure the EC2 security group:

| Type | Port | Purpose |
|---|---:|---|
| SSH | 22 | Server administration and deployment |
| HTTP | 80 | HTTP and Let's Encrypt validation |
| HTTPS | 443 | Secure web traffic |

Restrict SSH access to a trusted source.

After Nginx is configured, do not expose port `8501` publicly. Allow the reverse proxy to access Streamlit locally on the instance.

## Step 3: Connect to EC2

From your local machine:

```bash
ssh -i your-key.pem ubuntu@13.238.141.186
```

## Step 4: Install Docker

Install Docker Engine and the Docker Compose plugin using the official Docker installation instructions for Ubuntu.

Verify:

```bash
docker --version

docker compose version
```

Allow the Ubuntu user to run Docker commands:

```bash
sudo usermod -aG docker ubuntu
```

Reconnect to the server or refresh the group:

```bash
newgrp docker
```

Verify:

```bash
docker ps
```

## Step 5: Create the application directory

```bash
mkdir -p ~/agentic-chatbot

cd ~/agentic-chatbot
```

## Step 6: Configure environment variables

Create the server-side `.env` file:

```bash
nano .env
```

Add the actual API keys:

```env
OLLAMA_API_KEY=your_real_ollama_cloud_api_key
TAVILY_API_KEY=your_real_tavily_api_key
```

Save the file and restrict permissions:

```bash
chmod 600 .env
```

Never commit this file to GitHub.

## Step 7: Deploy using Docker Compose

The GitHub Actions workflow copies the Compose file and runs the deployment script.

For a manual deployment, once the image is available:

```bash
docker compose pull

docker compose up -d
```

Check the application:

```bash
docker compose ps

docker compose logs -f
```

The application should be reachable locally at:

```text
http://localhost:8501
```

---

# Domain Configuration with DuckDNS

DuckDNS provides a free subdomain that can point to your EC2 public IP.

## Step 1: Register a domain

Visit:

[https://www.duckdns.org](https://www.duckdns.org)

1. Sign in.
2. Create a subdomain.
3. Set its IPv4 address to your EC2 public IP.
4. Save the configuration.

Configured domain:

```text
chatpilot.duckdns.org
```

EC2 public IP:

```text
13.238.141.186
```

## Step 2: Verify DNS resolution

Run:

```bash
nslookup chatpilot.duckdns.org
```

The returned IPv4 address should match your EC2 public IP.

DNS changes may take some time to propagate.

---

# Nginx Reverse Proxy

Nginx receives external web traffic and forwards requests to the Streamlit application.

The user accesses the domain on port 80 or 443, while Nginx communicates with the application on port 8501 locally.

## Step 1: Install Nginx

```bash
sudo apt update

sudo apt install nginx -y
```

Check its status:

```bash
sudo systemctl status nginx
```

## Step 2: Create an Nginx site configuration

```bash
sudo nano /etc/nginx/sites-available/chatpilot
```

Add:

```nginx
server {
    listen 80;
    server_name chatpilot.duckdns.org;

    location / {
        proxy_pass http://127.0.0.1:8501;

        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Streamlit WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
```

## Step 3: Enable the configuration

```bash
sudo ln -s /etc/nginx/sites-available/chatpilot \
/etc/nginx/sites-enabled/chatpilot
```

If the link already exists, do not create a duplicate.

Test the configuration:

```bash
sudo nginx -t
```

Reload Nginx:

```bash
sudo systemctl reload nginx
```

The domain should now open over HTTP:

```text
http://chatpilot.duckdns.org
```

HTTPS is configured in the next section.

---

# HTTPS Configuration

HTTPS encrypts communication between the user's browser and the application.

This deployment uses:

- Let's Encrypt: Free SSL/TLS certificate authority.
- Certbot: Certificate installation and renewal.
- Nginx: Reverse proxy and HTTPS termination.

## Step 1: Install Certbot

Certbot is installed using Snap:

```bash
sudo snap install --classic certbot
```

Verify the installation:

```bash
certbot --version
```

## Step 2: Generate the HTTPS certificate

Run:

```bash
sudo certbot --nginx -d chatpilot.duckdns.org
```

Certbot will ask for:

1. Your email address.
2. Agreement to the terms of service.
3. Optional EFF email preferences.
4. Whether HTTP requests should redirect to HTTPS.

Choose the HTTP-to-HTTPS redirect option.

Certbot obtains the certificate and configures Nginx automatically.

## Step 3: Verify HTTPS

Open:

[https://chatpilot.duckdns.org](https://chatpilot.duckdns.org)

The browser should display a valid secure connection.

## Step 4: Test automatic renewal

```bash
sudo certbot renew --dry-run
```

Let's Encrypt certificates are short-lived and need renewal. Certbot normally configures automatic renewal; the dry run checks that renewal can succeed.

---

# Application Usage

1. Open [ChatPilot](https://chatpilot.duckdns.org).
2. Create a new conversation from the sidebar.
3. Ask a question and receive a streamed response.
4. Upload a PDF document.
5. Add the document to the knowledge base.
6. Ask questions about the uploaded document.
7. Allow the agent to use web search when needed.
8. Review tool arguments when a human approval is requested.
9. Approve or reject the tool execution.
10. Switch, rename, or delete conversations.

---

# Persistence and Data Management

The application uses SQLite and LangGraph checkpointing to maintain conversation state.

Docker named volumes are used to preserve runtime data across container recreation.

Important data includes:

- Chat history and checkpoint database.
- Thread metadata.
- Uploaded PDF documents.
- FAISS vector indexes.
- Document indexing registry.

Verify the configured volume:

```bash
docker volume ls
```

Inspect Compose services:

```bash
docker compose ps
```

**Important:** A Docker volume is persistent storage, not a backup. Back up important data regularly.

Before deleting a volume, understand that this command removes its contents:

```bash
docker compose down --volumes
```

---

# Security Considerations

- Never commit API keys or `.env` files.
- Restrict `.env` permissions on EC2.
- Keep the Streamlit port private behind Nginx.
- Expose only the required web ports publicly.
- Restrict SSH access to trusted sources.
- Use verified SSH host keys for automated deployment.
- Use least-privilege GitHub Actions permissions.
- Validate uploaded documents before processing.
- Treat uploaded PDF content as untrusted input.
- Add authentication and authorization before making the chatbot available to sensitive or private users.
- Back up SQLite databases, uploaded files, and vector indexes.
- Keep Docker, Ubuntu, Nginx, and Python dependencies updated.

---

# Troubleshooting

### 1. Container is not running

```bash
docker compose ps

docker compose logs --tail=100
```

### 2. Application is not responding

```bash
curl -I http://localhost:8501
```

Check whether the container is healthy and listening on port 8501.

### 3. Nginx returns 502 Bad Gateway

Check the application:

```bash
docker compose ps

curl -I http://127.0.0.1:8501
```

Check Nginx:

```bash
sudo nginx -t

sudo tail -n 50 /var/log/nginx/error.log
```

### 4. HTTPS certificate generation fails

Check DNS:

```bash
nslookup chatpilot.duckdns.org
```

Check Nginx:

```bash
sudo systemctl status nginx
```

Check that AWS security group inbound rules allow ports 80 and 443.

### 5. View application logs

```bash
docker compose logs -f app
```

### 6. Redeploy manually

```bash
docker compose pull

docker compose up -d
```

---

# Future Improvements

- Long-term memory and user-specific preferences.
- More advanced multi-agent workflows.
- Additional document formats such as DOCX and TXT.
- Improved RAG evaluation and retrieval quality.
- Authentication and role-based access control.
- Conversation export and download.
- Monitoring, logging, and tracing using LangSmith.
- Automated backups for persistent application data.
- AWS Systems Manager-based deployment instead of direct SSH.
- Infrastructure automation using Terraform.
- Rate limiting and production-grade security hardening.

---

# License

This project currently does not include a license file.

Add an appropriate open-source license before allowing reuse or redistribution.

---

# Author

**Saurabh Yadav**

GitHub: [https://github.com/saurabhNibble](https://github.com/saurabhNibble)

**Live Application:** [https://chatpilot.duckdns.org](https://chatpilot.duckdns.org)

