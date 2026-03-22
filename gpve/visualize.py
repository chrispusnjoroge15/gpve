"""Visualization - Proof graphs, simplicial complexes, homotopy paths"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json


@dataclass
class GraphStyle:
    """Styling for graph visualization"""
    node_color: str = "#4A90D9"
    edge_color: str = "#888888"
    node_size: int = 30
    edge_width: int = 2
    font_size: int = 12
    background: str = "#FFFFFF"


@dataclass
class Point2D:
    """2D point"""
    x: float
    y: float


@dataclass
class Point3D:
    """3D point"""
    x: float
    y: float
    z: float


class GraphVisualizer:
    """
    Generate visualizations of proof graphs.
    
    Outputs:
    - DOT (GraphViz) format
    - JSON for D3.js / web visualization
    - Mermaid diagrams
    """
    
    def __init__(self, style: Optional[GraphStyle] = None):
        self.style = style or GraphStyle()
    
    def to_dot(self, proof_graph, layout: str = "dot") -> str:
        """
        Generate DOT (GraphViz) format.
        
        Args:
            proof_graph: The ProofGraph to visualize
            layout: GraphViz layout algorithm (dot, neato, fdp, sfdp, circo, twopi)
        """
        lines = [
            f"digraph {proof_graph.name} {{",
            f"  layout={layout};",
            f"  rankdir=TB;",
            f"  node [style=filled, color={self.style.node_color}];",
            f"  edge [color={self.style.edge_color}];",
        ]
        
        # Add nodes
        for vertex in proof_graph.vertices.values():
            label = vertex.statement.replace('"', '\\"')[:50]
            lines.append(f'  "{vertex.id}" [label="{label}"];')
        
        # Add edges
        for edge in proof_graph.edges.values():
            label = edge.rule_name or edge.edge_type.value
            lines.append(f'  "{edge.source}" -> "{edge.target}" [label="{label}"];')
        
        lines.append("}")
        return "\n".join(lines)
    
    def to_mermaid(self, proof_graph) -> str:
        """Generate Mermaid flowchart format"""
        lines = ["flowchart TD"]
        
        # Add nodes with labels
        for vertex in proof_graph.vertices.values():
            label = vertex.statement.replace('"', '')[:30]
            # Use vertex type as shape hint
            shape = "{" if vertex.vertex_type.value == "theorem" else "["
            shape_close = "}" if vertex.vertex_type.value == "theorem" else "]"
            lines.append(f'  {vertex.id}{shape}"{label}"{shape_close}')
        
        # Add edges
        for edge in proof_graph.edges.values():
            label = edge.rule_name or ""
            if label:
                lines.append(f'  {edge.source} -->|{label}| {edge.target}')
            else:
                lines.append(f'  {edge.source} --> {edge.target}')
        
        return "\n".join(lines)
    
    def to_json(self, proof_graph) -> str:
        """Generate JSON for web visualization"""
        data = {
            "nodes": [
                {
                    "id": v.id,
                    "label": v.statement[:50],
                    "type": v.vertex_type.value,
                }
                for v in proof_graph.vertices.values()
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "label": e.rule_name,
                }
                for e in proof_graph.edges.values()
            ],
        }
        return json.dumps(data, indent=2)
    
    def to_cytoscape_json(self, proof_graph) -> str:
        """Generate JSON for Cytoscape.js"""
        elements = []
        
        for vertex in proof_graph.vertices.values():
            elements.append({
                "data": {
                    "id": vertex.id,
                    "label": vertex.statement[:30],
                }
            })
        
        for edge in proof_graph.edges.values():
            elements.append({
                "data": {
                    "id": edge.id,
                    "source": edge.source,
                    "target": edge.target,
                    "label": edge.rule_name,
                }
            })
        
        return json.dumps({"elements": elements}, indent=2)


class SimplicialVisualizer:
    """
    Visualize simplicial complexes.
    
    Outputs formats for:
    - 3D viewing (OBJ, PLY)
    - WebGL (three.js compatible)
    - 2D projection
    """
    
    def __init__(self):
        self.vertices_3d: Dict[int, Point3D] = {}
    
    def project_to_2d(
        self, 
        vertices_3d: Dict[int, Tuple[float, float, float]]
    ) -> Dict[int, Point2D]:
        """Project 3D vertices to 2D (simple orthographic)"""
        result = {}
        for vid, (x, y, z) in vertices_3d.items():
            # Simple projection - could use perspective
            result[vid] = Point2D(x, y)
        return result
    
    def compute_layout(
        self, 
        simplices: List[Any],
        iterations: int = 100
    ) -> Dict[int, Point2D]:
        """
        Compute force-directed layout for simplicial complex.
        
        Simple spring embedding algorithm.
        """
        if not simplices:
            return {}
        
        # Extract unique vertices
        all_vertices = set()
        for s in simplices:
            for v in s.vertices:
                all_vertices.add(v)
        
        # Initialize random positions
        import random
        random.seed(42)
        positions = {v: Point2D(random.random(), random.random()) for v in all_vertices}
        
        # Simple iteration (placeholder for real force-directed)
        for _ in range(iterations):
            pass  # Would apply forces here
        
        return positions
    
    def to_threejs_json(self, simplicial_complex) -> str:
        """Generate three.js compatible JSON"""
        # Get all vertices
        vertices_list = []
        indices_list = []
        
        # Collect unique vertices and build index mapping
        vertex_map = {}
        vertex_idx = 0
        
        for simplex in simplicial_complex.simplices:
            if simplex.dimension == 0:
                # Point
                vertex_map[simplex.vertices[0]] = vertex_idx
                vertices_list.extend([0.0, 0.0, 0.0])  # Placeholder
                vertex_idx += 1
            elif simplex.dimension == 1:
                # Line
                for v in simplex.vertices:
                    if v not in vertex_map:
                        vertex_map[v] = vertex_idx
                        vertices_list.extend([0.0, 0.0, 0.0])
                        vertex_idx += 1
                indices_list.extend([vertex_map[simplex.vertices[0]], vertex_map[simplex.vertices[1]]])
            elif simplex.dimension == 2:
                # Triangle
                for v in simplex.vertices:
                    if v not in vertex_map:
                        vertex_map[v] = vertex_idx
                        vertices_list.extend([0.0, 0.0, 0.0])
                        vertex_idx += 1
                indices_list.extend([
                    vertex_map[simplex.vertices[0]],
                    vertex_map[simplex.vertices[1]],
                    vertex_map[simplex.vertices[2]]
                ])
        
        data = {
            "vertices": vertices_list,
            "indices": indices_list,
        }
        
        return json.dumps(data)
    
    def to_obj(self, simplicial_complex) -> str:
        """Generate OBJ 3D format"""
        lines = ["# GPVE Simplicial Complex"]
        
        # Very simplified OBJ output
        vertex_counter = 1
        
        for simplex in sorted(simplicial_complex.simplices, key=lambda s: s.dimension):
            if simplex.dimension == 1:
                # Edge
                lines.append(f"v 0 0 0  # {simplex.vertices[0]}")
                lines.append(f"v 1 0 0  # {simplex.vertices[1]}")
                lines.append(f"l {vertex_counter} {vertex_counter + 1}")
                vertex_counter += 2
            elif simplex.dimension == 2:
                # Triangle
                lines.append(f"v 0 0 0")
                lines.append(f"v 1 0 0")
                lines.append(f"v 0.5 1 0")
                lines.append(f"f {vertex_counter} {vertex_counter+1} {vertex_counter+2}")
                vertex_counter += 3
        
        return "\n".join(lines)


class HomotopyVisualizer:
    """Visualize homotopy classes and proof equivalence"""
    
    def to_svg(self, homotopy_classes: List[Any], proof_graph) -> str:
        """Generate SVG showing equivalence classes"""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">',
            "  <style>",
            "    .node { fill: #4A90D9; stroke: #333; }",
            "    .edge { stroke: #888; stroke-width: 2; }",
            "    .equiv { stroke-dasharray: 5,5; }",
            "  </style>",
        ]
        
        # Add equivalence classes as dashed circles
        for i, cls in enumerate(homotopy_classes):
            cx, cy = 50 + (i % 3) * 120, 50 + (i // 3) * 100
            lines.append(f'  <circle cx="{cx}" cy="{cy}" r="40" fill="none" stroke="#888" stroke-dasharray="5,5"/>')
            lines.append(f'  <text x="{cx}" y="{cy+55}" text-anchor="middle">Class {i+1}</text>')
        
        lines.append("</svg>")
        return "\n".join(lines)


class ProofPathRenderer:
    """Render proof paths and equivalence classes"""
    
    def __init__(self):
        self.colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
    
    def render_paths_svg(
        self, 
        paths: List[List[str]], 
        proof_graph,
        width: int = 800,
        height: int = 600
    ) -> str:
        """Render multiple proof paths as SVG"""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
            "  <style>",
            "    .path { fill: none; stroke-width: 3; }",
            "    .vertex { fill: #4A90D9; }",
            "  </style>",
        ]
        
        # Simple layout
        import random
        random.seed(42)
        
        vertex_positions = {}
        for i, vid in enumerate(proof_graph.vertices.keys()):
            x = 50 + (i % 4) * (width // 5)
            y = 50 + (i // 4) * (height // 5)
            vertex_positions[vid] = (x, y)
        
        # Draw vertices
        for vid, (x, y) in vertex_positions.items():
            label = proof_graph.vertices[vid].statement[:15]
            lines.append(f'  <circle cx="{x}" cy="{y}" r="15" class="vertex"/>')
            lines.append(f'  <text x="{x}" y="{y+30}" text-anchor="middle" font-size="10">{label}</text>')
        
        # Draw paths with different colors
        for i, path in enumerate(paths):
            color = self.colors[i % len(self.colors)]
            d = ""
            
            for j, vid in enumerate(path):
                if vid in vertex_positions:
                    x, y = vertex_positions[vid]
                    cmd = "M" if j == 0 else "L"
                    d += f" {cmd}{x},{y}"
            
            lines.append(f'  <path d="{d}" stroke="{color}" class="path"/>')
        
        lines.append("</svg>")
        return "\n".join(lines)


def visualize_proof(proof_graph, output_format: str = "mermaid") -> str:
    """
    Quick visualization helper.
    
    Args:
        proof_graph: The ProofGraph to visualize
        output_format: "dot", "mermaid", "json", "svg"
    
    Returns:
        Visualization in requested format
    """
    viz = GraphVisualizer()
    
    if output_format == "dot":
        return viz.to_dot(proof_graph)
    elif output_format == "mermaid":
        return viz.to_mermaid(proof_graph)
    elif output_format == "json":
        return viz.to_json(proof_graph)
    else:
        return viz.to_dot(proof_graph)


def visualize_proof_paths(proof_graph, paths: List[List[str]]) -> str:
    """Quick path visualization"""
    renderer = ProofPathRenderer()
    return renderer.render_paths_svg(paths, proof_graph)
