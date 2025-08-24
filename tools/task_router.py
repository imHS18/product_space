"""
Task Router Tool
Routes tasks to appropriate agents and manages workload distribution
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from crewai.tools import BaseTool

logger = logging.getLogger(__name__)


class TaskRouter(BaseTool):
    """Tool for routing tasks to appropriate agents and managing workload distribution"""
    
    name: str = "Task Router"
    description: str = "Routes tasks to appropriate agents and manages workload distribution across the multi-agent system."
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'agent_capacities', {
            "sentiment_analyst": {"max_concurrent": 5, "current_load": 0},
            "alert_manager": {"max_concurrent": 3, "current_load": 0},
            "response_generator": {"max_concurrent": 4, "current_load": 0},
            "integration_coordinator": {"max_concurrent": 2, "current_load": 0},
            "orchestrator": {"max_concurrent": 10, "current_load": 0}
        })
        
        object.__setattr__(self, 'task_priorities', {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        })
        
        object.__setattr__(self, 'task_queue', [])
    
    def _run(self, task_type: str, priority: str) -> str:
        """Required method for CrewAI BaseTool - entry point for the tool"""
        # In practice, you'd convert the strings back to proper types or handle JSON
        # For now, returning a simple task routing result
        return f"Task {task_type} routed with priority {priority}"
    
    def route_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a task to the appropriate agent
        
        Args:
            task_data: Task information including type, priority, and data
            
        Returns:
            Dictionary with routing information
        """
        try:
            task_type = task_data.get("task_type", "unknown")
            priority = task_data.get("priority", "medium")
            task_id = task_data.get("task_id", f"task_{datetime.now().timestamp()}")
            
            # Determine appropriate agent for task type
            agent_assignment = self._determine_agent_assignment(task_type, priority)
            
            # Check agent availability
            availability = self._check_agent_availability(agent_assignment["agent"])
            
            # Create routing plan
            routing_plan = self._create_routing_plan(
                task_id, task_type, priority, agent_assignment, availability
            )
            
            # Add to task queue if needed
            if not availability["available"]:
                self._add_to_queue(task_data, routing_plan)
            
            return {
                "task_id": task_id,
                "routing_plan": routing_plan,
                "agent_assignment": agent_assignment,
                "availability": availability,
                "estimated_start_time": self._estimate_start_time(availability, priority)
            }
            
        except Exception as e:
            logger.error(f"Error routing task: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _determine_agent_assignment(self, task_type: str, priority: str) -> Dict[str, Any]:
        """Determine which agent should handle the task"""
        
        # Task type to agent mapping
        task_agent_mapping = {
            "sentiment_analysis": "sentiment_analyst",
            "risk_assessment": "alert_manager",
            "response_generation": "response_generator",
            "integration": "integration_coordinator",
            "orchestration": "orchestrator",
            "escalation": "alert_manager",
            "notification": "integration_coordinator"
        }
        
        # Default agent assignment
        assigned_agent = task_agent_mapping.get(task_type, "orchestrator")
        
        # Priority-based adjustments
        if priority == "critical":
            # Critical tasks might need multiple agents or special handling
            if task_type in ["sentiment_analysis", "risk_assessment"]:
                assigned_agent = "alert_manager"  # Escalate to alert manager for critical cases
        
        return {
            "agent": assigned_agent,
            "task_type": task_type,
            "priority": priority,
            "requires_backup": priority == "critical"
        }
    
    def _check_agent_availability(self, agent_name: str) -> Dict[str, Any]:
        """Check if agent is available to handle tasks"""
        agent_info = self.agent_capacities.get(agent_name, {"max_concurrent": 1, "current_load": 0})
        
        current_load = agent_info["current_load"]
        max_capacity = agent_info["max_concurrent"]
        
        availability = {
            "agent": agent_name,
            "current_load": current_load,
            "max_capacity": max_capacity,
            "available_capacity": max_capacity - current_load,
            "utilization": (current_load / max_capacity) * 100 if max_capacity > 0 else 0,
            "available": current_load < max_capacity
        }
        
        # Determine backup agent if needed
        if not availability["available"]:
            availability["backup_agent"] = self._get_backup_agent(agent_name)
            availability["backup_available"] = self._check_agent_availability(
                availability["backup_agent"]
            )["available"]
        
        return availability
    
    def _get_backup_agent(self, primary_agent: str) -> str:
        """Get backup agent if primary agent is unavailable"""
        backup_mapping = {
            "sentiment_analyst": "orchestrator",
            "alert_manager": "orchestrator",
            "response_generator": "orchestrator",
            "integration_coordinator": "orchestrator",
            "orchestrator": "sentiment_analyst"  # Fallback to sentiment analyst
        }
        return backup_mapping.get(primary_agent, "orchestrator")
    
    def _create_routing_plan(self, task_id: str, task_type: str, priority: str,
                           agent_assignment: Dict[str, Any], 
                           availability: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed routing plan for the task"""
        
        plan = {
            "task_id": task_id,
            "primary_agent": agent_assignment["agent"],
            "backup_agent": availability.get("backup_agent"),
            "priority": priority,
            "estimated_processing_time": self._estimate_processing_time(task_type, priority),
            "routing_strategy": "direct" if availability["available"] else "queued",
            "created_at": datetime.now().isoformat()
        }
        
        # Add priority-specific routing details
        if priority == "critical":
            plan["routing_strategy"] = "immediate"
            plan["requires_escalation"] = True
            plan["notification_channels"] = ["slack_urgent", "email_urgent"]
        elif priority == "high":
            plan["routing_strategy"] = "priority_queue"
            plan["requires_escalation"] = False
            plan["notification_channels"] = ["slack_high"]
        else:
            plan["routing_strategy"] = "standard_queue"
            plan["requires_escalation"] = False
            plan["notification_channels"] = ["email_standard"]
        
        return plan
    
    def _estimate_processing_time(self, task_type: str, priority: str) -> int:
        """Estimate processing time for task in seconds"""
        base_times = {
            "sentiment_analysis": 2,
            "risk_assessment": 1,
            "response_generation": 3,
            "integration": 1,
            "orchestration": 1,
            "escalation": 2,
            "notification": 1
        }
        
        base_time = base_times.get(task_type, 2)
        
        # Priority adjustments
        if priority == "critical":
            base_time = max(1, base_time // 2)  # Critical tasks get priority processing
        elif priority == "low":
            base_time = base_time * 2  # Low priority tasks may take longer
        
        return base_time
    
    def _estimate_start_time(self, availability: Dict[str, Any], priority: str) -> str:
        """Estimate when task will start processing"""
        if availability["available"]:
            return datetime.now().isoformat()
        
        # Calculate queue position and estimated wait time
        queue_position = len(self.task_queue)
        estimated_wait_minutes = queue_position * 2  # Rough estimate
        
        # Priority adjustments
        if priority == "critical":
            estimated_wait_minutes = max(1, estimated_wait_minutes // 4)
        elif priority == "high":
            estimated_wait_minutes = max(1, estimated_wait_minutes // 2)
        
        estimated_start = datetime.now() + timedelta(minutes=estimated_wait_minutes)
        return estimated_start.isoformat()
    
    def _add_to_queue(self, task_data: Dict[str, Any], routing_plan: Dict[str, Any]):
        """Add task to processing queue"""
        queue_item = {
            "task_data": task_data,
            "routing_plan": routing_plan,
            "queued_at": datetime.now(),
            "priority_score": self._calculate_priority_score(
                task_data.get("priority", "medium")
            )
        }
        
        self.task_queue.append(queue_item)
        
        # Sort queue by priority (lower score = higher priority)
        self.task_queue.sort(key=lambda x: x["priority_score"])
        
        logger.info(f"Task {task_data.get('task_id', 'unknown')} added to queue")
    
    def _calculate_priority_score(self, priority: str) -> int:
        """Calculate priority score for queue sorting"""
        return self.task_priorities.get(priority, 4)
    
    def get_next_task(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get next available task for an agent"""
        for i, queue_item in enumerate(self.task_queue):
            routing_plan = queue_item["routing_plan"]
            
            # Check if this task is for the requesting agent
            if (routing_plan["primary_agent"] == agent_name or 
                routing_plan["backup_agent"] == agent_name):
                
                # Remove from queue and return
                task = self.task_queue.pop(i)
                return task
        
        return None
    
    def update_agent_load(self, agent_name: str, load_change: int = 1):
        """Update agent load (called when tasks start/complete)"""
        if agent_name in self.agent_capacities:
            current_load = self.agent_capacities[agent_name]["current_load"]
            self.agent_capacities[agent_name]["current_load"] = max(0, current_load + load_change)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and queue information"""
        total_queue_length = len(self.task_queue)
        
        # Calculate queue statistics
        priority_counts = {}
        for item in self.task_queue:
            priority = item["task_data"].get("priority", "medium")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Calculate agent utilization
        agent_utilization = {}
        for agent, info in self.agent_capacities.items():
            utilization = (info["current_load"] / info["max_concurrent"]) * 100 if info["max_concurrent"] > 0 else 0
            agent_utilization[agent] = {
                "current_load": info["current_load"],
                "max_capacity": info["max_concurrent"],
                "utilization_percent": utilization,
                "available": info["current_load"] < info["max_concurrent"]
            }
        
        return {
            "queue_length": total_queue_length,
            "queue_priority_distribution": priority_counts,
            "agent_utilization": agent_utilization,
            "system_health": self._assess_system_health(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _assess_system_health(self) -> str:
        """Assess overall system health"""
        total_queue_length = len(self.task_queue)
        
        # Check for critical issues
        if total_queue_length > 100:
            return "critical"
        elif total_queue_length > 50:
            return "warning"
        elif total_queue_length > 20:
            return "degraded"
        else:
            return "healthy"
    
    def clear_queue(self, priority: Optional[str] = None) -> Dict[str, Any]:
        """Clear tasks from queue (for maintenance or emergency)"""
        if priority:
            # Clear only tasks of specific priority
            original_length = len(self.task_queue)
            self.task_queue = [item for item in self.task_queue 
                             if item["task_data"].get("priority") != priority]
            cleared_count = original_length - len(self.task_queue)
        else:
            # Clear all tasks
            cleared_count = len(self.task_queue)
            self.task_queue = []
        
        logger.info(f"Cleared {cleared_count} tasks from queue")
        
        return {
            "success": True,
            "cleared_count": cleared_count,
            "remaining_tasks": len(self.task_queue)
        }
