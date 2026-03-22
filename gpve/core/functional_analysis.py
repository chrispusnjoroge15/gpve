"""Functional Analysis Layer - Stability and convergence verification of AI models"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
import numpy as np


@dataclass
class Metric:
    """A metric for analyzing model behavior"""
    name: str
    value: float
    timestamp: float = 0.0


@dataclass
class StabilityResult:
    """Result of stability analysis"""
    is_stable: bool
    bound: float
    lyapunov_exponent: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)


class FunctionalAnalyzer:
    """
    Functional analysis for AI models.
    
    Capabilities:
    - Stability analysis (Lyapunov exponents)
    - Convergence verification
    - Fixed point detection
    - Sensitivity analysis
    """
    
    def __init__(self):
        self.metrics: List[Metric] = []
        self.history: Dict[str, List[float]] = {}
    
    def add_metric(self, name: str, value: float) -> None:
        """Add a metric observation"""
        self.metrics.append(Metric(name=name, value=value))
        
        if name not in self.history:
            self.history[name] = []
        self.history[name].append(value)
    
    def compute_gradient_norm(self, grads: np.ndarray) -> float:
        """Compute gradient norm"""
        return float(np.linalg.norm(grads))
    
    def check_convergence(self, values: List[float], tolerance: float = 1e-6) -> bool:
        """Check if a sequence has converged"""
        if len(values) < 2:
            return False
        
        # Check difference between consecutive values
        diffs = np.abs(np.diff(values))
        return np.all(diffs < tolerance)
    
    def estimate_lyapunov_exponent(
        self, 
        trajectory: np.ndarray, 
        delta: float = 1e-5
    ) -> float:
        """
        Estimate Lyapunov exponent from trajectory.
        
        Positive exponent = chaotic/unstable
        Negative exponent = stable/contracting
        """
        if len(trajectory) < 2:
            return 0.0
        
        # Simplified: use log of expansion rates
        rates = []
        for i in range(len(trajectory) - 1):
            dist = np.abs(trajectory[i + 1] - trajectory[i])
            if dist > delta:
                rates.append(np.log(dist / delta))
        
        if rates:
            return float(np.mean(rates))
        return 0.0
    
    def analyze_stability(
        self, 
        dynamics: Callable[[np.ndarray], np.ndarray],
        initial_state: np.ndarray,
        n_iterations: int = 100
    ) -> StabilityResult:
        """
        Analyze stability of a dynamical system.
        
        Uses Lyapunov exponent estimation.
        """
        # Generate trajectory
        trajectory = [initial_state.copy()]
        state = initial_state.copy()
        
        for _ in range(n_iterations):
            state = dynamics(state)
            trajectory.append(state.copy())
        
        trajectory = np.array(trajectory)
        
        # Flatten for analysis
        flat_trajectory = trajectory.flatten()
        
        # Estimate Lyapunov exponent
        lyap_exp = self.estimate_lyapunov_exponent(flat_trajectory)
        
        # Determine stability
        is_stable = lyap_exp < 0
        
        return StabilityResult(
            is_stable=is_stable,
            bound=float(np.max(np.abs(trajectory))),
            lyapunov_exponent=lyap_exp,
            details={
                "n_iterations": n_iterations,
                "final_state": trajectory[-1].tolist(),
            }
        )
    
    def sensitivity_analysis(
        self,
        model: Callable[[np.ndarray], np.ndarray],
        input_dim: int,
        n_samples: int = 100
    ) -> Dict[str, float]:
        """
        Perform sensitivity analysis on model inputs.
        
        Returns sensitivity scores for each input dimension.
        """
        sensitivities = []
        
        base_input = np.zeros(input_dim)
        base_output = model(base_input)
        
        for _ in range(n_samples):
            # Random perturbation
            perturbation = np.random.randn(input_dim) * 0.1
            perturbed_output = model(base_input + perturbation)
            
            # Compute output difference
            diff = np.linalg.norm(perturbed_output - base_output)
            sensitivities.append(diff)
        
        return {
            "mean_sensitivity": float(np.mean(sensitivities)),
            "max_sensitivity": float(np.max(sensitivities)),
            "std_sensitivity": float(np.std(sensitivities)),
        }
    
    def find_fixed_points(
        self,
        dynamics: Callable[[np.ndarray], np.ndarray],
        initial_guesses: List[np.ndarray],
        tolerance: float = 1e-6,
        max_iterations: int = 100
    ) -> List[np.ndarray]:
        """
        Find fixed points of a dynamical system.
        
        Uses simple iteration from multiple initial guesses.
        """
        fixed_points = []
        
        for initial in initial_guesses:
            state = initial.copy()
            
            for _ in range(max_iterations):
                new_state = dynamics(state)
                
                if np.linalg.norm(new_state - state) < tolerance:
                    # Found fixed point - check if not already found
                    is_new = True
                    for fp in fixed_points:
                        if np.linalg.norm(fp - new_state) < tolerance:
                            is_new = False
                            break
                    
                    if is_new:
                        fixed_points.append(new_state)
                    break
                
                state = new_state
        
        return fixed_points
    
    def verify_boundedness(
        self,
        trajectory: np.ndarray,
        bound: float
    ) -> bool:
        """Verify trajectory stays within bound"""
        return np.all(np.abs(trajectory) < bound)
    
    def __repr__(self):
        return f"FunctionalAnalyzer(metrics={len(self.metrics)})"


class ConvergenceVerifier:
    """
    Verifies convergence of iterative algorithms/proofs.
    """
    
    def __init__(self):
        self.traces: Dict[str, List[float]] = {}
    
    def add_trace(self, name: str, value: float) -> None:
        if name not in self.traces:
            self.traces[name] = []
        self.traces[name].append(value)
    
    def verify_monotone_convergence(
        self, 
        trace: List[float], 
        direction: str = "decrease"
    ) -> bool:
        """Verify monotonic convergence"""
        if len(trace) < 2:
            return True
        
        diffs = np.diff(trace)
        
        if direction == "decrease":
            return np.all(diffs <= 0)
        else:
            return np.all(diffs >= 0)
    
    def verify_rate(
        self, 
        trace: List[float], 
        expected_rate: float
    ) -> Dict[str, Any]:
        """Verify convergence rate matches expected"""
        if len(trace) < 3:
            return {"verified": False, "reason": "insufficient data"}
        
        # Estimate actual rate via linear regression on log errors
        errors = np.abs(np.array(trace[1:]) - trace[-1])
        errors = errors[errors > 1e-10]  # Filter zeros
        
        if len(errors) < 2:
            return {"verified": False, "reason": "no convergence"}
        
        log_errors = np.log(errors)
        indices = np.arange(len(log_errors))
        
        # Linear fit
        coeffs = np.polyfit(indices, log_errors, 1)
        actual_rate = coeffs[0]
        
        return {
            "verified": abs(actual_rate - expected_rate) < 0.5,
            "expected_rate": expected_rate,
            "actual_rate": float(actual_rate),
        }
    
    def __repr__(self):
        return f"ConvergenceVerifier(traces={list(self.traces.keys())})"
