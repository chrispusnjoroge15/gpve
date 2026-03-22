# GPVE - Geometric Proof & Verification Engine

A multi-AI theorem prover integrating SMT solving, type theory, homotopy type theory, and geometric reasoning.

## Architecture

```
Layer 6: AI Exploration (Gemini, DeepSeek, ChatGPT)
Layer 5: Geometric Proof Space
Layer 4: Higher Category Reasoning
Layer 3: Sheaf-based Modular Reasoning  
Layer 2: Type-theoretic Logical Core
Layer 1: SMT / Symbolic Solving (Z3)
```

## Features

- **SMT Solving** - Z3 integration for constraint solving
- **Proof Graphs** - Directed acyclic graphs representing proofs
- **Type Theory** - Dependent types and proof kernel
- **Geometric Reasoning** - Simplicial complexes, homotopy detection
- **Category Theory** - Morphisms, 2-morphisms, higher categories
- **Sheaf Theory** - Modular proof reasoning
- **Multi-AI Orchestration** - Gemini, DeepSeek, ChatGPT

## Installation

```bash
cd gpve
pip install -r requirements.txt
```

Set API keys (optional for local SMT mode):
```bash
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export DEEPSEEK_API_KEY="your-key"
```

## Usage

```bash
# Run SMT demo
python -m gpve.cli smt

# Create proof graph
python -m gpve.cli proof

# Run proof kernel
python -m gpve.cli kernel

# Analyze topology
python -m gpve.cli topology

# Query AIs
python -m gpve.cli ai "What is 2+2?"

# Compare AIs
python -m gpve.cli compare "Explain quantum computing"

# Interactive mode
python -m gpve.cli interactive
```

## Project Structure

```
gpve/
├── gpve/
│   ├── core/          # SMT solver, proof graph, proof kernel
│   ├── geometric/     # Simplicial complexes, homotopy
│   ├── category/      # Category theory, morphisms
│   ├── sheaf/         # Sheaf structures, gluing
│   ├── ai/            # Multi-AI orchestration
│   └── cli.py         # Command-line interface
├── requirements.txt
└── pyproject.toml
```

## Documentation

See GPVE design document for full architecture details.
