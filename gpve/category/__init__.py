"""Category theory module initialization"""
from .morphisms import (
    ProofCategory, 
    Object, 
    Morphism, 
    TwoMorphisms,
    Functor,
    NaturalTransformation,
    ThinCategory,
    EnrichedCategory
)
from .higher_morphisms import HigherCategory, HomotopyCategory, ThreeMorphism

__all__ = [
    "ProofCategory",
    "Object",
    "Morphism",
    "TwoMorphisms",
    "Functor",
    "NaturalTransformation",
    "ThinCategory",
    "EnrichedCategory",
    "HigherCategory",
    "HomotopyCategory",
    "ThreeMorphism",
]
