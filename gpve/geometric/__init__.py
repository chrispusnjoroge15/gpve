"""Geometric module initialization"""
from .simplicial_complex import SimplicialComplex, Simplex, create_proof_complex
from .homotopy import HomotopyDetector, HomotopyClass, PersistentHomology
from .topological_proof import TopologicalProofEngine, ProofSpace, Path, ProofSpaceType

__all__ = [
    "SimplicialComplex",
    "Simplex", 
    "create_proof_complex",
    "HomotopyDetector",
    "HomotopyClass",
    "PersistentHomology",
    "TopologicalProofEngine",
    "ProofSpace",
    "Path",
    "ProofSpaceType",
]
