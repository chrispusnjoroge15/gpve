"""Geometric module - Simplicial complexes and topology"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from itertools import combinations
import numpy as np


@dataclass
class Simplex:
    """A geometric simplex (vertex, edge, triangle, tetrahedron, etc.)"""
    vertices: Tuple[int, ...]
    dimension: int = field(init=False)
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.dimension = len(self.vertices) - 1
    
    def __hash__(self):
        return hash(self.vertices)
    
    def __eq__(self, other):
        if not isinstance(other, Simplex):
            return False
        return set(self.vertices) == set(other.vertices)
    
    def faces(self) -> List[Simplex]:
        """Get all proper faces of this simplex"""
        faces = []
        for k in range(len(self.vertices)):
            face_vertices = self.vertices[:k] + self.vertices[k+1:]
            if len(face_vertices) > 0:
                faces.append(Simplex(tuple(sorted(face_vertices))))
        return faces
    
    def boundary(self) -> List[Simplex]:
        """Get the boundary (set of (d-1)-faces)"""
        return self.faces()
    
    def __repr__(self):
        return f"Simplex({self.vertices}, dim={self.dimension})"


class SimplicialComplex:
    """
    A simplicial complex - a collection of simplices closed under faces.
    
    This represents the higher-dimensional structure of proofs,
    where:
    - 0-simplices = statements/vertices
    - 1-simplices = inference steps/edges  
    - 2-simplices = relationships between proofs
    - n-simplices = higher-order relationships
    """
    
    def __init__(self, name: str = "complex"):
        self.name = name
        self.simplices: Set[Simplex] = set()
        self.dimension: int = 0
        
        # Chain groups for homology
        self.chains: Dict[int, List[Simplex]] = {}
    
    def add_simplex(self, vertices: List[int]) -> Simplex:
        """Add a simplex to the complex"""
        simplex = Simplex(tuple(sorted(vertices)))
        
        # Check if we need to add all faces (closed under faces)
        for face in simplex.faces():
            if face not in self.simplices:
                self.simplices.add(face)
        
        self.simplices.add(simplex)
        self._update_dimension()
        return simplex
    
    def add_simplices(self, vertex_lists: List[List[int]]) -> List[Simplex]:
        """Add multiple simplices"""
        return [self.add_simplex(vl) for vl in vertex_lists]
    
    def _update_dimension(self):
        """Update the dimension of the complex"""
        if self.simplices:
            self.dimension = max(s.dimension for s in self.simplices)
    
    def get_simplices_of_dim(self, dim: int) -> List[Simplex]:
        """Get all simplices of a given dimension"""
        return [s for s in self.simplices if s.dimension == dim]
    
    def get_vertices(self) -> List[int]:
        """Get all 0-simplices (vertices)"""
        return [v[0] for v in self.get_simplices_of_dim(0)]
    
    def get_edges(self) -> List[Simplex]:
        """Get all 1-simplices (edges)"""
        return self.get_simplices_of_dim(1)
    
    def get_triangles(self) -> List[Simplex]:
        """Get all 2-simplices (triangles)"""
        return self.get_simplices_of_dim(2)
    
    def is_closed(self) -> bool:
        """Check if the complex is closed (contains all faces)"""
        for simplex in self.simplices:
            for face in simplex.faces():
                if face not in self.simplices:
                    return False
        return True
    
    def is_pure(self) -> bool:
        """Check if it's a pure complex (all maximal simplices same dimension)"""
        max_dim = self.dimension
        max_simplices = [s for s in self.simplices if s.dimension == max_dim]
        return len(set(s.dimension for s in max_simplices)) == 1
    
    def link(self, simplex: Simplex) -> SimplicialComplex:
        """Compute the link of a simplex"""
        link_complex = SimplicialComplex(f"link({simplex.vertices})")
        
        for s in self.simplices:
            if s == simplex:
                continue
            # Check if s and simplex are disjoint
            if set(s.vertices).isdisjoint(set(simplex.vertices)):
                # Check if union is in complex
                union = Simplex(tuple(sorted(s.vertices + list(simplex.vertices))))
                if union in self.simplices:
                    link_complex.add_simplex(list(s.vertices))
        
        return link_complex
    
    def star(self, simplex: Simplex) -> SimplicialComplex:
        """Compute the star of a simplex"""
        star_complex = SimplicialComplex(f"star({simplex.vertices})")
        
        for s in self.simplices:
            # Check if simplex is a face of s
            if set(simplex.vertices).issubset(set(s.vertices)):
                star_complex.add_simplex(list(s.vertices))
        
        return star_complex
    
    def boundary_operator(self, dim: int) -> np.ndarray:
        """Compute the boundary matrix for dimension dim"""
        if dim <= 0:
            return np.array([])
        
        simplices_dim = self.get_simplices_of_dim(dim)
        simplices_dim_1 = self.get_simplices_of_dim(dim - 1)
        
        if not simplices_dim or not simplices_dim_1:
            return np.array([])
        
        # Build boundary matrix
        matrix = np.zeros((len(simplices_dim_1), len(simplices_dim)))
        
        for i, simplex in enumerate(simplices_dim):
            for j, face in enumerate(simplex.faces()):
                # Find face in lower dimension
                for k, low_simplex in enumerate(simplices_dim_1):
                    if set(face.vertices) == set(low_simplex.vertices):
                        # Orientation sign
                        sign = (-1) ** (simplex.vertices.index(face.vertices[0]) 
                                       if face.vertices[0] in simplex.vertices else 0)
                        matrix[k, i] = sign
                        break
        
        return matrix
    
    def betti_numbers(self, max_dim: Optional[int] = None) -> List[int]:
        """Compute Betti numbers (placeholder - needs actual homology computation)"""
        if max_dim is None:
            max_dim = self.dimension
        
        betti = []
        for dim in range(max_dim + 1):
            # Simplified - actual computation needs Smith normal form
            num_simplices = len(self.get_simplices_of_dim(dim))
            betti.append(max(0, num_simplices - 1))  # Placeholder
        
        return betti
    
    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            "name": self.name,
            "dimension": self.dimension,
            "simplices": [
                {"vertices": list(s.vertices), "dimension": s.dimension}
                for s in self.simplices
            ]
        }
    
    def __repr__(self):
        return f"SimplicialComplex({self.name}, dim={self.dimension}, simplices={len(self.simplices)})"


def create_proof_complex(proof_graph) -> SimplicialComplex:
    """
    Create a simplicial complex from a proof graph.
    
    - Vertices (0-simplices) = proof vertices
    - Edges (1-simplices) = inference steps
    - Triangles (2-simplices) = alternative proof paths
    """
    complex = SimplicialComplex("proof_complex")
    
    # Add vertices
    for vid in proof_graph.vertices:
        complex.add_simplex([vid])
    
    # Add edges
    for edge in proof_graph.edges.values():
        complex.add_simplex([edge.source, edge.target])
    
    # Add triangles for convergent paths
    # (when multiple paths lead to same conclusion)
    return complex
