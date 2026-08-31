# FINCTRL AI — Setup and Installation Guide

## System Requirements
- **OS**: Windows 10/11, macOS, or Linux
- **Python**: 3.11 or higher
- **RAM**: Minimum 8 GB (16 GB recommended)
- **Local AI Runtime**: Ollama (Optional, fallback provided if offline)

## Quick Start (Local Setup)

1. **Clone/Navigate to Project Repository**:
   ```bash
   cd c:/Users/yashw/Music/Bobby
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Install Local AI Model via Ollama**:
   ```bash
   ollama pull llama3.2:3b
   ```

4. **Generate Demo & Benchmark Datasets**:
   ```bash
   python scripts/generate_dataset.py
   ```

5. **Launch the Streamlit Control Room UI**:
   ```bash
   streamlit run app/main.py
   ```

6. **Run Test & Evaluation Suites**:
   ```bash
   pytest
   python scripts/evaluate.py
   ```
