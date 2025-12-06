# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NVIDIA Hybrid RAG - An NVIDIA AI Workbench application providing a flexible RAG (Retrieval Augmented Generation) system with a Gradio chat interface. Users can chat with their own documents using a Milvus vector database, choosing between multiple inference modes: Cloud (NVIDIA API), Local (GPU via TGI), Microservices (NIM), or Remote NIM.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Gradio Chat UI (Port 8080)                                     │
│  code/chatui/ - FastAPI + Gradio mount                          │
│  └─ pages/converse.py: Main chat interface                      │
│  └─ chat_client.py: HTTP client for backend                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────────────┐
│  Chain Server / RAG Backend (Port 8000)                         │
│  code/chain_server/server.py - FastAPI RAG endpoints            │
│  └─ chains.py: Document ingestion, vector search, RAG execution │
│  └─ nvcf_llm.py: NVIDIA Cloud Functions LLM wrapper             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────▼──────┐   ┌───────▼───────┐   ┌──────▼──────┐
│ Milvus DB   │   │ TGI Local     │   │ NVIDIA API  │
│ Port 19530  │   │ Port 9090     │   │ (Cloud/NIM) │
└─────────────┘   └───────────────┘   └─────────────┘
```

## Key Commands

### Start Backend Services
```bash
# Initialize Milvus + Chain Server (run once)
bash /project/code/scripts/rag-consolidated.sh
```

### Run Applications
```bash
# Start ChatUI (main app)
cd /project/code/ && python -m chatui --port 8080 --host 0.0.0.0

# Start Chain Server directly
cd /project/code/ && python -m uvicorn chain_server.server:app --port=8000 --host='0.0.0.0'
```

### Local Inference Management
```bash
# Download model weights
bash /project/code/scripts/download-local.sh

# Start local TGI server
bash /project/code/scripts/start-local.sh

# Stop local TGI server
bash /project/code/scripts/stop-local.sh
```

### Vector Database Operations
```bash
# Check Milvus health
bash /project/code/scripts/check-database.sh

# Clear all documents from vector DB
bash /project/code/scripts/clear-docs.sh

# Manual document upload
bash /project/code/scripts/upload-docs.sh
```

## Key Configuration Files

- `.project/spec.yaml` - NVIDIA AI Workbench project spec (apps, mounts, secrets)
- `compose.yaml` - Docker Compose for local NIM microservice
- `requirements.txt` - Python dependencies
- `variables.env` - Environment variables (HF cache, embedding device)

## Important Code Locations

### Frontend (code/chatui/)
- `__main__.py` - Entry point, starts uvicorn server
- `pages/converse.py` - Main chat interface (settings, chat, document upload)
- `pages/kb.py` - Knowledge base management
- `chat_client.py` - Backend HTTP client with streaming support
- `configuration.py` - AppConfig dataclass

### Backend (code/chain_server/)
- `server.py` - FastAPI endpoints: `/health`, `/uploadDocument`, `/generate`, `/documentSearch`
- `chains.py` - RAG chain logic: `ingest_docs()`, `rag_chain_streaming()`, `document_search()`
- `nvcf_llm.py` - NVIDIA Cloud Functions LLM interface
- `chat_templates.py` - Prompt templates per model family

### Helper Scripts (code/scripts/)
- `helpers/docs.py` - `DocProcessor` class with file hash caching
- `helpers/upload-docs.py` - CLI document upload
- `helpers/empty-docs.py` - CLI to clear database

## Technical Details

- **Embedding Model**: `intfloat/e5-large-v2` via SentenceTransformers
- **Chunk Size**: 510 tokens, overlap 200
- **Max Context**: 800 tokens
- **Default Output Tokens**: 50
- **Vector DB**: Milvus on port 19530, persistence at `/mnt/milvus/`
- **Model Cache**: `/data/` (HuggingFace Hub cache)

## Environment Notes

- Two separate conda environments: `api-env` (backend) and `ui-env` (frontend)
- Requires `NVIDIA_API_KEY` secret for cloud inference
- GPU required for local inference (CUDA 11.8)
- Build scripts: `preBuild.bash` (system packages), `postBuild.bash` (conda envs + Python deps)
