# IaC-Driven WebRTC Stress Testing Framework for BigBlueButton

This repository contains the complete, automated performance evaluation and load generation architecture developed as part of scalability research for high-concurrency WebRTC systems.

The framework leverages the Infrastructure as Code (IaC) paradigm to declaratively provision distributed traffic generator clusters, utilizing Docker containers and Playwright to orchestrate high-concurrency WebRTC user interactions.

## 🏗️ Architecture Overview

The testing suite partitions responsibilities into three distinct conceptual layers:
1. **Infrastructure Provisioning (Terraform):** Dynamically scales compute resources by launching ephemeral AWS Spot Instances deployed within dedicated security zones.
2. **Orchestration & Automation (Playwright & Docker):** Deploys containerized headless Chromium instances designed to isolate runtime environments and emulate highly concurrent media exchanges.
3. **Observability (Dashboard):** Aggregates host-level performance telemetry, feeding standard system resource distribution updates directly into web-accessible internal endpoints.

## 📂 Repository Structure

* `main.tf` — Declarative Terraform definition for provisioning AWS Spot instances, security groups, and automated node initialization.
* `terraform.tfvars` — Configuration file for storing environment-specific variables and credentials safely (locally managed, excluded from git).
* `Dockerfile` — Docker recipe extending a WebRTC-compliant Playwright image to compile independent test execution environments.
* `bot.js` — Core automation script managing headless browser flow, audio/video injection constraints, and synthetic room authentication.
* `bot-vid.js` — Alternative automation script that injects a dynamic canvas overlay rendering real-time host telemetry (CPU, RAM, Uptime) directly into the published video stream.
* `create.py` & `end_meeting.py` — Python utilities interacting with the BigBlueButton API to handle programmatically signed room lifecycles.
* `check_meetings.py` & `get_join_link.py` — Analytical tools to verify active room presence and extract programmatic token-based entrance paths.

## 🚀 Getting Started

### 1. Prerequisites
* Terraform >= 1.0
* Docker
* AWS CLI configured with valid infrastructure access deployment permissions

### 2. Local Environment Configuration

1. Create a `.env` file in the root directory for your Python/Node.js helper utilities:
```env
BBB_URL=[https://your-bbb-instance.com/bigbluebutton/](https://your-bbb-instance.com/bigbluebutton/)
BBB_SECRET=YourTargetServerAPISecretKey
BOTS=1
DURATION=60
```
2.  Create a terraform.tfvars file in the same directory as main.tf to safely store your AWS infrastructure variables and target server credentials:

Terraform: 
```
# BigBlueButton Server Configuration
bbb_url    = "[https://your-bbb-instance.com/bigbluebutton/](https://your-bbb-instance.com/bigbluebutton/)"
bbb_secret = "YourTargetServerAPISecretKey"

# AWS Access Credentials
aws_access_key = "YOUR_AWS_ACCESS_KEY"
aws_secret_key = "YOUR_AWS_SECRET_KEY"

# Load Testing Parameters
instance_count    = 25             # Total number of AWS EC2 instances to provision
bots_per_instance = 20             # Number of concurrent Playwright bots per instance
instance_type     = "c7a.2xlarge"  # Compute-optimized instance type for headless browsers

# Synthetic Video Source Asset
video_url = "[http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4](http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4)"
```
3. Deploying the Cloud Traffic Cluster

Initialize the configuration and apply the deployment. Terraform will automatically pick up the variables defined in your terraform.tfvars file:
Bash
```
terraform init
terraform apply
```
Upon successful fulfillment, Terraform outputs live HTTP monitoring links (http://<instance-ip>:8080) tracking container and instance metrics in real time.
