"""Category-Theoretic Engine - Morphisms and higher morphisms"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Callable, TypeVar, Generic
from abc import ABC, abstractmethod
from enum import Enum
import uuid


T = TypeVar('T')
U = TypeVar('U')


class Category(ABC, Generic[T]):
    """Abstract category"""
    
    @abstractmethod
    def objects(self) -> Set[T]:
        pass
    
    @abstractmethod
    def morphisms(self, a: T, b: T) -> List["Morphism[T]"]:
        pass
    
    @abstractmethod
    def compose(self, f: "Morphism[T]", g: "Morphism[T]") -> "Morphism[T]":
        pass
    
    @abstractmethod
    def identity(self, a: T) -> "Morphism[T]":
        pass


@dataclass
class Morphism:
    """A morphism (arrow) between objects"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = ""
    target: str = ""
    name: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)
    
    def __repr__(self):
        return f"{self.name}: {self.source} → {self.target}"


@dataclass
class Object:
    """An object in a category"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)
    
    def __repr__(self):
        return self.name


@dataclass
class TwoMorphisms:
    """
    A 2-morphism - a morphism between morphisms (natural transformation)
    
    In proof theory:
    - Objects = propositions
    - Morphisms = proofs
    - 2-morphisms = proof equivalences / rewrites
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = ""  # Morphism ID
    target: str = ""  # Morphism ID
    name: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


class ProofCategory:
    """
    Category where:
    - Objects = propositions/statements
    - Morphisms = proofs
    - 2-morphisms = proof equivalences
    """
    
    def __init__(self, name: str = "Proof"):
        self.name = name
        self.objects: Dict[str, Object] = {}
        self.morphisms: Dict[str, Morphism] = {}
        self.morphism_composition: Dict[str, List[str]] = {}  # morpism_id -> [premise_ids]
        self.two_morphisms: Dict[str, TwoMorphisms] = {}
    
    def add_object(self, name: str, **data) -> Object:
        """Add an object (proposition)"""
        obj = Object(name=name, data=data)
        self.objects[name] = obj
        return obj
    
    def add_morphism(self, source: str, target: str, name: str = "", 
                     **data) -> Morphism:
        """Add a morphism (proof)"""
        if source not in self.objects:
            self.add_object(source)
        if target not in self.objects:
            self.add_object(target)
        
        morphism = Morphism(source=source, target=target, name=name, data=data)
        self.morphisms[morphism.id] = morphism
        return morphism
    
    def add_two_morphism(self, source_morph: str, target_morph: str, 
                         name: str = "", **data) -> TwoMorphisms:
        """Add a 2-morphism (proof equivalence)"""
        two_morph = TwoMorphisms(
            source=source_morph, 
            target=target_morph, 
            name=name,
            data=data
        )
        self.two_morphisms[two_morph.id] = two_morph
        return two_morph
    
    def compose(self, f: Morphism, g: Morphism) -> Optional[Morphism]:
        """Compose morphisms (compose proofs)"""
        if f.target != g.source:
            return None
        
        # Create composite morphism
        composite = Morphism(
            source=f.source,
            target=g.target,
            name=f"{f.name} ∘ {g.name}"
        )
        self.morphisms[composite.id] = composite
        self.morphism_composition[composite.id] = [f.id, g.id]
        
        return composite
    
    def identity(self, obj: Object) -> Morphism:
        """Identity morphism for an object"""
        morph = Morphism(source=obj.name, target=obj.name, name=f"id_{obj.name}")
        self.morphisms[morph.id] = morph
        return morph
    
    def get_proofs(self, premise: str, conclusion: str) -> List[Morphism]:
        """Get all proofs from premise to conclusion"""
        return [m for m in self.morphisms.values() 
                if m.source == premise and m.target == conclusion]
    
    def get_equivalences(self, proof1: str, proof2: str) -> List[TwoMorphisms]:
        """Get all equivalences between two proofs"""
        return [t for t in self.two_morphisms.values()
                if t.source == proof1 and t.target == proof2]
    
    def hom(self, a: str, b: str) -> List[Morphism]:
        """Get the hom-set (all morphisms from a to b)"""
        return self.get_proofs(a, b)
    
    def is_isomorphic(self, a: str, b: str) -> bool:
        """Check if two objects are isomorphic"""
        # Has morphisms in both directions
        forward = self.get_proofs(a, b)
        backward = self.get_proofs(b, a)
        return bool(forward) and bool(backward)
    
    def __repr__(self):
        return f"ProofCategory({self.name}, objects={len(self.objects)}, morphisms={len(self.morphisms)})"


class Functor(ABC):
    """A functor between categories"""
    
    @abstractmethod
    def map_object(self, obj: Object) -> Object:
        pass
    
    @abstractmethod
    def map_morphism(self, morph: Morphism) -> Morphism:
        pass


class NaturalTransformation:
    """Natural transformation between functors"""
    
    def __init__(self, source_functor: Functor, target_functor: Functor):
        self.source = source_functor
        self.target = target_functor
        self.components: Dict[str, Morphism] = {}
    
    def add_component(self, obj: Object, morph: Morphism) -> None:
        """Add a component for an object"""
        self.components[obj.id] = morph


# Specialized categories for proof theory

class ThinCategory(ProofCategory):
    """Thin category (at most one morphism between any two objects)"""
    
    def add_morphism(self, source: str, target: str, name: str = "", **data) -> Morphism:
        # Check if morphism already exists
        existing = self.get_proofs(source, target)
        if existing:
            return existing[0]
        return super().add_morphism(source, target, name, **data)


class EnrichedCategory(ProofCategory):
    """Category enriched over another category (e.g., proof complexity)"""
    
    def __init__(self, name: str = "EnrichedProof"):
        super().__init__(name)
        self.morphism_weights: Dict[str, float] = {}  # Weight/complexity
    
    def set_weight(self, morph_id: str, weight: float) -> None:
        """Set weight (complexity) of a morphism"""
        self.morphism_weights[morph_id] = weight
    
    def get_weight(self, morph_id: str) -> float:
        """Get weight of a morphism"""
        return self.morphism_weights.get(morph_id, 1.0)
    
    def find_shortest_proof(self, premise: str, conclusion: str) -> Optional[Morphism]:
        """Find shortest (least weight) proof"""
        proofs = self.get_proofs(premise, conclusion)
        if not proofs:
            return None
        return min(proofs, key=lambda p: self.get_weight(p.id))
