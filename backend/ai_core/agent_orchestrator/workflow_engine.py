"""Workflow engine — defines and executes multi-step agent workflows."""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from enum import Enum
from loguru import logger


class StepType(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class WorkflowStep:
    def __init__(self, name: str, agent: str, method: str, params: Dict = None,
                 condition: Optional[str] = None):
        self.name = name
        self.agent = agent
        self.method = method
        self.params = params or {}
        self.condition = condition
        self.result: Any = None
        self.status: str = "pending"


class Workflow:
    def __init__(self, name: str, steps: List[WorkflowStep], step_type: StepType = StepType.SEQUENTIAL):
        self.workflow_id = str(uuid.uuid4())[:12]
        self.name = name
        self.steps = steps
        self.step_type = step_type
        self.status = "created"
        self.results: Dict[str, Any] = {}


class WorkflowEngine:
    """Executes multi-step agent workflows with sequential, parallel, and conditional support."""

    PREDEFINED_WORKFLOWS = {
        "full_analysis": [
            WorkflowStep("analyze", "market_analysis", "analyze", {"symbol": "NIFTY"}),
            WorkflowStep("discover", "strategy_discovery", "discover", {"symbol": "NIFTY"}),
            WorkflowStep("backtest", "backtesting", "backtest", {}),
            WorkflowStep("risk_check", "risk_management", "check", {}),
        ],
        "quick_scan": [
            WorkflowStep("analyze", "market_analysis", "analyze", {"symbol": "NIFTY"}),
            WorkflowStep("report", "reporting", "generate", {}),
        ],
    }

    def __init__(self):
        self._active_workflows: Dict[str, Workflow] = {}

    async def execute(self, workflow: Workflow, orchestrator) -> Dict[str, Any]:
        """Execute a workflow using the orchestrator's agent pool."""
        self._active_workflows[workflow.workflow_id] = workflow
        workflow.status = "running"
        logger.info(f"Workflow started: {workflow.name} ({workflow.workflow_id})")

        try:
            if workflow.step_type == StepType.PARALLEL:
                await self._run_parallel(workflow, orchestrator)
            else:
                await self._run_sequential(workflow, orchestrator)

            workflow.status = "completed"
        except Exception as e:
            workflow.status = "failed"
            logger.error(f"Workflow failed: {e}")

        return {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status,
            "results": workflow.results,
        }

    async def _run_sequential(self, workflow: Workflow, orchestrator):
        for step in workflow.steps:
            if step.condition and not self._evaluate_condition(step.condition, workflow.results):
                step.status = "skipped"
                continue

            step.status = "running"
            try:
                agent = orchestrator._agents.get(step.agent)
                if agent and hasattr(agent, step.method):
                    # Merge previous results into params
                    params = {**step.params}
                    if workflow.results:
                        params["previous_results"] = workflow.results
                    step.result = await getattr(agent, step.method)(**params)
                else:
                    step.result = {"error": f"Agent '{step.agent}' or method '{step.method}' not found"}
                step.status = "completed"
            except Exception as e:
                step.result = {"error": str(e)}
                step.status = "failed"
                logger.error(f"Step '{step.name}' failed: {e}")

            workflow.results[step.name] = step.result

    async def _run_parallel(self, workflow: Workflow, orchestrator):
        tasks = []
        for step in workflow.steps:
            tasks.append(self._run_step(step, orchestrator))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for step, result in zip(workflow.steps, results):
            if isinstance(result, Exception):
                step.result = {"error": str(result)}
                step.status = "failed"
            workflow.results[step.name] = step.result

    async def _run_step(self, step: WorkflowStep, orchestrator):
        step.status = "running"
        try:
            agent = orchestrator._agents.get(step.agent)
            if agent and hasattr(agent, step.method):
                step.result = await getattr(agent, step.method)(**step.params)
            else:
                step.result = {"error": f"Agent or method not found"}
            step.status = "completed"
        except Exception as e:
            step.result = {"error": str(e)}
            step.status = "failed"

    def _evaluate_condition(self, condition: str, results: Dict) -> bool:
        """Simple condition evaluation based on previous step results."""
        try:
            return eval(condition, {"__builtins__": {}}, {"results": results})
        except Exception:
            return True

    def create_workflow(self, name: str, symbol: str = "NIFTY") -> Workflow:
        """Create a workflow from predefined templates."""
        template = self.PREDEFINED_WORKFLOWS.get(name)
        if not template:
            return Workflow(name=name, steps=[])
        # Clone steps with symbol override
        steps = []
        for s in template:
            params = {**s.params, "symbol": symbol}
            steps.append(WorkflowStep(s.name, s.agent, s.method, params, s.condition))
        return Workflow(name=name, steps=steps)

    def get_active_workflows(self) -> List[Dict]:
        return [
            {"workflow_id": w.workflow_id, "name": w.name, "status": w.status}
            for w in self._active_workflows.values()
        ]
