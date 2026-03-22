"""Tests for GPVE category and AI modules"""

import unittest
from gpve.category import ProofCategory, HigherCategory, Object, Morphism
from gpve.ai import AIOrchestrator, AIProvider


class TestProofCategory(unittest.TestCase):
    """Tests for ProofCategory"""
    
    def test_create_category(self):
        cat = ProofCategory("test")
        self.assertEqual(cat.name, "test")
    
    def test_add_object(self):
        cat = ProofCategory("test")
        obj = cat.add_object("P")
        
        self.assertEqual(obj.name, "P")
        self.assertIn("P", cat.objects)
    
    def test_add_morphism(self):
        cat = ProofCategory("test")
        cat.add_object("P")
        cat.add_object("Q")
        morph = cat.add_morphism("P", "Q", "proof_1")
        
        self.assertEqual(morph.source, "P")
        self.assertEqual(morph.target, "Q")
    
    def test_get_proofs(self):
        cat = ProofCategory("test")
        cat.add_morphism("P", "Q", "f")
        cat.add_morphism("P", "Q", "g")
        
        proofs = cat.get_proofs("P", "Q")
        self.assertEqual(len(proofs), 2)
    
    def test_compose(self):
        cat = ProofCategory("test")
        cat.add_object("P")
        cat.add_object("Q")
        cat.add_object("R")
        
        f = cat.add_morphism("P", "Q", "f")
        g = cat.add_morphism("Q", "R", "g")
        
        h = cat.compose(f, g)
        self.assertIsNotNone(h)
        self.assertEqual(h.source, "P")
        self.assertEqual(h.target, "R")


class TestHigherCategory(unittest.TestCase):
    """Tests for HigherCategory"""
    
    def test_create_higher_category(self):
        cat = HigherCategory(dimension=2)
        self.assertEqual(cat.dimension, 2)
    
    def test_add_2_morphism(self):
        cat = HigherCategory(dimension=2)
        cat.add_object("P")
        cat.add_object("Q")
        
        f = cat.add_morphism("P", "Q", "f")
        g = cat.add_morphism("P", "Q", "g")
        
        two_morph = cat.add_2_morphism(f.id, g.id, "equiv")
        self.assertIsNotNone(two_morph)


class TestAIOrchestrator(unittest.TestCase):
    """Tests for AIOrchestrator"""
    
    def test_create_orchestrator(self):
        orch = AIOrchestrator()
        self.assertIsNotNone(orch.providers)
    
    def test_available(self):
        orch = AIOrchestrator()
        # Without API keys, should be empty or have errors
        avail = orch.available()
        self.assertIsInstance(avail, list)
    
    def test_generate_returns_dict(self):
        orch = AIOrchestrator()
        result = orch.generate("Hello")
        
        self.assertIsInstance(result, dict)


class TestGPVEEngine(unittest.TestCase):
    """Tests for the main GPVE Engine"""
    
    def test_create_engine(self):
        from gpve import GPVEEngine
        engine = GPVEEngine()
        
        self.assertIsNotNone(engine.smt_solver)
        self.assertIsNotNone(engine.proof_kernel)
        self.assertIsNotNone(engine.ai)
    
    def test_add_proposition(self):
        from gpve import GPVEEngine
        engine = GPVEEngine()
        
        engine.add_proposition("P")
        
        self.assertIn("P", engine.category.objects)
    
    def test_full_verify(self):
        from gpve import GPVEEngine
        from gpve.core import ProofGraph
        
        engine = GPVEEngine()
        graph = ProofGraph("test")
        v1 = graph.add_vertex("x > 0")
        v2 = graph.add_vertex("y > 0")
        v3 = graph.add_vertex("x + y > 0")
        
        result = engine.full_verify("x + y > 0", graph)
        
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
