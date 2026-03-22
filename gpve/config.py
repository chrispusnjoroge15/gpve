"""Configuration for GPVE"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import os
import json


@dataclass
class AIConfig:
    """AI provider configuration"""
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    default_model: str = "gpt-4o"
    timeout: int = 60


@dataclass
class SMTConfig:
    """SMT solver configuration"""
    solver: str = "z3"
    timeout: int = 30
    random_seed: Optional[int] = None


@dataclass
class VisualizationConfig:
    """Visualization settings"""
    default_format: str = "mermaid"
    output_dir: str = "./output"
    theme: str = "default"


@dataclass
class GPVEConfig:
    """GPVE configuration"""
    ai: AIConfig = field(default_factory=AIConfig)
    smt: SMTConfig = field(default_factory=SMTConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    log_level: str = "INFO"
    workspace: str = "./workspace"


def load_config(config_path: str = "~/.gpve/config.json") -> GPVEConfig:
    """Load configuration from file"""
    path = os.path.expanduser(config_path)
    
    if not os.path.exists(path):
        return GPVEConfig()
    
    with open(path) as f:
        data = json.load(f)
    
    return GPVEConfig(
        ai=AIConfig(**data.get("ai", {})),
        smt=SMTConfig(**data.get("smt", {})),
        visualization=VisualizationConfig(**data.get("visualization", {})),
        log_level=data.get("log_level", "INFO"),
        workspace=data.get("workspace", "./workspace")
    )


def save_config(config: GPVEConfig, config_path: str = "~/.gpve/config.json") -> None:
    """Save configuration to file"""
    path = os.path.expanduser(config_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    data = {
        "ai": {
            "openai_api_key": config.ai.openai_api_key,
            "gemini_api_key": config.ai.gemini_api_key,
            "deepseek_api_key": config.ai.deepseek_api_key,
            "default_model": config.ai.default_model,
            "timeout": config.ai.timeout,
        },
        "smt": {
            "solver": config.smt.solver,
            "timeout": config.smt.timeout,
            "random_seed": config.smt.random_seed,
        },
        "visualization": {
            "default_format": config.visualization.default_format,
            "output_dir": config.visualization.output_dir,
            "theme": config.visualization.theme,
        },
        "log_level": config.log_level,
        "workspace": config.workspace,
    }
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def get_api_keys() -> Dict[str, str]:
    """Get API keys from environment"""
    return {
        "openai": os.environ.get("OPENAI_API_KEY"),
        "gemini": os.environ.get("GEMINI_API_KEY"),
        "deepseek": os.environ.get("DEEPSEEK_API_KEY"),
    }
