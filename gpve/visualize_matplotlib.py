"""Visualization with Matplotlib support"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
import numpy as np

# Optional matplotlib import
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class MatplotlibVisualizer:
    """
    Matplotlib-based visualization for proof graphs.
    
    Requires: pip install matplotlib
    """
    
    def __init__(self, figsize: tuple = (12, 8)):
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib not installed. Run: pip install matplotlib")
        
        self.figsize = figsize
        self.fig = None
        self.ax = None
    
    def _init_figure(self):
        """Initialize figure"""
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.ax.set_axis_off()
    
    def plot_proof_graph(
        self, 
        proof_graph,
        layout: Optional[Dict[str, tuple]] = None,
        title: str = "Proof Graph"
    ) -> None:
        """Plot a proof graph"""
        self._init_figure()
        
        if layout is None:
            # Simple layered layout
            layout = self._compute_layout(proof_graph)
        
        # Draw edges first (behind nodes)
        for edge in proof_graph.edges.values():
            src = layout.get(edge.source)
            dst = layout.get(edge.target)
            
            if src and dst:
                self.ax.annotate(
                    "", xy=dst, xytext=src,
                    arrowprops=dict(arrowstyle="->", color="#888", lw=1.5)
                )
        
        # Draw nodes
        for vid, vertex in proof_graph.vertices.items():
            pos = layout.get(vid)
            if pos:
                # Color by type
                colors = {
                    "assumption": "#FF6B6B",
                    "theorem": "#4ECDC4",
                    "lemma": "#45B7D1",
                    "axiom": "#96CEB4",
                    "goal": "#FFEAA7",
                    "derived": "#DDA0DD"
                }
                color = colors.get(vertex.vertex_type.value, "#DDA0DD")
                
                circle = plt.Circle(pos, 0.08, color=color, ec="#333", lw=2)
                self.ax.add_patch(circle)
                
                # Label
                label = vertex.statement[:20] + "..." if len(vertex.statement) > 20 else vertex.statement
                self.ax.text(pos[0], pos[1]-0.12, label, ha='center', fontsize=8)
        
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.ax.autoscale()
        self.ax.set_aspect('equal')
    
    def _compute_layout(self, proof_graph) -> Dict[str, tuple]:
        """Compute simple layered layout"""
        # Group by distance from roots
        distances = {}
        
        # Find roots (no incoming edges)
        for vid in proof_graph.vertices:
            if not proof_graph.reverse_adjacency.get(vid):
                distances[vid] = 0
        
        # BFS to compute distances
        queue = list(distances.keys())
        while queue:
            vid = queue.pop(0)
            dist = distances[vid]
            
            for edge_id in proof_graph.adjacency.get(vid, []):
                edge = proof_graph.edges[edge_id]
                if edge.target not in distances:
                    distances[edge.target] = dist + 1
                    queue.append(edge.target)
        
        # Default for disconnected
        for vid in proof_graph.vertices:
            if vid not in distances:
                distances[vid] = 1
        
        # Group by distance
        layers = {}
        for vid, d in distances.items():
            if d not in layers:
                layers[d] = []
            layers[d].append(vid)
        
        # Compute positions
        layout = {}
        max_width = max(len(l) for l in layers.values()) if layers else 1
        
        for dist, vertices in layers.items():
            n = len(vertices)
            for i, vid in enumerate(vertices):
                x = (i - (n-1)/2) * 0.5
                y = -dist * 0.5
                layout[vid] = (x, y)
        
        return layout
    
    def plot_proof_paths(
        self,
        proof_graph,
        paths: List[List[str]],
        title: str = "Proof Paths"
    ) -> None:
        """Plot multiple proof paths"""
        self._init_figure()
        
        layout = self._compute_layout(proof_graph)
        
        # Colors for different paths
        colors = plt.cm.Set1(np.linspace(0, 1, len(paths)))
        
        # Draw all edges faintly
        for edge in proof_graph.edges.values():
            src = layout.get(edge.source)
            dst = layout.get(edge.target)
            
            if src and dst:
                self.ax.plot([src[0], dst[0]], [src[1], dst[1]], 
                           'k-', alpha=0.1, lw=1)
        
        # Highlight each path
        for i, path in enumerate(paths):
            for j in range(len(path) - 1):
                src = layout.get(path[j])
                dst = layout.get(path[j+1])
                
                if src and dst:
                    self.ax.annotate(
                        "", xy=dst, xytext=src,
                        arrowprops=dict(arrowstyle="->", color=colors[i], lw=2)
                    )
        
        # Draw nodes
        for vid, vertex in proof_graph.vertices.items():
            pos = layout.get(vid)
            if pos:
                circle = plt.Circle(pos, 0.05, color="#4A90D9", ec="#333")
                self.ax.add_patch(circle)
        
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.ax.set_aspect('equal')
        self.ax.autoscale()
    
    def plot_smt_model(
        self,
        model: Dict[str, Any],
        title: str = "SMT Model"
    ) -> None:
        """Plot SMT solver model"""
        self._init_figure()
        
        if not model:
            self.ax.text(0.5, 0.5, "No model", ha='center', va='center')
            return
        
        y_pos = 0.9
        for var, value in model.items():
            self.ax.text(0.1, y_pos, f"{var} = {value}", fontsize=12, 
                        family='monospace', transform=self.ax.transAxes)
            y_pos -= 0.1
        
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis('off')
    
    def save(self, filename: str, dpi: int = 150) -> None:
        """Save figure to file"""
        if self.fig:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')
            print(f"Saved: {filename}")
    
    def show(self) -> None:
        """Show figure (if interactive)"""
        if self.fig:
            plt.show()
    
    def close(self) -> None:
        """Close figure"""
        if self.fig:
            plt.close(self.fig)


def plot_proof(proof_graph, output: str = None, title: str = "Proof Graph"):
    """Quick plot function"""
    if not MATPLOTLIB_AVAILABLE:
        print("matplotlib not available")
        return
    
    viz = MatplotlibVisualizer()
    viz.plot_proof_graph(proof_graph, title=title)
    
    if output:
        viz.save(output)
    else:
        viz.show()
    
    viz.close()


# Convenience function
def visualize(
    proof_graph,
    output: str = None,
    format: str = "mermaid"
):
    """
    Visualize a proof graph.
    
    Args:
        proof_graph: The ProofGraph to visualize
        output: Output file path (optional)
        format: "mermaid", "dot", "json", or "matplotlib"
    """
    if format == "matplotlib":
        plot_proof(proof_graph, output)
    else:
        # Use text-based visualizer
        from .visualize import visualize_proof
        print(visualize_proof(proof_graph, format))
