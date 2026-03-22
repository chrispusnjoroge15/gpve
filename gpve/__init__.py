"""GPVE - Geometric Proof & Verification Engine

A multi-AI theorem prover integrating:
- SMT solving (Z3)
- Dependent type theory / HoTT
- Category theory
- Sheaf-based modular reasoning
- Geometric/homotopy reasoning
- AI exploration (Gemini, DeepSeek, ChatGPT)
"""

__version__ = "0.1.0"

from .engine import GPVEEngine, create_engine, VerificationResult, AIExplorationResult
from .core import (
    ProofGraph, SMTSolver, ProofKernel, GeometricProof,
    FunctionalAnalyzer, BinaryAnalyzer
)
from .geometric import (
    SimplicialComplex, TopologicalProofEngine, HomotopyDetector
)
from .category import ProofCategory, HigherCategory
from .sheaf import SheafReasoning, ModularVerifier
from .ai import AIOrchestrator, AIProvider, AIResponse
from .config import GPVEConfig, load_config, save_config, get_api_keys

__all__ = [
    # Version
    "__version__",
    # Engine
    "GPVEEngine",
    "create_engine",
    "VerificationResult",
    "AIExplorationResult",
    # Core
    "ProofGraph",
    "SMTSolver",
    "ProofKernel",
    "GeometricProof",
    "FunctionalAnalyzer",
    "BinaryAnalyzer",
    # Geometric
    "SimplicialComplex",
    "TopologicalProofEngine",
    "HomotopyDetector",
    # Category
    "ProofCategory",
    "HigherCategory",
    # Sheaf
    "SheafReasoning",
    "ModularVerifier",
    # AI
    "AIOrchestrator",
    "AIProvider",
    "AIResponse",
    # Config
    "GPVEConfig",
    "load_config",
    "save_config",
    "get_api_keys",
]
