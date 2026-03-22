"""Topological Proof Engine - Geometric reasoning about proofs"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Callable
from enum import Enum
import uuid

from .simplicial_complex import SimplicialComplex, Simplex
from .homotopy import HomotopyDetector, HomotopyClass


class ProofSpaceType(Enum):
    """Types of proof spaces"""
    DISCRETE = "discrete"           # Finite discrete topology
    FINITE = "finite"                # Finite topological space
    CW = "cw"                        # CW complex
    SIMPLICIAL = "simplicial"       # Simplicial set


@dataclass
class Path:
    """A path in the proof space"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    vertices: List[str] = field(default_factory=list)
    edges: List[tuple] = field(default_factory=list)
    homotopy_class: Optional[str] = None
    
    def __repr__(self):
        return f"Path({' → '.join(self.vertices[:3])}{'...' if len(self.vertices) > 3 else ''})"


@dataclass  
class ProofSpace:
    """
    A topological space representing the proof landscape.
    
    The space consists of:
    - Points: logical statements
    - Paths: chains of inference
    - Homotopy classes: equivalent proof strategies
    """
    name: str
    space_type: ProofSpaceType = ProofSpaceType.DISCRETE
    vertices: Set[str] = field(default_factory=set)
    edges: Set[tuple] = field(default_factory=set)
    paths: Dict[str, Path] = field(default_factory=dict)
    homotopy_classes: Dict[str, HomotopyClass] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_vertex(self, statement: str) -> str:
        """Add a vertex (statement) to the proof space"""
        self.vertices.add(statement)
        return statement
    
    def add_edge(self, source: str, target: str) -> None:
        """Add an edge (inference) to the proof space"""
        self.edges.add((source, target))
    
    def create_path(self, vertices: List[str]) -> Path:
        """Create a path through the proof space"""
        path = Path(vertices=vertices)
        
        # Create edges from vertices
        for i in range(len(vertices) - 1):
            path.edges.append((vertices[i], vertices[i+1]))
        
        self.paths[path.id] = path
        return path
    
    def compute_homotopy(self) -> Dict[str, HomotopyClass]:
        """Compute homotopy classes of paths"""
        detector = HomotopyDetector()
        
        # Add edges
        for source, target in self.edges:
            detector.add_edge(source, target)
        
        # Find paths between all pairs of vertices
        for v1 in self.vertices:
            for v2 in self.vertices:
                if v1 != v2:
                    classes = detector.compute_homotopy_classes(v1, v2)
                    for cls in classes:
                        self.homotopy_classes[cls.id] = cls
        
        return self.homotopy_classes
    
    def get_proof_space(self, start: str, end: str) -> List[Path]:
        """Get all proof paths from start to end"""
        return [p for p in self.paths.values() 
                if p.vertices and p.vertices[0] == start and p.vertices[-1] == end]


class TopologicalProofEngine:
    """
    Engine for topological reasoning about proofs.
    
    Capabilities:
    - Build proof spaces from proof graphs
    - Detect equivalent proofs via homotopy
    - Analyze proof topology (connected components, holes)
    - Find optimal proof paths
    """
    
    def __init__(self):
        self.spaces: Dict[str, ProofSpace] = {}
        self.current_space: Optional[ProofSpace] = None
    
    def build_proof_space(self, proof_graph, name: str = "proof_space") -> ProofSpace:
        """Build a topological proof space from a proof graph"""
        space = ProofSpace(name=name)
        
        # Add vertices
        for vid, vertex in proof_graph.vertices.items():
            space.add_vertex(vertex.statement)
        
        # Add edges
        for edge in proof_graph.edges.values():
            source_stmt = proof_graph.vertices[edge.source].statement
            target_stmt = proof_graph.vertices[edge.target].statement
            space.add_edge(source_stmt, target_stmt)
        
        # Compute homotopy
        space.compute_homotopy()
        
        self.spaces[name] = space
        self.current_space = space
        return space
    
    def find_proofs(self, premise: str, conclusion: str) -> List[Path]:
        """Find all proof paths from premise to conclusion"""
        if self.current_space:
            return self.current_space.get_proof_space(premise, conclusion)
        return []
    
    def find_shortest_proof(self, premise: str, conclusion: str) -> Optional[Path]:
        """Find the shortest proof path"""
        proofs = self.find_proofs(premise, conclusion)
        if not proofs:
            return None
        return min(proofs, key=lambda p: len(p.vertices))
    
    def find_simplest_proof(self, premise: str, conclusion: str) -> Optional[Path]:
        """Find the simplest (least complex) proof"""
        proofs = self.find_proofs(premise, conclusion)
        if not proofs:
            return None
        
        # Simplest = shortest
        return min(proofs, key=lambda p: len(p.edges))
    
    def get_equivalent_proofs(self, path: Path) -> List[Path]:
        """Get all proofs equivalent to the given path"""
        if not self.current_space:
            return []
        
        equiv = []
        for p in self.current_space.paths.values():
            if p.id != path.id and p.vertices == path.vertices:
                equiv.append(p)
        
        return equiv
    
    def analyze_topology(self, space_name: str) -> Dict[str, Any]:
        """Analyze the topology of a proof space"""
        space = self.spaces.get(space_name)
        if not space:
            return {}
        
        # Build adjacency for analysis
        adjacency = {v: set() for v in space.vertices}
        for s, t in space.edges:
            if s in adjacency and t in adjacency:
                adjacency[s].add(t)
        
        # Find connected components
        visited = set()
        components = []
        
        def dfs(v, component):
            visited.add(v)
            component.append(v)
            for neighbor in adjacency.get(v, []):
                if neighbor not in visited:
                    dfs(neighbor, component)
        
        for v in space.vertices:
            if v not in visited:
                component = []
                dfs(v, component)
                components.append(component)
        
        return {
            "num_vertices": len(space.vertices),
            "num_edges": len(space.edges),
            "num_components": len(components),
            "components": components,
            "num_homotopy_classes": len(space.homotopy_classes),
            "num_paths": len(space.paths),
        }
    
    def compare_proofs(self, path1: Path, path2: Path) -> Dict[str, Any]:
        """Compare two proof paths"""
        return {
            "same_vertices": path1.vertices == path2.vertices,
            "same_edges": path1.edges == path2.edges,
            "length_difference": abs(len(path1.edges) - len(path2.edges)),
            "homotopy_equivalent": path1.homotopy_class == path2.homotopy_class 
                                   if path1.homotopy_class and path2.homotopy_class 
                                   else False,
        }
    
    def __repr__(self):
        return f"TopologicalProofEngine(spaces={len(self.spaces)})"
