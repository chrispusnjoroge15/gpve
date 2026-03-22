"""Tests for GPVE core modules"""

import unittest
from gpve.core import (
    ProofGraph, Vertex, Edge, VertexType, EdgeType,
    SMTSolver, ProofKernel, GeometricProof
)


class TestProofGraph(unittest.TestCase):
    """Tests for ProofGraph"""
    
    def test_create_graph(self):
        graph = ProofGraph("test")
        self.assertEqual(graph.name, "test")
        self.assertEqual(len(graph.vertices), 0)
        self.assertEqual(len(graph.edges), 0)
    
    def test_add_vertex(self):
        graph = ProofGraph("test")
        v = graph.add_vertex("x > 0", VertexType.ASSUMPTION)
        
        self.assertEqual(len(graph.vertices), 1)
        self.assertEqual(v.statement, "x > 0")
        self.assertEqual(v.vertex_type, VertexType.ASSUMPTION)
    
    def test_add_edge(self):
        graph = ProofGraph("test")
        v1 = graph.add_vertex("P")
        v2 = graph.add_vertex("Q")
        e = graph.add_edge(v1.id, v2.id, rule_name="implies")
        
        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(e.rule_name, "implies")
    
    def test_topological_sort(self):
        graph = ProofGraph("test")
        v1 = graph.add_vertex("A")
        v2 = graph.add_vertex("B")
        v3 = graph.add_vertex("C")
        
        graph.add_edge(v1.id, v2.id)
        graph.add_edge(v2.id, v3.id)
        
        order = graph.topological_sort()
        statements = [v.statement for v in order]
        
        self.assertEqual(statements[0], "A")
        self.assertEqual(statements[-1], "C")


class TestSMTSolver(unittest.TestCase):
    """Tests for SMTSolver"""
    
    def test_create_solver(self):
        solver = SMTSolver()
        self.assertIsNotNone(solver)
    
    def test_bool_symbol(self):
        solver = SMTSolver()
        p = solver.Bool("p")
        self.assertIsNotNone(p)
    
    def test_int_symbol(self):
        solver = SMTSolver()
        x = solver.Int("x")
        self.assertIsNotNone(x)
    
    def test_simple_sat(self):
        solver = SMTSolver()
        x = solver.Int("x")
        
        solver.assert_formula(x > 0)
        solver.assert_formula(x < 10)
        
        result = solver.check()
        self.assertEqual(result.status, "sat")
    
    def test_unsat(self):
        solver = SMTSolver()
        x = solver.Int("x")
        
        solver.assert_formula(x > 0)
        solver.assert_formula(x < 0)
        
        result = solver.check()
        self.assertEqual(result.status, "unsat")


class TestProofKernel(unittest.TestCase):
    """Tests for ProofKernel"""
    
    def test_create_kernel(self):
        kernel = ProofKernel()
        self.assertIsNotNone(kernel)
    
    def test_assume(self):
        kernel = ProofKernel()
        term = kernel.assume("H1", "x > 0")
        
        self.assertEqual(term.name, "H1")
    
    def test_start_proof(self):
        kernel = ProofKernel()
        proof = kernel.start_proof("Theorem: P → P")
        
        self.assertEqual(proof.theorem, "Theorem: P → P")
        self.assertIsNotNone(proof.vertices)


class TestGeometricProof(unittest.TestCase):
    """Tests for GeometricProof"""
    
    def test_create_proof(self):
        proof = GeometricProof(theorem="P → P")
        
        self.assertEqual(proof.theorem, "P → P")
        self.assertEqual(len(proof.vertices), 0)
        self.assertEqual(len(proof.edges), 0)
    
    def test_add_vertex(self):
        proof = GeometricProof(theorem="test")
        vid = proof.add_vertex("x > 0")
        
        self.assertEqual(len(proof.vertices), 1)
        self.assertEqual(vid, "v0")


if __name__ == "__main__":
    unittest.main()
