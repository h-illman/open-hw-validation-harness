# Getting Started

Welcome to the Open Hardware Validation Harness. This guide will help you set up the basic Phase 1 environment.

## 1. Setting Up the Python Environment

We recommend using a Python virtual environment to keep dependencies isolated cleanly. 
From the root of the project, run:

```bash
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

## 2. Installing Dependencies

Install the Phase 1 required packages:

```bash
pip install -r requirements.txt
```

*(Note: In Phase 2, this will be expanded to include HDL simulation tools like cocotb.)*

## 3. Running the Smoke Test

To verify that your environment is correctly configured, run the included basic smoke test:

```bash
pytest tests/test_smoke.py
```

If the test passes, your initial scaffolding is correctly set up.
