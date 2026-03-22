"""GPVE CLI - Extended command-line interface"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpve import GPVEEngine, create_engine
from gpve.core import ProofGraph, Vertex
from gpve.visualize import visualize_proof, visualize_proof_paths
from gpve.config import get_api_keys


def cmd_engine(args):
    """Run the unified GPVE engine"""
    engine = create_engine()
    print(f"GPVE Engine initialized: {engine}")
    
    # Quick demo
    engine.add_proposition("P")
    engine.add_proposition("Q")
    engine.add_proof_morphism("P", "Q", "proof_1")
    
    print(f"Category: {engine.category}")


def cmd_verify(args):
    """Verify a proof"""
    engine = create_engine()
    
    # Build simple proof graph
    graph = ProofGraph("demo")
    v1 = graph.add_vertex("x > 0")
    v2 = graph.add_vertex("y > 0")
    v3 = graph.add_vertex("x + y > 0")
    
    graph.add_edge(v1.id, v3.id, rule_name="add_positive")
    graph.add_edge(v2.id, v3.id, rule_name="add_positive")
    
    result = engine.full_verify("x + y > 0", graph)
    
    print(f"Verification result:")
    print(f"  Valid: {result.is_valid}")
    print(f"  SMT: {result.smt_result}")
    print(f"  Type check: {result.type_check}")
    print(f"  Geometric: {result.geometric_check}")


def cmd_ai_status(args):
    """Check AI provider status"""
    keys = get_api_keys()
    
    print("AI Provider Status:")
    for name, key in keys.items():
        status = "✅ Configured" if key else "❌ Not set"
        print(f"  {name.upper()}: {status}")


def cmd_sheaf(args):
    """Demonstrate sheaf-based reasoning"""
    engine = create_engine()
    
    # Add local proofs
    engine.add_local_proof("U1", "P → Q", {"type": "lemma1"})
    engine.add_local_proof("U2", "Q → R", {"type": "lemma2"})
    
    # Glue
    global_proof = engine.glue_local_proofs(["U1", "U2"])
    
    print(f"Sheaf Reasoning:")
    print(f"  Local proofs: 2")
    print(f"  Global proof: {global_proof is not None}")


def cmd_category(args):
    """Demonstrate category theory"""
    engine = create_engine()
    
    # Add propositions
    engine.add_proposition("P")
    engine.add_proposition("Q")
    engine.add_proposition("R")
    
    # Add proofs as morphisms
    engine.add_proof_morphism("P", "Q", "f")
    engine.add_proof_morphism("Q", "R", "g")
    engine.add_proof_morphism("P", "R", "h")
    
    # Add equivalence
    engine.add_proof_equivalence("f∘g", "h", "associativity")
    
    is_equiv = engine.check_proof_equivalent("f∘g", "h")
    
    print(f"Category Theory:")
    print(f"  Objects: {len(engine.category.objects)}")
    print(f"  Morphisms: {len(engine.category.morphisms)}")
    print(f"  Proofs equivalent: {is_equiv}")


def cmd_visualize(args):
    """Visualize a proof graph"""
    graph = ProofGraph("demo")
    v1 = graph.add_vertex("x > 0")
    v2 = graph.add_vertex("y > 0")
    v3 = graph.add_vertex("x + y > 0")
    graph.add_edge(v1.id, v3.id, rule_name="add")
    graph.add_edge(v2.id, v3.id, rule_name="add")
    
    fmt = args.format or "mermaid"
    output = visualize_proof(graph, fmt)
    
    print(output)


def cmd_topology(args):
    """Analyze proof topology"""
    engine = create_engine()
    
    graph = ProofGraph("topology")
    v1 = graph.add_vertex("A")
    v2 = graph.add_vertex("B")
    v3 = graph.add_vertex("C")
    v4 = graph.add_vertex("D")
    
    graph.add_edge(v1.id, v2.id)
    graph.add_edge(v1.id, v3.id)
    graph.add_edge(v2.id, v4.id)
    graph.add_edge(v3.id, v4.id)
    
    engine.build_proof_space(graph)
    analysis = engine.topology_engine.analyze_topology("topology")
    
    print("Topology Analysis:")
    for k, v in analysis.items():
        print(f"  {k}: {v}")


def cmd_all(args):
    """Run full demo"""
    print("=" * 50)
    print("GPVE Full Demo")
    print("=" * 50)
    
    engine = create_engine()
    
    # 1. SMT
    print("\n[1] SMT Layer:")
    print(f"  Solver: {engine.smt_solver}")
    
    # 2. Type theory
    print("\n[2] Type Theory Layer:")
    proof = engine.create_proof("If P then P")
    print(f"  Proof kernel: {engine.proof_kernel}")
    
    # 3. Sheaf
    print("\n[3] Sheaf Layer:")
    engine.add_local_proof("ctx1", "P", {"proof": "local1"})
    print(f"  Sheaf reasoning: {engine.sheaf_reasoning}")
    
    # 4. Category
    print("\n[4] Category Layer:")
    engine.add_proposition("X")
    engine.add_proposition("Y")
    engine.add_proof_morphism("X", "Y", "f")
    print(f"  Category: {engine.category}")
    
    # 5. Geometric
    print("\n[5] Geometric Layer:")
    graph = ProofGraph("test")
    v1 = graph.add_vertex("P")
    v2 = graph.add_vertex("Q")
    graph.add_edge(v1.id, v2.id)
    engine.build_proof_space(graph)
    print(f"  Topology engine: {engine.topology_engine}")
    
    # 6. AI
    print("\n[6] AI Layer:")
    print(f"  Available: {engine.ai.available()}")
    
    print("\n" + "=" * 50)
    print("All layers functional!")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="GPVE - Geometric Proof & Verification Engine")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Core
    subparsers.add_parser("engine", help="Run GPVE engine demo")
    subparsers.add_parser("verify", help="Verify a proof")
    subparsers.add_parser("all", help="Run full demo")
    
    # AI
    subparsers.add_parser("ai-status", help="Check AI provider status")
    
    # Layers
    subparsers.add_parser("sheaf", help="Demonstrate sheaf reasoning")
    subparsers.add_parser("category", help="Demonstrate category theory")
    subparsers.add_parser("topology", help="Analyze proof topology")
    
    # Visualization
    viz_parser = subparsers.add_parser("visualize", help="Visualize proof graph")
    viz_parser.add_argument("-f", "--format", choices=["dot", "mermaid", "json"], help="Format")
    
    args = parser.parse_args()
    
    if args.command == "engine":
        cmd_engine(args)
    elif args.command == "verify":
        cmd_verify(args)
    elif args.command == "ai-status":
        cmd_ai_status(args)
    elif args.command == "sheaf":
        cmd_sheaf(args)
    elif args.command == "category":
        cmd_category(args)
    elif args.command == "topology":
        cmd_topology(args)
    elif args.command == "visualize":
        cmd_visualize(args)
    elif args.command == "all":
        cmd_all(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
