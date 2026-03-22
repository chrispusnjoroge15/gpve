"""
Example proofs demonstrating GPVE capabilities.

Run with: python -m gpve.examples
"""

from gpve import create_engine
from gpve.core import ProofGraph, Vertex


def example_smt_solving():
    """Example: Simple SMT constraint solving"""
    print("=" * 50)
    print("Example 1: SMT Solving")
    print("=" * 50)
    
    from gpve.core import SMTSolver
    
    solver = SMTSolver()
    x = solver.Int("x")
    y = solver.Int("y")
    
    # Constraints: x + y = 10, x > 0, y > 0
    solver.assert_formula(x + y == 10)
    solver.assert_formula(x > 0)
    solver.assert_formula(y > 0)
    
    result = solver.check()
    print(f"Constraints: x + y = 10, x > 0, y > 0")
    print(f"Result: {result.status}")
    print(f"Model: {result.model}")
    print()


def example_proof_graph():
    """Example: Building a proof graph"""
    print("=" * 50)
    print("Example 2: Proof Graph")
    print("=" * 50)
    
    from gpve.core import ProofGraph, Vertex, Edge
    
    graph = ProofGraph("modus_ponens")
    
    # P, P → Q ⊢ Q (Modus Ponens)
    v1 = graph.add_vertex("P", vertex_type=Vertex.VertexType.ASSUMPTION)
    v2 = graph.add_vertex("P → Q", vertex_type=Vertex.VertexType.ASSUMPTION)
    v3 = graph.add_vertex("Q", vertex_type=Vertex.VertexType.THEOREM)
    
    graph.add_edge(v1.id, v3.id, rule_name="modus_ponens_1")
    graph.add_edge(v2.id, v3.id, rule_name="modus_ponens_2")
    
    print(f"Proof: Modus Ponens (P, P → Q ⊢ Q)")
    print(f"Vertices: {len(graph.vertices)}")
    print(f"Edges: {len(graph.edges)}")
    
    # Show structure
    for v in graph.vertices.values():
        print(f"  - {v.statement} ({v.vertex_type.value})")
    print()


def example_theorem_proving():
    """Example: Theorem proving with GPVE engine"""
    print("=" * 50)
    print("Example 3: Theorem Proving")
    print("=" * 50)
    
    engine = create_engine()
    
    # Prove: If x > 0 and y > 0, then x + y > 0
    engine.create_proof("If x > 0 and y > 0, then x + y > 0")
    
    # Add assumptions
    engine.add_assumption("H1", "x > 0")
    engine.add_assumption("H2", "y > 0")
    
    # Add inference
    engine.add_inference(["x > 0", "y > 0"], "x + y > 0", "addition_positive")
    
    result = engine.verify_proof()
    print("Theorem: If x > 0 and y > 0, then x + y > 0")
    print(f"Verified: {result.is_valid}")
    print()


def example_category_theory():
    """Example: Category theory reasoning"""
    print("=" * 50)
    print("Example 4: Category Theory")
    print("=" * 50)
    
    engine = create_engine()
    
    # Add propositions as objects
    engine.add_proposition("P")
    engine.add_proposition("Q")
    engine.add_proposition("R")
    
    # Add proofs as morphisms
    engine.add_proof_morphism("P", "Q", "f")
    engine.add_proof_morphism("Q", "R", "g")
    
    # Check morphisms exist
    proofs_PQ = engine.category.get_proofs("P", "Q")
    proofs_QR = engine.category.get_proofs("Q", "R")
    
    print("Category: Proof")
    print(f"  Objects: P, Q, R")
    print(f"  Morphisms P→Q: {len(proofs_PQ)}")
    print(f"  Morphisms Q→R: {len(proofs_QR)}")
    print()


def example_topology():
    """Example: Topological proof analysis"""
    print("=" * 50)
    print("Example 5: Topology Analysis")
    print("=" * 50)
    
    from gpve.core import ProofGraph
    from gpve.geometric import TopologicalProofEngine
    
    # Create proof graph with multiple paths
    graph = ProofGraph("multiple_proofs")
    vA = graph.add_vertex("A")
    vB = graph.add_vertex("B")
    vC = graph.add_vertex("C")
    vD = graph.add_vertex("D")
    
    # Two different proof paths
    graph.add_edge(vA.id, vB.id)  # A → B
    graph.add_edge(vA.id, vC.id)  # A → C
    graph.add_edge(vB.id, vD.id)  # B → D
    graph.add_edge(vC.id, vD.id)  # C → D
    
    # Build topology
    engine = TopologicalProofEngine()
    engine.build_proof_space(graph)
    
    # Analyze
    analysis = engine.analyze_topology("multiple_proofs")
    
    print("Proof with multiple paths A→D:")
    print(f"  Vertices: {analysis['num_vertices']}")
    print(f"  Edges: {analysis['num_edges']}")
    print(f"  Components: {analysis['num_components']}")
    
    # Find all proofs
    proofs = engine.find_proofs("A", "D")
    print(f"  Proof paths: {len(proofs)}")
    print()


def example_sheaf_reasoning():
    """Example: Sheaf-based modular reasoning"""
    print("=" * 50)
    print("Example 6: Sheaf Reasoning")
    print("=" * 50)
    
    engine = create_engine()
    
    # Add local proofs in different contexts
    engine.add_local_proof("U1", "P → Q", {"type": "lemma", "proof": "..."})
    engine.add_local_proof("U2", "Q → R", {"type": "lemma", "proof": "..."})
    
    # Glue into global proof
    global_proof = engine.glue_local_proofs(["U1", "U2"])
    
    print("Sheaf-based reasoning:")
    print(f"  Local patches: 2")
    print(f"  Global proof: {global_proof is not None}")
    print()


def example_ai_exploration():
    """Example: AI-assisted proof exploration"""
    print("=" * 50)
    print("Example 7: AI Exploration")
    print("=" * 50)
    
    from gpve.config import get_api_keys
    
    keys = get_api_keys()
    configured = [k for k, v in keys.items() if v]
    
    if configured:
        engine = create_engine()
        
        # Try AI exploration
        prompt = "Prove that the square root of 2 is irrational"
        results = engine.ai_explore(prompt)
        
        for provider, result in results.items():
            print(f"  {provider.value}: {result.response.content[:100]}...")
    else:
        print("  No AI APIs configured.")
        print("  Set OPENAI_API_KEY, GEMINI_API_KEY, or DEEPSEEK_API_KEY")
    print()


def example_visualization():
    """Example: Visualizing a proof"""
    print("=" * 50)
    print("Example 8: Visualization")
    print("=" * 50)
    
    from gpve.core import ProofGraph
    from gpve.visualize import visualize_proof
    
    graph = ProofGraph("demo")
    v1 = graph.add_vertex("P → Q")
    v2 = graph.add_vertex("P")
    v3 = graph.add_vertex("Q")
    
    graph.add_edge(v1.id, v3.id, rule_name="elim")
    graph.add_edge(v2.id, v3.id, rule_name="intro")
    
    # Generate Mermaid diagram
    mermaid = visualize_proof(graph, "mermaid")
    
    print("Mermaid diagram:")
    print(mermaid)
    print()


def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("GPVE EXAMPLES")
    print("=" * 60 + "\n")
    
    example_smt_solving()
    example_proof_graph()
    example_theorem_proving()
    example_category_theory()
    example_topology()
    example_sheaf_reasoning()
    example_ai_exploration()
    example_visualization()
    
    print("=" * 60)
    print("All examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
