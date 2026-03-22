"""Higher category theory - 2-categories and beyond"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Callable
from enum import Enum
import uuid

from .morphisms import ProofCategory, Object, Morphism, TwoMorphisms


@dataclass
class ThreeMorphism:
    """
    A 3-morphism - morphism between 2-morphisms
    
    In higher category theory:
    - 0-cells: objects (propositions)
    - 1-cells: morphisms (proofs)
    - 2-cells: 2-morphisms (proof equivalences)
    - 3-cells: 3-morphisms (higher coherences)
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = ""  # 2-morphism ID
    target: str = ""  # 2-morphism ID
    name: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


class HigherCategory(ProofCategory):
    """
    Higher category with morphisms at multiple levels.
    
    Supports:
    - Objects (0-cells)
    - Morphisms (1-cells)
    - 2-morphisms
    - 3-morphisms (and theoretically higher)
    """
    
    def __init__(self, name: str = "HigherProof", dimension: int = 2):
        super().__init__(name)
        self.dimension = dimension
        self.n_morphisms: Dict[int, Dict[str, Any]] = {
            0: {},  # Objects
            1: {},  # Morphisms
            2: {},  # 2-morphisms
        }
        
        if dimension >= 3:
            self.n_morphisms[3] = {}
    
    def add_2_morphism(self, source_morph: str, target_morph: str,
                       name: str = "", **data) -> TwoMorphisms:
        """Add a 2-morphism"""
        two_morph = TwoMorphisms(
            source=source_morph,
            target=target_morph,
            name=name,
            data=data
        )
        self.two_morphisms[two_morph.id] = two_morph
        self.n_morphisms[2][two_morph.id] = two_morph
        return two_morph
    
    def add_3_morphism(self, source_2morph: str, target_2morph: str,
                       name: str = "", **data) -> ThreeMorphism:
        """Add a 3-morphism"""
        if self.dimension < 3:
            raise ValueError("Category dimension too low for 3-morphisms")
        
        three_morph = ThreeMorphism(
            source=source_2morph,
            target=target_2morph,
            name=name,
            data=data
        )
        self.n_morphisms[3][three_morph.id] = three_morph
        return three_morph
    
    def vertical_compose_2morph(self, f: TwoMorphisms, g: TwoMorphisms) -> Optional[TwoMorphisms]:
        """Vertical composition of 2-morphisms"""
        if f.target != g.source:
            return None
        
        composite = TwoMorphisms(
            source=f.source,
            target=g.target,
            name=f"{f.name} • {g.name}"
        )
        self.two_morphisms[composite.id] = composite
        return composite
    
    def horizontal_compose_2morph(self, f: TwoMorphisms, g: TwoMorphisms) -> Optional[TwoMorphisms]:
        """Horizontal composition of 2-morphisms"""
        # Need to find morphisms that f and g operate on
        # This requires more context in a full implementation
        return None
    
    def get_2cell_equivalence(self, morph1: str, morph2: str) -> List[TwoMorphisms]:
        """Get all 2-morphisms showing equivalence between morphisms"""
        equiv = []
        
        for two_m in self.two_morphisms.values():
            if two_m.source == morph1 and two_m.target == morph2:
                equiv.append(two_m)
            # Also check reverse
            if two_m.source == morph2 and two_m.target == morph1:
                equiv.append(two_m)
        
        return equiv
    
    def are_proof_equivalent(self, proof1: str, proof2: str) -> bool:
        """Check if two proofs are equivalent (exists 2-morphism)"""
        return bool(self.get_2cell_equivalence(proof1, proof2))


class HomotopyCategory(HigherCategory):
    """
    Category where morphisms are homotopy classes of paths.
    
    This is relevant for proof equivalence - two proofs are
    equal in the homotopy category if they're homotopic.
    """
    
    def __init__(self, name: str = "HomotopyProof"):
        super().__init__(name, dimension=2)
        self.homotopy_relation: Dict[str, Set[str]] = {}  # morph_id -> set of equivalent morphs
    
    def add_homotopy(self, morph1: str, morph2: str) -> None:
        """Declare two morphisms homotopic (equivalent)"""
        if morph1 not in self.homotopy_relation:
            self.homotopy_relation[morph1] = set()
        if morph2 not in self.homotopy_relation:
            self.homotopy_relation[morph2] = set()
        
        self.homotopy_relation[morph1].add(morph2)
        self.homotopy_relation[morph2].add(morph1)
        
        # Add 2-morphism for this equivalence
        self.add_2_morphism(morph1, morph2, name=f"homotopy_{morph1[:8]}_{morph2[:8]}")
    
    def are_homotopic(self, morph1: str, morph2: str) -> bool:
        """Check if two morphisms are homotopic"""
        return (morph1 in self.homotopy_relation and 
                morph2 in self.homotopy_relation.get(morph1, set()))
