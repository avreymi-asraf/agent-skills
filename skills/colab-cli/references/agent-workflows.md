# Google Colab CLI: Agent Automation Workflows & Best Practices

This guide covers patterns for autonomous agents and automated pipelines using the Google Colab CLI.

---

## 1. Ephemeral Task Execution (Fire-and-Forget)

For automated pipelines (e.g. running evaluations, synthetic data generation, or training jobs), use `colab run`. It provisions a remote VM, installs dependencies, executes the job, streams logs back to stdout/stderr, and immediately deallocates the instance to avoid compute charges.

### Pattern: Self-Contained Batch Job
```bash
# 1. Run job with specified accelerator
colab run --gpu A100 batch_eval.py

# 2. Check exit code: colab run propagates the script's exit status
if [ $? -ne 0 ]; then
  echo "Job failed on remote Colab instance"
fi
```

### Self-Bundling Remote Script
In agent workflows, create a standalone execution script that installs requirements and outputs artifacts to a known directory:

```python
# run_agent_job.py
import subprocess
import sys

def setup():
    subprocess.check_call(["uv", "pip", "install", "--system", "-q", "torch", "transformers", "datasets"])

if __name__ == "__main__":
    setup()
    import torch
    print("CUDA available:", torch.cuda.is_available())
    # Perform evaluation/training here...
```

Run directly:
```bash
colab run --gpu L4 run_agent_job.py
```

---

## 2. Persistent Iterative Experimentation Workflow

When an agent needs to perform multiple iterative actions (e.g. uploading datasets, testing several variations in a REPL, probing intermediate layer weights), use a named persistent session.

### Lifecycle Pattern:
1. **Provision Session**:
   ```bash
   colab new --session agent-exp-01 --gpu T4
   ```
2. **Upload Assets**:
   ```bash
   tar czf dataset.tgz -C ./local_dataset . && colab upload -s agent-exp-01 dataset.tgz /content/dataset.tgz   # upload takes files, not dirs; untar on the VM
   ```
3. **Execute Iterations**:
   ```bash
   # First iteration: install dependencies with uv
   colab install -s agent-exp-01 -r /content/dataset/requirements.txt

   # Second iteration: run phase 1
   colab exec -s agent-exp-01 -f phase1_probe.py

   # Third iteration: run phase 2 (reuses phase 1 state in memory if needed)
   colab exec -s agent-exp-01 -f phase2_prune.py
   ```
4. **Retrieve Results**:
   ```bash
   colab download -s agent-exp-01 /content/results ./local_results
   ```
5. **Always Clean Up / Deallocate**:
   ```bash
   colab stop agent-exp-01
   ```

> **IMPORTANT**: In agent workflows, always implement a `try...finally` or cleanup trap in bash scripts to ensure `colab stop <session>` is called, even on failure or unexpected termination.

---

## 3. Interactive Notebook Cell Execution & In-Memory Probing

When an agent needs to test a Jupyter notebook or run exploratory code iteratively:

### Pattern: Live Cell Execution & In-Memory Probing
1. **Provision persistent session**:
   ```bash
   colab new -s agent-probe --gpu T4
   ```
2. **Execute Full Notebook against Persistent Kernel**:
   `colab exec` can take whole `.ipynb` files directly, run every cell sequentially, format markdown tables/outputs in terminal streams, and write out the executed notebook:
   ```bash
   colab exec -s agent-probe -f notebooks/01_explore_pruning.ipynb --timeout 300
   ```
   > **Note on Timeouts**: The default timeout for `colab exec` is `30.0` seconds. For tasks making LLM API calls or dataset downloads, always specify `--timeout 300` or higher.

3. **Ad-hoc REPL In-Memory Probing**:
   Because the kernel is persistent, all variables (datasets, models, traces) stay in remote GPU memory. An agent can immediately run one-liners or interactive verification blocks without re-running data ingestion:
   ```bash
   cat << 'EOF' | colab exec -s agent-probe
   # Probe variables created in earlier cells:
   print("In-memory dataset count:", len(hf_dataset))
   print("Sample target continuation:", hf_dataset[0]["target_y"])
   EOF
   ```

4. **Connect Web UI for User Inspection**:
   ```bash
   colab url -s agent-probe --open
   ```

---

## 4. Automation Script Template (Bash Trap for Cleanup)

```bash
#!/usr/bin/env bash
set -euo pipefail

SESSION_NAME="agent-run-$(date +%s)"
ACCELERATOR="T4"

cleanup() {
    echo "Deallocating Colab instance: $SESSION_NAME..."
    colab stop "$SESSION_NAME" || true
}
trap cleanup EXIT

echo "Provisioning session $SESSION_NAME with GPU $ACCELERATOR..."
colab new -s "$SESSION_NAME" --gpu "$ACCELERATOR"

echo "Uploading files..."
tar czf src.tgz src && colab upload -s "$SESSION_NAME" src.tgz /content/src.tgz   # then untar on the VM

echo "Executing job..."
colab exec -s "$SESSION_NAME" "python /content/src/main.py"

echo "Downloading results..."
colab download -s "$SESSION_NAME" /content/output ./output

echo "Job completed successfully."
```

---

## 4. Troubleshooting Agent Execution

| Symptom | Root Cause | Fix |
|---|---|---|
| `QuotaExceeded` / `ResourceExhausted` | GPU tier quota is depleted or unavailable | Fallback to `--gpu T4` or run standard CPU |
| Session left running indefinitely | No teardown trap on script crash | Wrap in `trap cleanup EXIT` or use `colab run` |
| Missing files in remote session | Remote path assumed local current directory | All remote files reside under `/content/` |
| `OAuth Error: No browser detected` | Headless server cannot open local OAuth URL | Use `colab auth login --auth=adc` or pre-authenticate session |
