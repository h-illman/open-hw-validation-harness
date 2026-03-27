# Getting Started

This guide covers installation, setup, and running your first validation.

---

## 1. Prerequisites

### WSL2 (Windows users)
Verilator does not run on native Windows. Install WSL2 with Ubuntu from the
Microsoft Store, then follow the Linux instructions below. Your project files
on your D: drive are accessible inside WSL at `/mnt/d/`.

### Python 3.10+
```bash
sudo apt install python3 python3-venv python3-full -y
```

### Virtual environment (one-time setup)
The venv must live in the Linux filesystem, not on the Windows drive:
```bash
python3 -m venv ~/hwvenv
source ~/hwvenv/bin/activate
```

Add to `~/.bashrc` so it activates automatically:
```bash
echo 'source ~/hwvenv/bin/activate' >> ~/.bashrc
```

### Install Python dependencies
```bash
cd /path/to/open-hw-validation-harness
pip install -r requirements.txt
```

This installs: `cocotb`, `pytest`, `pyyaml`.

### Verilator 5.036 (build from source)
The apt repository version is too old. Build from source:
```bash
sudo apt install -y git perl make autoconf g++ flex bison ccache help2man \
    libgoogle-perftools-dev numactl libfl2 libfl-dev zlib1g zlib1g-dev

git clone https://github.com/verilator/verilator
cd verilator && git checkout v5.036
autoconf && ./configure
make -j$(nproc)
sudo make install
cd .. && rm -rf verilator
verilator --version   # should print 5.036
```

### GTKWave (optional, for waveform viewing)
```bash
sudo apt install gtkwave -y
```

---

## 2. Verify your setup

```bash
source ~/hwvenv/bin/activate
verilator --version          # Verilator 5.036
make --version               # GNU Make 4.x
python -c "import cocotb; print(cocotb.__version__)"   # 2.x
python -c "import yaml; print('yaml ok')"
```

Then check the framework can discover projects:
```bash
cd /path/to/open-hw-validation-harness
python scripts/run_regression.py --list
```

Expected output:
```
Discovered 2 project(s):

  periph_ctrl          Phase 3  —  Phase 3 MVP: register-mapped peripheral...
  reg8                 Phase 2  —  Phase 2 bring-up example: 8-bit register...
```

---

## 3. Run the example projects

### Run all projects
```bash
python scripts/run_regression.py
```

### Run one project
```bash
python scripts/run_regression.py --project periph_ctrl
python scripts/run_regression.py --project reg8
```

### Run a project directly with make
```bash
cd projects/periph_ctrl/sim
make
make copy-waves
```

---

## 4. View waveforms

After any simulation run:
```bash
gtkwave artifacts/waves/dump.vcd
```

In GTKWave: expand the DUT in the left panel, drag signals to the wave view,
press `Ctrl+Shift+E` to fit the view.

---

## 5. Add your own design

See **[docs/adding_a_project.md](adding_a_project.md)** for the full guide.

Short version:
```bash
cp -r projects/template projects/my_design
# Add RTL, write tests, edit project.yaml and Makefile
python scripts/run_regression.py --project my_design
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `cocotb-config: not found` | Activate your venv: `source ~/hwvenv/bin/activate` |
| `verilator: not found` | Build Verilator from source (see above) |
| `No module named 'yaml'` | `pip install pyyaml` |
| No VCD in `artifacts/waves/` | Run `make copy-waves` from `projects/<name>/sim/` |
| Project not in `--list` | Check `projects/<name>/project.yaml` exists and has valid `name:` |
| Verilator version error | You need 5.036+; `apt install verilator` gives an older version |
