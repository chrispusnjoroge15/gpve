"""Proof Graph - Core data structure for logical proofs"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum
import uuid


class VertexType(Enum):
    """Types of vertices in the proof graph"""
    ASSUMPTION = "assumption"
    THEOREM = "theorem"
    LEMMA = "lemma"
    AXIOM = "axiom"
    GOAL = "goal"
    DERIVED = "derived"


class EdgeType(Enum):
    """Types of edges (inference steps)"""
    IMPLIES = "implies"
    AND_ELIM = "and_elim"
    OR_INTRO = "or_intro"
    NOT_ELIM = "not_elim"
    FORALL_ELIM = "forall_elim"
    EXISTS_INTRO = "exists_intro"
    EQUIV = "equiv"
    CUSTOM = "custom"


@dataclass
class Vertex:
    """A vertex representing a logical statement"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    statement: str = ""
    vertex_type: VertexType = VertexType.DERIVED
    formula: Optional[Any] = None  # SMT formula representation
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, Vertex):
            return False
        return self.id == other.id


@dataclass
class Edge:
    """An edge representing an inference step"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = ""  # Vertex ID
    target: str = ""  # Vertex ID
    edge_type: EdgeType = EdgeType.CUSTOM
    rule_name: str = ""
    premises: List[str] = field(default_factory=list)
    conclusion: str = ""
    proof_step: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)


class ProofGraph:
    """
    Directed acyclic graph representing a mathematical proof.
    
    Vertices = statements (assumptions, theorems, lemmas, derived facts)
    Edges = inference steps connecting premises to conclusions
    """
    
    def __init__(self, name: str = "proof"):
        self.name = name
        self.vertices: Dict[str, Vertex] = {}
        self.edges: Dict[str, Edge] = {}
        self.adjacency: Dict[str, List[str]] = {}  # vertex_id -> [outgoing edge ids]
        self.reverse_adjacency: Dict[str, List[str]] = {}  # vertex_id -> [incoming edge ids]
    
    def add_vertex(self, statement: str, vertex_type: VertexType = VertexType.DERIVED, 
                   formula: Any = None, **metadata) -> Vertex:
        """Add a new vertex to the proof graph"""
        vertex = Vertex(
            statement=statement,
            vertex_type=vertex_type,
            formula=formula,
            metadata=metadata
        )
        self.vertices[vertex.id] = vertex
        self.adjacency[vertex.id] = []
        self.reverse_adjacency[vertex.id] = []
        return vertex
    
    def add_edge(self, source: str, target: str, edge_type: EdgeType = EdgeType.CUSTOM,
                 rule_name: str = "", proof_step: str = "", **metadata) -> Edge:
        """Add a new edge (inference step) to the proof graph"""
        if source not in self.vertices:
            raise ValueError(f"Source vertex {source} not in graph")
        if target not in self.vertices:
            raise ValueError(f"Target vertex {target} not in graph")
        
        edge = Edge(
            source=source,
            target=target,
            edge_type=edge_type,
            rule_name=rule_name,
            proof_step=proof_step,
            metadata=metadata
        )
        self.edges[edge.id] = edge
        self.adjacency[source].append(edge.id)
        self.reverse_adjacency[target].append(edge.id)
        return edge
    
    def get_premises(self, vertex_id: str) -> List[Vertex]:
        """Get all premises (incoming vertices) for a given vertex"""
        premise_ids = self.reverse_adjacency.get(vertex_id, [])
        return [self.edges[eid].source for eid in premise_ids]
    
    def get_conclusions(self, vertex_id: str) -> List[Vertex]:
        """Get all conclusions (outgoing vertices) from a given vertex"""
        conclusion_ids = self.adjacency.get(vertex_id, [])
        return [self.edges[eid].target for eid in conclusion_ids]
    
    def get_path(self, start: str, end: str) -> List[List[Vertex]]:
        """Find all paths from start vertex to end vertex"""
        paths = []
        
        def dfs(current: str, target: str, path: List[str]):
            if current == target:
                paths.append(path.copy())
                return
            for edge_id in self.adjacency.get(current, []):
                edge = self.edges[edge_id]
                if edge.target not in path:
                    path.append(edge.target)
                    dfs(edge.target, target, path)
                    path.pop()
        
        dfs(start, end, [start])
        return [[self.vertices[v_id] for v_id in path] for path in paths]
    
    def topological_sort(self) -> List[Vertex]:
        """Return vertices in topological order (prerequisites first)"""
        in_degree = {v: len(self.reverse_adjacency[v]) for v in self.vertices}
        queue = [v for v, d in in_degree.items() if d == 0]
        result = []
        
        while queue:
            vertex_id = queue.pop(0)
            result.append(self.vertices[vertex_id])
            
            for edge_id in self.adjacency[vertex_id]:
                edge = self.edges[edge_id]
                in_degree[edge.target] -= 1
                if in_degree[edge.target] == 0:
                    queue.append(edge.target)
        
        return result
    
    def to_dict(self) -> dict:
        """Serialize proof graph to dictionary"""
        return {
            "name": self.name,
            "vertices": [
                {
                    "id": v.id,
                    "statement": v.statement,
                    "type": v.vertex_type.value,
                    "metadata": v.metadata
                }
                for v in self.vertices.values()
            ],
            "edges": [
                {
                    "id": e.id,
                    "source": e.source,
                    "target": e.target,
                    "type": e.edge_type.value,
                    "rule": e.rule_name,
                    "proof_step": e.proof_step,
                    "metadata": e.metadata
                }
                for e in self.edges.values()
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProofGraph":
        """Deserialize proof graph from dictionary"""
        graph = cls(name=data.get("name", "proof"))
        
        vertex_map = {}
        for v_data in data.get("vertices", []):
            vertex = Vertex(
                id=v_data["id"],
                statement=v_data["statement"],
                vertex_type=VertexType(v_data.get("type", "derived")),
                metadata=v_data.get("metadata", {})
            )
            graph.vertices[vertex.id] = vertex
            graph.adjacency[vertex.id] = []
            graph.reverse_adjacency[vertex.id] = []
            vertex_map[v_data["id"]] = vertex
        
        for e_data in data.get("edges", []):
            edge = Edge(
                id=e_data["id"],
                source=e_data["source"],
                target=e_data["target"],
                edge_type=EdgeType(e_data.get("type", "custom")),
                rule_name=e_data.get("rule", ""),
                proof_step=e_data.get("proof_step", ""),
                metadata=e_data.get("metadata", {})
            )
            graph.edges[edge.id] = edge
            graph.adjacency[edge.source].append(edge.id)
            graph.reverse_adjacency[edge.target].append(edge.id)
        
        return graph
    
    def __repr__(self):
        return f"ProofGraph(name={self.name}, vertices={len(self.vertices)}, edges={len(self.edges)})"
