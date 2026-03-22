# GPVE - Geometric Proof & Verification Engine

A multi-AI theorem prover integrating SMT solving, type theory, homotopy type theory, and geometric reasoning.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

GPVE combines multiple reasoning paradigms:

```
┌─────────────────────────────────────────────────────┐
│  Layer 6: AI Exploration (Gemini, DeepSeek, GPT)   │
├─────────────────────────────────────────────────────┤
│  Layer 5: Geometric Proof Space                     │
├─────────────────────────────────────────────────────┤
│  Layer 4: Higher Category Theory                   │
├─────────────────────────────────────────────────────┤
│  Layer 3: Sheaf-based Modular Reasoning             │
├─────────────────────────────────────────────────────┤
│  Layer 2: Type-theoretic Logical Core              │
├─────────────────────────────────────────────────────┤
│  Layer 1: SMT / Symbolic Solving (Z3)             │
└─────────────────────────────────────────────────────┘
```

## Features

- **SMT Solving** — Z3 integration for constraint solving
- **Proof Graphs** — Directed acyclic graphs representing proofs
- **Type Theory** — Dependent types and proof kernel (HoTT)
- **Geometric Reasoning** — Simplicial complexes, homotopy detection
- **Category Theory** — Morphisms, 2-morphisms, higher categories
- **Sheaf Theory** — Modular proof reasoning
- **Multi-AI Orchestration** — Gemini, DeepSeek, ChatGPT
- **Visualization** — DOT, Mermaid, JSON, Matplotlib

## Installation

```bash
# Clone the repo
git clone https://github.com/chrispusnjoroge15/gpve.git
cd gpve

# Install dependencies
pip install -r requirements.txt

# Optional: Install matplotlib for advanced visualization
pip install matplotlib
```

## API Keys (Optional)

Set environment variables for AI features:

```bash
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."
export DEEPSEEK_API_KEY="..."
```

The core works without API keys — SMT solving, proof graphs, topology, etc.

## Quick Start

```python
from gpve import create_engine
from gpve.core import ProofGraph

# Create engine
engine = create_engine()

# Build a proof
graph = ProofGraph("demo")
v1 = graph.add_vertex("x > 0")
v2 = graph.add_vertex("y > 0")
v3 = graph.add_vertex("x + y > 0")

graph.add_edge(v1.id, v3.id, rule_name="add_positive")
graph.add_edge(v2.id, v3.id, rule_name="add_positive")

# Verify
result = engine.full_verify("x + y > 0", graph)
print(f"Valid: {result.is_valid}")
```

## Command Line

```bash
# Run full demo
python -m gpve.cli all

# Run SMT solver
python -m gpve.cli smt

# Run tests
python -m gpve.cli test

# Run examples
python -m gpve.cli examples

# Query AI
python -m gpve.cli ai "Prove that sqrt(2) is irrational"

# Visualize proof
python -m gpve.cli visualize

# Check AI status
python -m gpve.cli ai-status
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `gpve all` | Run full demo |
| `gpve verify` | Verify a proof |
| `gpve smt` | Run SMT solver |
| `gpve test` | Run unit tests |
| `gpve examples` | Run example proofs |
| `gpve ai <prompt>` | Query AI providers |
| `gpve ai-status` | Check API keys |
| `gpve visualize` | Visualize proof graph |
| `gpve sheaf` | Sheaf reasoning demo |
| `gpve category` | Category theory demo |
| `gpve topology` | Topology analysis |

## Project Structure

```
gpve/
├── gpve/
│   ├── core/              # SMT, proof graph, kernel
│   │   ├── proof_graph.py
│   │   ├── smt_solver.py
│   │   ├── proof_kernel.py
│   │   ├── functional_analysis.py
│   │   └── reverse_eng.py
│   ├── geometric/         # Topology, homotopy
│   │   ├── simplicial_complex.py
│   │   ├── homotopy.py
│   │   └── topological_proof.py
│   ├── category/          # Category theory
│   │   ├── morphisms.py
│   │   └── higher_morphisms.py
│   ├── sheaf/             # Modular reasoning
│   │   ├── sheaf_structure.py
│   │   └── gluing.py
│   ├── ai/                # Multi-AI orchestration
│   │   └── orchestrator.py
│   ├── engine.py          # Unified engine
│   ├── cli.py             # CLI
│   ├── examples.py        # Examples
│   ├── visualize.py       # Visualization
│   └── config.py          # Configuration
├── tests/                 # Unit tests
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Examples

### SMT Solving
```python
from gpve.core import SMTSolver

solver = SMTSolver()
x = solver.Int("x")
y = solver.Int("y")

solver.assert_formula(x + y == 10)
solver.assert_formula(x > 0)

result = solver.check()
print(result.model)  # {'x': '1', 'y': '9'}
```

### Category Theory
```python
from gpve import create_engine

engine = create_engine()
engine.add_proposition("P")
engine.add_proof_morphism("P", "Q", "f")
```

### AI Exploration
```python
from gpve import create_engine

engine = create_engine()
results = engine.ai_explore("Prove Fermat's Last Theorem")
```

## Testing

```bash
# Run all tests
python -m gpve.cli test

# Or with pytest
pytest tests/ -v
```

## Visualization

GPVE supports multiple output formats:

- **Mermaid** — `gpve visualize -f mermaid`
- **DOT/GraphViz** — `gpve visualize -f dot`
- **JSON** — `gpve visualize -f json`
- **Matplotlib** — Requires `pip install matplotlib`

## Requirements

- Python 3.10+
- z3-solver
- openai
- google-generativeai
- pydantic
- rich

## License

MIT License

## Author

Chrispus Njoroge

## Citation

If you use GPVE in research, please cite:

```bibtex
@software{gpve,
  title = {GPVE - Geometric Proof \& Verification Engine},
  author = {Chrispus Njoroge},
  year = {2026},
  url = {https://github.com/chrispusnjoroge15/gpve}
}
```
