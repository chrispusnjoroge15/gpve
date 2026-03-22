"""Tests for GPVE geometric modules"""

import unittest
from gpve.geometric import (
    SimplicialComplex, Simplex,
    HomotopyDetector, HomotopyClass,
    TopologicalProofEngine, ProofSpace
)
from gpve.core import ProofGraph


class TestSimplicialComplex(unittest.TestCase):
    """Tests for SimplicialComplex"""
    
    def test_create_complex(self):
        complex = SimplicialComplex("test")
        self.assertEqual(complex.name, "test")
        self.assertEqual(complex.dimension, 0)
    
    def test_add_simplex(self):
        complex = SimplicialComplex("test")
        s = complex.add_simplex([0, 1])
        
        self.assertEqual(s.dimension, 1)
        self.assertIn(s, complex.simplices)
    
    def test_get_vertices(self):
        complex = SimplicialComplex("test")
        complex.add_simplex([0])
        complex.add_simplex([1])
        complex.add_simplex([0, 1])
        
        vertices = complex.get_vertices()
        self.assertEqual(len(vertices), 2)


class TestSimplex(unittest.TestCase):
    """Tests for Simplex"""
    
    def test_create_simplex(self):
        s = Simplex((0, 1, 2))
        self.assertEqual(s.dimension, 2)
    
    def test_faces(self):
        s = Simplex((0, 1, 2))
        faces = s.faces()
        
        self.assertEqual(len(faces), 3)  # 3 faces of a triangle


class TestHomotopyDetector(unittest.TestCase):
    """Tests for HomotopyDetector"""
    
    def test_create_detector(self):
        detector = HomotopyDetector()
        self.assertIsNotNone(detector)
    
    def test_add_edge(self):
        detector = HomotopyDetector()
        detector.add_edge("A", "B")
        
        self.assertIn("B", detector.vertex_graph["A"])
    
    def test_find_paths(self):
        detector = HomotopyDetector()
        detector.add_edge("A", "B")
        detector.add_edge("B", "C")
        
        paths = detector.find_all_paths("A", "C")
        self.assertGreater(len(paths), 0)


class TestTopologicalProofEngine(unittest.TestCase):
    """Tests for TopologicalProofEngine"""
    
    def test_create_engine(self):
        engine = TopologicalProofEngine()
        self.assertEqual(len(engine.spaces), 0)
    
    def test_build_proof_space(self):
        engine = TopologicalProofEngine()
        graph = ProofGraph("test")
        v1 = graph.add_vertex("P")
        v2 = graph.add_vertex("Q")
        graph.add_edge(v1.id, v2.id)
        
        space = engine.build_proof_space(graph)
        
        self.assertIsNotNone(space)
        self.assertIn("test", engine.spaces)


if __name__ == "__main__":
    unittest.main()
