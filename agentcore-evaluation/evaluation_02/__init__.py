"""
AgentCore Evaluation Agent 02

A production-ready agent with observability and built-in evaluators.
"""

__version__ = "1.0.0"
__author__ = "AgentCore Team"

from .agent import agent_invocation
from .evaluation_config import get_evaluation_config, get_enabled_evaluator_names

__all__ = [
    'agent_invocation',
    'get_evaluation_config',
    'get_enabled_evaluator_names'
]
