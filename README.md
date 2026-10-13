<div align="center">

# 🧊 CryoTrace
### Autonomous Cold-Chain Logistics Incident Dispatch & Analytics Platform

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph-FF6F00?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Groq LPU](https://img.shields.io/badge/Inference-Groq_LPU-F55036?style=for-the-badge)](https://groq.com/)
[![Pinecone](https://img.shields.io/badge/Vector_DB-Pinecone-000000?style=for-the-badge&logo=pinecone&logoColor=white)](https://www.pinecone.io/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Microsoft SQL Server](https://img.shields.io/badge/Database-MSSQL_2022-CC292B?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)](https://www.microsoft.com/sql-server)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS EC2](https://img.shields.io/badge/Cloud-AWS_EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/ec2/)

<p align="center">
  <b>An enterprise-grade Agentic AI command center that continuously monitors 32,065+ active fleet telemetry records, predicts weather corridor risks in real time, and synthesizes Standard Operating Procedure (SOP) compliance mitigation protocols with strict database-level security guardrails.</b>
</p>

</div>

---

## 📌 Executive Overview

In cold-chain logistics, temperature deviations during the transportation of sensitive cargo—such as pharmaceutical biologics, vaccines, fresh produce, and dairy products—lead to catastrophic spoilage, strict regulatory non-compliance (FDA 21 CFR Part 11, WHO Good Distribution Practices), and severe financial loss.

**CryoTrace** resolves this operational challenge by replacing manual, retrospective dispatch workflows with an autonomous **ReAct AI Agent**. The platform:
1. **Monitors Fleet Telemetry:** Ingests and queries 32,065 multi-sensor fleet telemetry records via high-performance database views.
2. **Correlates Weather Hazards:** Queries real-time meteorological conditions via the Open-Meteo REST API along active GPS transit corridors.
3. **Retrieves Compliance SOPs (RAG):** Semantically searches Standard Operating Procedure (SOP) protocols stored in a Pinecone vector database using dense 1024-dimensional embeddings.
4. **Prevents AI Hallucination Mutations:** Enforces strict database-level Role-Based Access Control (RBAC) so the LLM cannot mutate, alter, or drop raw production tables.
5. **Provides a Glassmorphic Command Center:** A unified operations console with prompt action chips, multi-turn conversational memory, real-time subsystem diagnostic benchmarks, and immutable audit logs.

---

## 🏗️ System Architecture

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │       CryoTrace Glassmorphic Command Center (8501)     │
                                  │   - Real-Time Fleet KPIs & Telemetry Monitor           │
                                  │   - Multi-Turn Natural Language Incident Triage        │
                                  │   - 5/5 Subsystem Endpoint Diagnostic Report Card      │
                                  │   - Admin-Authenticated Security & Audit Log Viewer    │
                                  └───────────────────────────┬────────────────────────────┘
                                                              │
                                                              ▼
                                  ┌────────────────────────────────────────────────────────┐
                                  │        LangGraph ReAct Agentic Orchestrator            │
                                  │   - StateGraph (Reasoner ⇄ ToolNode Cyclic Loop)       │
                                  │   - MemorySaver Session Checkpointer                   │
                                  │   - Reasoning Engine: Groq llama-3.3-70b-versatile     │
                                  └───────────┬───────────────────┬────────────────────┬───┘
                                              │                   │                    │
                   ┌──────────────────────────┘                   │                    └───────────────────────────┐
                   ▼                                              ▼                                                ▼
     ┌───────────────────────────┐                  ┌───────────────────────────┐                    ┌───────────────────────────┐
     │   query_telemetry_db      │                  │ fetch_corridor_conditions │                    │   search_compliance_sop   │
     │  - SQLAlchemy Parameterized│                 │  - Open-Meteo REST API    │                    │  - Pinecone Serverless    │
     │  - Read-Only T-SQL Queries│                  │  - GPS Lat/Lon Resolution │                    │  - BAAI/bge-m3 Embeddings │
     └─────────────┬─────────────┘                  └─────────────┬─────────────┘                    └─────────────┬─────────────┘
                   │                                              │                                                │
                   ▼                                              ▼                                                ▼
     ┌───────────────────────────┐                  ┌───────────────────────────┐                    ┌───────────────────────────┐
     │  Microsoft SQL Server     │                  │  Live Weather Corridor    │                    │   Pinecone Vector DB      │
     │  - Docker Container (1433)│                  │  - Ambient Temperature    │                    │  - Index: fde-sop-local   │
     │  - FDE_VIEWS.VW_ACTIVE_...│                  │  - Wind Gusts & Precip.   │                    │  - Cosine Metric (1024-d) │
     │  - RBAC: USR_FDE_RO (DENY)│                  │  - Corridor Risk Scoring  │                    │  - Tier 1/2/3 Protocols   │
     └───────────────────────────┘                  └───────────────────────────┘                    └───────────────────────────┘
```

---

## ⚡ Core Features

- **🚀 Ultra-Fast Reasoning (< 2.8s):** Powered by Groq's LPU inference engine running `llama-3.3-70b-versatile`, enabling dynamic multi-tool reasoning chains without latency degradation.
- **🛡️ Defense-in-Depth RBAC Guardrails:** The dedicated AI user (`USR_FDE_RO`) is granted `SELECT` access exclusively on sanitized views (`FDE_VIEWS.VW_ACTIVE_FLEET`) with explicit `DENY` permissions on raw base tables (`dbo.TBL_SC_FLEET_HIST_RAW`).
- **🔍 Semantic Vector Knowledge Base:** SOP documents are indexed into Pinecone using `BAAI/bge-m3` (1024-dimensional dense embeddings), ensuring precise retrieval of Tier 1 (Advisory), Tier 2 (Warning), and Tier 3 (Critical Spoilage) remediation protocols.
- **🌐 Real-Time Corridor Hazard Indexing:** Automatically samples external environmental parameters (temperature spikes, road congestion, storm fronts) via Open-Meteo to distinguish between reefer cooling failures and ambient heatwaves.
- **📊 Subsystem Diagnostic Benchmarks:** Integrated self-testing suite verifying all 5 platform endpoints with automated latency benchmarking and pass/fail status cards.
- **📜 Immutable Audit Trail:** Every agent invocation, tool call, query parameter, and response payload is recorded in `FDE_VIEWS.AgentAuditLog` with unique session tokens.

---

## 📂 Repository Structure

```
CryoTrace/
├── .github/
│   └── workflows/
│       └── deploy.yml              # Automated CI/CD deployment pipeline to AWS EC2
├── .streamlit/
│   └── config.toml                 # Dark-mode theme & server configuration
├── data/
│   ├── cache/                      # Ingestion hash caches for incremental indexing
│   ├── policy/
│   │   └── Cold_Chain_Incident_SOP_v2.md  # Standard Operating Procedures & escalation rules
│   ├── raw/
│   │   └── dynamic_supply_chain_logistics_dataset.csv # 32,065-row telemetry dataset
│   └── source/
│       └── data.txt                # Dataset attribution & source link
├── scripts/
│   ├── ingest_legacy_data.py       # ETL pipeline reverse-engineering legacy columns into MSSQL
│   ├── ingest_sop_pinecone.py      # BGE-M3 vector chunking & Pinecone index ingestion
│   └── setup_security_and_view.sql # RBAC schemas, secure views, and DENY guardrails
├── src/
│   ├── prompts/
│   │   └── system_prompt.txt       # Structured dispatch agent system prompt
│   ├── agent_tools.py              # Typed LangChain enterprise tools (DB, Weather, SOP)
│   ├── orchestrator.py             # LangGraph ReAct StateGraph orchestrator
│   └── ui.py                       # Glassmorphic Streamlit command center UI
├── .env.example                    # Environment variable configuration template
├── .gitignore                      # Git exclusion rules (secrets, virtualenv, docs)
├── requirements.txt                # Python package dependencies
└── README.md                       # Comprehensive platform documentation
```

---

## 🛠️ Tech Stack Breakdown

| Layer | Technology | Specification / Usage |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit 1.40+ | Glassmorphic Dark UI, interactive telemetry, prompt chips, diagnostic cards |
| **Agent Orchestration** | LangGraph & LangChain Core | Cyclic ReAct graph (`StateGraph`), ToolNode, MemorySaver session persistence |
| **Foundation Model** | Groq LPU (`llama-3.3-70b`) | Primary reasoning brain with sub-3s multi-tool execution latency |
| **Vector Database** | Pinecone Serverless | `fde-sop-index-local`, 1024 dimensions, Cosine metric |
| **Embeddings** | BAAI/bge-m3 | Multilingual dense semantic embeddings |
| **Relational Database** | Microsoft SQL Server 2022 | Dockerized engine, 32,065 records, clustered indexing on coordinates |
| **Database Security** | T-SQL RBAC & Views | `FDE_VIEWS` schema, `VW_ACTIVE_FLEET` view, `USR_FDE_RO` DENY policies |
| **External Weather API**| Open-Meteo REST API | Global forecast & hazard disruption index without API key limits |
| **Container & Cloud** | Docker & AWS EC2 | `t2.micro` host (Ubuntu 22.04 LTS), GitHub Actions CI/CD via SSH |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python 3.12+**
- **Docker Desktop** (or Docker Engine on Linux)
- **ODBC Driver 18 for SQL Server** ([Download Guide](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server))
- Free API keys from [Groq](https://console.groq.com/) and [Pinecone](https://app.pinecone.io/)

---

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/Janani-N14/CryoTrace.git
cd CryoTrace

# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 3. Spin up Microsoft SQL Server 2022 (Docker)
```bash
docker run -e "ACCEPT_EULA=Y" \
           -e "MSSQL_SA_PASSWORD=FdeEnterprisePass123!" \
           -p 1433:1433 \
           --name cryotrace-mssql \
           -d mcr.microsoft.com/mssql/server:2022-latest
```

---

### 4. Configure Environment Variables
Copy the template and configure your API keys:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
SQL_SERVER_HOST=localhost
SQL_SERVER_PORT=1433
SQL_ADMIN_USER=sa
SQL_ADMIN_PASSWORD=FdeEnterprisePass123!
SQL_AGENT_USER=USR_FDE_RO
SQL_AGENT_PASSWORD=AgentPassword2026!

# Pinecone Vector DB Key
PINECONE_API_KEY=pcsk_your_pinecone_key_here

# Groq LLM Key
Agent_llm=GROQ
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

---

### 5. Ingest Telemetry Data, Security Policies & Vector SOPs

Execute the three-stage ingestion pipeline:

```bash
# Stage 1: Bulk ingest 32,065 telemetry records into raw tables
python scripts/ingest_legacy_data.py

# Stage 2: Create RBAC user, secure view, and DENY policies
# Run scripts/setup_security_and_view.sql via your preferred SQL client or sqlcmd:
sqlcmd -S localhost,1433 -U sa -P "FdeEnterprisePass123!" -i scripts/setup_security_and_view.sql

# Stage 3: Generate dense embeddings and populate Pinecone vector index
python scripts/ingest_sop_pinecone.py
```

---

### 6. Launch the Command Center
```bash
streamlit run src/ui.py --server.port=8501
```

Access the dashboard at **`http://localhost:8501`**.

---

## 🧪 Subsystem Diagnostic Benchmark

CryoTrace includes a self-testing diagnostic benchmark suite accessible directly from the **Endpoint Health & Diagnostics** tab:

| Subsystem Endpoint | Architectural Role | Verification Test | Benchmark Metric | Status |
| :--- | :--- | :--- | :--- | :---: |
| **MSSQL Telemetry View** | Relational Data Querying | SELECT COUNT(*) on `FDE_VIEWS.VW_ACTIVE_FLEET` | 32,065 Rows (< 5 ms) | `PASS` |
| **RBAC Security Guardrail**| Mutation & Hallucination Defense | SELECT query as `USR_FDE_RO` on `dbo.Raw` | Access Correctly Denied (< 2 ms) | `PASS` |
| **Open-Meteo Weather API** | Real-Time Transit Risk | HTTPS REST GET on Lat/Lon Coordinates | Live Meteorological Index (< 190 ms) | `PASS` |
| **Pinecone Vector DB** | Semantic Compliance RAG | Dense vector query on `fde-sop-index-local` | Cosine Similarity > 0.82 (< 210 ms) | `PASS` |
| **Groq LLM Reasoner** | Multi-Tool Agent Orchestration | Handshake probe on `llama-3.3-70b-versatile` | Complete ReAct Cycle (< 2.8 s) | `PASS` |

---

## ☁️ Production Deployment (AWS EC2 & CI/CD)

1. **Host Provisioning:** Launch an AWS EC2 `t2.micro` Ubuntu 22.04 LTS instance (AWS Free Tier eligible).
2. **Security Groups:** Configure inbound rules for TCP ports `8501` (Streamlit), `1433` (MSSQL), and `22` (SSH).
3. **CI/CD Automation:** The `.github/workflows/deploy.yml` pipeline automatically deploys code updates to EC2 upon every push to `main` using GitHub Actions Secrets:
   - `EC2_HOST`: Elastic IP address of the EC2 instance
   - `EC2_USER`: `ubuntu`
   - `EC2_SSH_KEY`: Private SSH identity key

---

## 🔒 Security & Compliance

- **Zero Credential Exposure:** All credentials are dynamically loaded via environment variables and excluded from version control.
- **Tamper-Proof Audit Logging:** Every agent decision and tool interaction is recorded in `FDE_VIEWS.AgentAuditLog` with session UUIDs.
- **Data Minimization:** Raw 26-column legacy tables are shielded behind a 15-column curated semantic view.
- **Hallucination Prevention:** The database engine rejects any non-SELECT SQL commands generated by the AI agent.

---

## 📄 License & Attribution

Distributed under the **MIT License**. Developed as an engineering mini-project by **Janani N** ([@Janani-N14](https://github.com/Janani-N14)).
Dataset provided by [Kaggle Dynamic Supply Chain Logistics Dataset](https://www.kaggle.com/datasets/datasetengineer/logistics-and-supply-chain-dataset).
