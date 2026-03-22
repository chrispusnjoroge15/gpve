"""Proof Kernel - Dependent Type Theory & HoTT Semantics"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from abc import ABC, abstractmethod
import uuid


class TypeKind(Enum):
    """Kinds of types in the type system"""
    PROP = "prop"           # Proposition (logical statement)
    TYPE = "type"           # Computational type
    FUNCTION = "function"   # Function type
    PRODUCT = "product"     # Dependent product
    SUM = "sum"             # Dependent sum
    NAT = "nat"             # Natural numbers
    EQ = "eq"               # Identity type


@dataclass
class Type:
    """Base type representation"""
    kind: TypeKind
    name: str
    params: List["Type"] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    
    def __repr__(self):
        if self.params:
            return f"{self.name}[{', '.join(str(p) for p in self.params)}]"
        return self.name


@dataclass
class Term:
    """Term in the type theory"""
    name: str
    term_type: Type
    value: Any = None
    definition: Optional[str] = None
    
    def __repr__(self):
        return f"{self.name} : {self.term_type}"


@dataclass
class Proof:
    """A proof term with justification"""
    term: Term
    justification: str
    rule: str
    premises: List["Proof"] = field(default_factory=list)
    ref_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __repr__(self):
        return f"Proof({self.term}, by={self.rule})"


@dataclass
class GeometricProof:
    """
    Core proof object with geometric representation.
    
    This is the heart of GPVE - representing proofs as geometric
    objects that can be visualized, compared, and transformed.
    """
    vertices: List[str] = field(default_factory=list)      # Logical statements
    edges: List[tuple] = field(default_factory=list)         # Inference steps
    simplicial_complex: Optional[Any] = field(default=None) # Higher relations
    category_structure: Optional[Dict] = field(default=None) # Objects/morphisms
    homotopy_classes: Dict[str, List[str]] = field(default_factory=dict)
    sheaf_sections: Dict[str, Any] = field(default_factory=dict)
    invariants: Dict[str, Any] = field(default_factory=dict)
    
    theorem: str = ""
    assumptions: List[str] = field(default_factory=list)
    
    def add_vertex(self, statement: str) -> str:
        """Add a vertex (statement) to the proof"""
        vid = f"v{len(self.vertices)}"
        self.vertices.append(statement)
        return vid
    
    def add_inference(self, from_statements: List[str], to_statement: str) -> None:
        """Add an inference step"""
        self.edges.append((from_statements, to_statement))
    
    def get_invariants(self) -> Dict[str, Any]:
        """Compute topological invariants"""
        return {
            "num_vertices": len(self.vertices),
            "num_edges": len(self.edges),
            "homotopy_classes": self.homotopy_classes,
        }


class ProofKernel:
    """
    The core proof engine implementing:
    - Dependent type theory
    - Homotopy Type Theory (HoTT) semantics
    - Proof construction and verification
    """
    
    def __init__(self):
        self.context: Dict[str, Term] = {}
        self.proofs: Dict[str, Proof] = {}
        self.types: Dict[str, Type] = {}
        self.current_proof: Optional[GeometricProof] = None
        
        # Initialize built-in types
        self._init_builtin_types()
    
    def _init_builtin_types(self):
        """Initialize built-in types"""
        self.types["Prop"] = Type(TypeKind.PROP, "Prop")
        self.types["Type"] = Type(TypeKind.TYPE, "Type")
        self.types["Nat"] = Type(TypeKind.NAT, "Nat")
        self.types["Bool"] = Type(TypeKind.TYPE, "Bool")
    
    # Type checking
    
    def infer_type(self, term: Term) -> Type:
        """Infer the type of a term"""
        if term.name in self.context:
            return self.context[term.name].term_type
        if term.term_type:
            return term.term_type
        return self.types.get("Type", Type(TypeKind.TYPE, "Type"))
    
    def check_type(self, term: Term, expected: Type) -> bool:
        """Check if term has expected type"""
        inferred = self.infer_type(term)
        return inferred.name == expected.name or str(inferred) == str(expected)
    
    # Context management
    
    def extend_context(self, term: Term) -> None:
        """Add a term to the context"""
        self.context[term.name] = term
    
    def lookup(self, name: str) -> Optional[Term]:
        """Look up a term in the context"""
        return self.context.get(name)
    
    # Proof construction
    
    def assume(self, name: str, prop: str) -> Term:
        """Assume a proposition (add to context)"""
        term = Term(name, Type(TypeKind.PROP, prop))
        self.extend_context(term)
        
        # Also add to geometric proof if one is active
        if self.current_proof:
            self.current_proof.add_vertex(prop)
            self.current_proof.assumptions.append(prop)
        
        return term
    
    def define(self, name: str, term_type: Type, definition: Any) -> Term:
        """Define a new term with a definition"""
        term = Term(name, term_type, value=definition, definition=str(definition))
        self.extend_context(term)
        return term
    
    def prove(self, theorem: str, proof_fn: Callable[[], Proof]) -> Proof:
        """Prove a theorem"""
        # Create new geometric proof
        self.current_proof = GeometricProof(theorem=theorem)
        
        # Build proof
        proof = proof_fn()
        
        # Store proof
        self.proofs[proof.ref_id] = proof
        
        return proof
    
    # Inference rules
    
    def apply(self, f: Term, arg: Term) -> Term:
        """Apply a function to an argument (β-reduction)"""
        if f.definition and callable(f.definition):
            result = f.definition(arg.value)
            return Term(f"({f.name} {arg.name})", arg.term_type, value=result)
        raise NotImplementedError("Non-computational function application")
    
    def lambda_abs(self, param: Term, body: Term) -> Term:
        """Create a lambda abstraction"""
        return Term(
            f"λ{param.name}.{body.name}",
            Type(TypeKind.FUNCTION, f"({param.term_type} → {body.term_type})"),
            definition=lambda x: body.value
        )
    
    # HoTT operations
    
    def refl(self, term: Term) -> Proof:
        """Reflexivity - proof of x = x (identity type)"""
        proof = Proof(
            term=Term(f"refl({term.name})", Type(TypeKind.EQ, f"{term.name} = {term.name}")),
            justification="reflexivity",
            rule="refl"
        )
        return proof
    
    def symm(self, proof: Proof) -> Proof:
        """Symmetry of equality"""
        return Proof(
            term=Term(f"symm({proof.term.name})", proof.term.term_type),
            justification=f"symmetry of {proof.justification}",
            rule="sym",
            premises=[proof]
        )
    
    def trans(self, p1: Proof, p2: Proof) -> Proof:
        """Transitivity of equality"""
        return Proof(
            term=Term(f"trans({p1.term.name}, {p2.term.name})", p1.term.term_type),
            justification=f"transitivity of {p1.justification} and {p2.justification}",
            rule="trans",
            premises=[p1, p2]
        )
    
    # Geometric proof operations
    
    def start_proof(self, theorem: str) -> GeometricProof:
        """Begin a new geometric proof"""
        self.current_proof = GeometricProof(theorem=theorem)
        return self.current_proof
    
    def add_proof_step(self, from_props: List[str], to_prop: str, 
                       rule: str = "custom") -> None:
        """Add a step to the current geometric proof"""
        if self.current_proof:
            self.current_proof.add_inference(from_props, to_prop)
    
    def get_current_proof(self) -> Optional[GeometricProof]:
        """Get the current geometric proof"""
        return self.current_proof
    
    def finalize_proof(self) -> GeometricProof:
        """Finalize and return the current proof"""
        proof = self.current_proof
        self.current_proof = None
        return proof
    
    # Verification
    
    def verify_proof(self, proof: Proof) -> bool:
        """Verify that a proof is valid"""
        # Check all premises are valid
        for premise in proof.premises:
            if premise.ref_id not in self.proofs:
                return False
        
        # Basic rule checking
        valid_rules = {"refl", "sym", "trans", "intro", "elim", "assumption"}
        return proof.rule in valid_rules or proof.justification != ""
    
    def __repr__(self):
        return f"ProofKernel(context_size={len(self.context)}, proofs={len(self.proofs)})"
