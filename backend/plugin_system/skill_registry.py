"""Skill registry — agents register callable skills discoverable by other agents."""

from typing import Dict, Any, List, Optional, Callable
from loguru import logger

_registry = None


class Skill:
    """A registered callable skill."""

    def __init__(self, name: str, description: str, handler: Callable,
                 input_schema: Dict = None, output_schema: Dict = None,
                 owner: str = "system"):
        self.name = name
        self.description = description
        self.handler = handler
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}
        self.owner = owner

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "owner": self.owner,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }


class SkillRegistry:
    """Central registry where agents register callable skills."""

    def __init__(self):
        self._skills: Dict[str, Skill] = {}

    def register(self, name: str, description: str, handler: Callable,
                 input_schema: Dict = None, output_schema: Dict = None,
                 owner: str = "system"):
        """Register a new skill."""
        skill = Skill(name, description, handler, input_schema, output_schema, owner)
        self._skills[name] = skill
        logger.info(f"Skill registered: {name} (owner: {owner})")

    def unregister(self, name: str):
        """Remove a skill from the registry."""
        if name in self._skills:
            del self._skills[name]
            logger.info(f"Skill unregistered: {name}")

    def get(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)

    async def execute(self, name: str, params: Dict[str, Any] = None) -> Any:
        """Execute a registered skill by name."""
        skill = self._skills.get(name)
        if not skill:
            return {"error": f"Skill '{name}' not found"}
        try:
            import asyncio
            if asyncio.iscoroutinefunction(skill.handler):
                return await skill.handler(**(params or {}))
            else:
                return skill.handler(**(params or {}))
        except Exception as e:
            logger.error(f"Skill execution failed ({name}): {e}")
            return {"error": str(e)}

    def list_skills(self, owner: Optional[str] = None) -> List[Dict]:
        """List all registered skills, optionally filtered by owner."""
        skills = self._skills.values()
        if owner:
            skills = [s for s in skills if s.owner == owner]
        return [s.to_dict() for s in skills]

    def search(self, query: str) -> List[Dict]:
        """Search skills by name or description."""
        query_lower = query.lower()
        return [
            s.to_dict() for s in self._skills.values()
            if query_lower in s.name.lower() or query_lower in s.description.lower()
        ]


def get_skill_registry() -> SkillRegistry:
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry
