from typing import List, Dict, Any
from agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates between different agents"""
    
    def __init__(self):
        self.agents: List[BaseAgent] = []
        self.agent_priorities = {
            "DocumentAgent": 1,  # Highest priority for document queries
            "WeatherAgent": 2,
            "MeetingAgent": 3,
            "DatabaseAgent": 4
        }
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents.append(agent)
        logger.info(f"Registered agent: {agent.name}")
    
    def get_agent(self, agent_name: str) -> BaseAgent:
        """Get agent by name"""
        for agent in self.agents:
            if agent.name == agent_name:
                return agent
        return None
    
    async def route_query(self, query: str, user_id: str = None) -> Dict[str, Any]:
        """Route query to the most appropriate agent"""
        logger.info(f"Routing query: {query}")
        
        # Find agents that can handle the query
        capable_agents = []
        for agent in self.agents:
            if agent.can_handle(query):
                priority = self.agent_priorities.get(agent.name, 99)
                capable_agents.append((priority, agent))
        
        if not capable_agents:
            return {
                "success": False,
                "error": "No agent can handle this query",
                "suggestion": "Try asking about weather, meetings, or documents"
            }
        
        # Sort by priority (lower number = higher priority)
        capable_agents.sort(key=lambda x: x[0])
        
        # Try agents in order of priority
        tried_errors = {}
        for priority, agent in capable_agents:
            try:
                logger.info(f"Trying agent: {agent.name} (priority: {priority})")
                result = await agent.process(query, user_id=user_id)
                
                if result.get("success"):
                    result["orchestrator_choice"] = agent.name
                    result["alternatives_considered"] = [a.name for p, a in capable_agents if a != agent]
                    return result
                else:
                    error_msg = result.get('error', 'Unknown error')
                    logger.info(f"Agent {agent.name} failed: {error_msg}")
                    tried_errors[agent.name] = error_msg
                    
            except Exception as e:
                logger.error(f"Agent {agent.name} error: {str(e)}")
                tried_errors[agent.name] = str(e)
                continue
        
        # If all agents failed
        return {
            "success": False,
            "error": "All capable agents failed to process the query",
            "agents_tried": [a.name for p, a in capable_agents],
            "details": tried_errors
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all registered agents"""
        status = {
            "total_agents": len(self.agents),
            "agents": []
        }
        
        for agent in self.agents:
            status["agents"].append({
                "name": agent.name,
                "description": agent.description,
                "priority": self.agent_priorities.get(agent.name, "unknown")
            })
        
        return status