"""SMT Solver Interface - Z3 and CVC5 integration"""

from __future__ import annotations
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

try:
    from z3 import (Solver, sat, unsat, unknown, Bool, Int, Real, Function, 
                  Const, Exists, ForAll, And, Or, Not, Implies, If)
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    logger.warning("Z3 not available - install z3-solver")


class SolverType(Enum):
    Z3 = "z3"
    CVC5 = "cvc5"


@dataclass
class SMTRESULT:
    """Result from SMT solver"""
    status: str  # sat, unsat, unknown
    model: Optional[Dict[str, Any]] = None
    proof: Optional[Any] = None
    stats: Dict[str, Any] = None


class SMTSolver:
    """
    Interface to SMT solvers (Z3 primary, CVC5 planned)
    
    Supports:
    - Propositional logic
    - Integer/Real arithmetic
    - Quantifiers (limited)
    - Arrays, functions
    """
    
    def __init__(self, solver_type: SolverType = SolverType.Z3):
        if not Z3_AVAILABLE and solver_type == SolverType.Z3:
            raise ImportError("Z3 not installed. Run: pip install z3-solver")
        
        self.solver_type = solver_type
        self.solver = Solver()
        self.symbols: Dict[str, Any] = {}
        self.assertions: List[Any] = []
    
    def Bool(self, name: str) -> Any:
        """Create a Boolean symbol"""
        if name not in self.symbols:
            self.symbols[name] = Bool(name)
        return self.symbols[name]
    
    def Int(self, name: str) -> Any:
        """Create an Integer symbol"""
        if name not in self.symbols:
            self.symbols[name] = Int(name)
        return self.symbols[name]
    
    def Real(self, name: str) -> Any:
        """Create a Real symbol"""
        if name not in self.symbols:
            self.symbols[name] = Real(name)
        return self.symbols[name]
    
    def assert_formula(self, formula: Any) -> None:
        """Add an assertion to the solver"""
        self.assertions.append(formula)
        self.solver.add(formula)
    
    def check(self) -> SMTRESULT:
        """Check satisfiability of current assertions"""
        result = self.solver.check()
        
        if result == sat:
            model = self.solver.model()
            model_dict = {
                str(d): str(model[d]) 
                for d in model.decls()
            }
            return SMTRESULT(status="sat", model=model_dict)
        elif result == unsat:
            return SMTRESULT(status="unsat")
        else:
            return SMTRESULT(status="unknown")
    
    def check_assumptions(self, assumptions: List[Any]) -> SMTRESULT:
        """Check satisfiability with additional assumptions"""
        result = self.solver.check(*assumptions)
        
        if result == sat:
            model = self.solver.model()
            model_dict = {
                str(d): str(model[d]) 
                for d in model.decls()
            }
            return SMTRESULT(status="sat", model=model_dict)
        elif result == unsat:
            return SMTRESULT(status="unsat")
        else:
            return SMTRESULT(status="unknown")
    
    def push(self) -> None:
        """Push a new scope (for backtracking)"""
        self.solver.push()
    
    def pop(self) -> None:
        """Pop the current scope"""
        self.solver.pop()
    
    def reset(self) -> None:
        """Reset solver state"""
        self.solver.reset()
        self.assertions = []
        self.symbols = {}
    
    def get_model(self) -> Optional[Dict[str, Any]]:
        """Get the current model (if sat)"""
        model = self.solver.model()
        if model is None:
            return None
        return {str(d): str(model[d]) for d in model.decls()}
    
    # Convenience methods for common operations
    
    def assert_true(self, formula: Any) -> None:
        """Assert that a formula must be true"""
        self.assert_formula(formula)
    
    def assert_equals(self, left: Any, right: Any) -> None:
        """Assert left == right"""
        self.assert_formula(left == right)
    
    def assert_notequals(self, left: Any, right: Any) -> None:
        """Assert left != right"""
        self.assert_formula(left != right)
    
    def assert_greater(self, left: Any, right: Any) -> None:
        """Assert left > right"""
        self.assert_formula(left > right)
    
    def assert_less(self, left: Any, right: Any) -> None:
        """Assert left < right"""
        self.assert_formula(left < right)
    
    def assert_and(self, *formulas: Any) -> None:
        """Assert conjunction of formulas"""
        self.assert_formula(And(*formulas))
    
    def assert_or(self, *formulas: Any) -> None:
        """Assert disjunction of formulas"""
        self.assert_formula(Or(*formulas))
    
    def assert_not(self, formula: Any) -> None:
        """Assert negation of formula"""
        self.assert_formula(Not(formula))
    
    def assert_implies(self, antecedent: Any, consequent: Any) -> None:
        """Assert antecedent implies consequent"""
        self.assert_formula(Implies(antecedent, consequent))
    
    def exists(self, var: Any, body: Any) -> Any:
        """Create existential quantifier"""
        return Exists(var, body)
    
    def forall(self, var: Any, body: Any) -> Any:
        """Create universal quantifier"""
        return ForAll(var, body)
    
    # Example problem solvers
    
    def solve_linear_inequality(self, x: Any, y: Any, 
                                 constraint: str = "x + y > 10") -> SMTRESULT:
        """Solve a simple linear inequality"""
        x, y = self.Int(x), self.Int(y)
        
        if constraint == "x + y > 10":
            self.assert_formula(x > 0)
            self.assert_formula(y > 0)
            self.assert_formula(x + y > 10)
        
        return self.check()
    
    def prove(self, formula: Any) -> bool:
        """
        Attempt to prove a formula by checking unsatisfiability of its negation.
        Returns True if the formula is provable (unsat when negated).
        """
        self.solver.push()
        self.solver.add(Not(formula))
        result = self.solver.check()
        self.solver.pop()
        
        return result == unsat
    
    def __repr__(self):
        return f"SMTSolver(type={self.solver_type.value}, assertions={len(self.assertions)})"


# Convenience function for quick SAT checks
def sat_check(*formulas: Any, solver: Optional[SMTSolver] = None) -> SMTRESULT:
    """Quickly check if formulas are satisfiable"""
    if solver is None:
        solver = SMTSolver()
    
    for formula in formulas:
        solver.assert_formula(formula)
    
    return solver.check()
