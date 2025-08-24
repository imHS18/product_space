"""
Escalation Router Tool
Determines appropriate escalation paths and response channels based on risk assessment
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from crewai.tools import BaseTool

logger = logging.getLogger(__name__)


class EscalationRouter(BaseTool):
    """Tool for routing escalations to appropriate channels and teams"""
    
    name: str = "Escalation Router"
    description: str = "Determines appropriate escalation paths and response channels based on risk assessment and customer context."
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'escalation_paths', {
            "critical": {
                "immediate_actions": ["senior_support", "manager_alert", "executive_notification"],
                "response_time": "immediate",
                "channels": ["slack_urgent", "email_urgent", "phone_call"],
                "team": "crisis_response"
            },
            "high": {
                "immediate_actions": ["senior_support", "manager_alert"],
                "response_time": "2_hours",
                "channels": ["slack_high", "email_high"],
                "team": "senior_support"
            },
            "medium": {
                "immediate_actions": ["tier_2_support"],
                "response_time": "4_hours",
                "channels": ["slack_medium", "email_standard"],
                "team": "tier_2_support"
            },
            "low": {
                "immediate_actions": ["standard_support"],
                "response_time": "24_hours",
                "channels": ["email_standard"],
                "team": "standard_support"
            }
        })
        
        object.__setattr__(self, 'team_capacities', {
            "crisis_response": {"max_active": 5, "current_load": 0},
            "senior_support": {"max_active": 15, "current_load": 0},
            "tier_2_support": {"max_active": 30, "current_load": 0},
            "standard_support": {"max_active": 100, "current_load": 0}
        })
    
    def _run(self, risk_assessment: str, ticket_data: str) -> str:
        """Required method for CrewAI BaseTool - entry point for the tool"""
        # In practice, you'd convert the strings back to dicts or handle JSON
        # For now, returning a simple escalation routing
        return "Escalation routing completed"
    
    def route_escalation(self, risk_assessment: Dict[str, Any], ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route escalation to appropriate channels and teams
        
        Args:
            risk_assessment: Results from risk assessment
            ticket_data: Customer ticket information
            
        Returns:
            Dictionary with escalation routing information
        """
        try:
            risk_level = risk_assessment.get("risk_level", "low")
            overall_risk = risk_assessment.get("overall_risk", 0.0)
            priority_score = risk_assessment.get("priority_score", 0.0)
            
            # Get escalation path
            escalation_path = self.escalation_paths.get(risk_level, self.escalation_paths["low"])
            
            # Determine specific routing based on customer context
            routing_details = self._determine_routing_details(
                risk_level, overall_risk, priority_score, ticket_data, escalation_path
            )
            
            # Check team availability
            team_availability = self._check_team_availability(routing_details["assigned_team"])
            
            # Generate escalation plan
            escalation_plan = self._generate_escalation_plan(
                routing_details, team_availability, risk_assessment
            )
            
            return {
                "escalation_level": risk_level,
                "routing_details": routing_details,
                "team_availability": team_availability,
                "escalation_plan": escalation_plan,
                "response_channels": routing_details["channels"],
                "estimated_response_time": routing_details["response_time"],
                "priority_override": self._check_priority_override(ticket_data, risk_level)
            }
            
        except Exception as e:
            logger.error(f"Error in escalation routing: {e}")
            return {
                "escalation_level": "unknown",
                "error": str(e),
                "routing_details": self.escalation_paths["low"]
            }
    
    def _determine_routing_details(self, risk_level: str, overall_risk: float, 
                                 priority_score: float, ticket_data: Dict[str, Any],
                                 escalation_path: Dict[str, Any]) -> Dict[str, Any]:
        """Determine specific routing details based on context"""
        
        # Base routing from escalation path
        routing = {
            "assigned_team": escalation_path["team"],
            "response_time": escalation_path["response_time"],
            "channels": escalation_path["channels"].copy(),
            "immediate_actions": escalation_path["immediate_actions"].copy()
        }
        
        # Customer tier adjustments
        customer_tier = ticket_data.get("customer_tier", "standard")
        if customer_tier == "enterprise":
            routing["assigned_team"] = "senior_support"  # Enterprise customers get senior support
            routing["channels"].append("dedicated_support_line")
        elif customer_tier == "premium":
            if risk_level in ["low", "medium"]:
                routing["assigned_team"] = "tier_2_support"  # Premium customers get tier 2 minimum
        
        # Account value adjustments
        account_value = ticket_data.get("account_value", 0)
        if account_value > 50000:
            routing["channels"].append("executive_escalation")
        elif account_value > 10000:
            routing["channels"].append("account_manager_notification")
        
        # Historical relationship adjustments
        customer_since = ticket_data.get("customer_since")
        if customer_since:
            try:
                customer_date = datetime.fromisoformat(customer_since.replace('Z', '+00:00'))
                years_as_customer = (datetime.now() - customer_date).days / 365
                if years_as_customer > 5:
                    routing["channels"].append("loyalty_program_notification")
            except:
                pass
        
        # Priority score adjustments
        if priority_score > 0.8:
            routing["response_time"] = self._accelerate_response_time(routing["response_time"])
        
        return routing
    
    def _check_team_availability(self, team: str) -> Dict[str, Any]:
        """Check if the assigned team has capacity"""
        team_info = self.team_capacities.get(team, {"max_active": 10, "current_load": 0})
        
        # Simulate current load (in real implementation, this would come from database)
        current_load = team_info["current_load"]
        max_capacity = team_info["max_active"]
        
        availability = {
            "team": team,
            "current_load": current_load,
            "max_capacity": max_capacity,
            "available_capacity": max_capacity - current_load,
            "capacity_percentage": (current_load / max_capacity) * 100 if max_capacity > 0 else 0,
            "has_capacity": current_load < max_capacity
        }
        
        # Determine if backup team is needed
        if not availability["has_capacity"]:
            availability["backup_team"] = self._get_backup_team(team)
            availability["escalation_reason"] = "team_at_capacity"
        
        return availability
    
    def _get_backup_team(self, primary_team: str) -> str:
        """Get backup team if primary team is at capacity"""
        backup_mapping = {
            "crisis_response": "senior_support",
            "senior_support": "tier_2_support",
            "tier_2_support": "standard_support",
            "standard_support": "tier_2_support"
        }
        return backup_mapping.get(primary_team, "standard_support")
    
    def _accelerate_response_time(self, current_time: str) -> str:
        """Accelerate response time based on priority"""
        time_mapping = {
            "24_hours": "12_hours",
            "12_hours": "4_hours",
            "4_hours": "2_hours",
            "2_hours": "1_hour",
            "1_hour": "immediate"
        }
        return time_mapping.get(current_time, current_time)
    
    def _generate_escalation_plan(self, routing_details: Dict[str, Any], 
                                team_availability: Dict[str, Any],
                                risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed escalation plan"""
        
        plan = {
            "immediate_actions": routing_details["immediate_actions"],
            "assigned_team": team_availability["team"] if team_availability["has_capacity"] 
                           else team_availability["backup_team"],
            "response_time": routing_details["response_time"],
            "channels": routing_details["channels"],
            "escalation_notes": []
        }
        
        # Add escalation notes based on context
        if not team_availability["has_capacity"]:
            plan["escalation_notes"].append(
                f"Primary team {routing_details['assigned_team']} at capacity, "
                f"routing to {team_availability['backup_team']}"
            )
        
        risk_level = risk_assessment.get("risk_level", "low")
        if risk_level == "critical":
            plan["escalation_notes"].append("Critical risk level - immediate attention required")
        
        churn_risk = risk_assessment.get("risk_factors", {}).get("churn_risk", 0.0)
        if churn_risk > 0.7:
            plan["escalation_notes"].append("High churn risk detected - retention focus required")
        
        return plan
    
    def _check_priority_override(self, ticket_data: Dict[str, Any], risk_level: str) -> Dict[str, Any]:
        """Check if priority should be overridden based on special circumstances"""
        override = {
            "should_override": False,
            "reason": None,
            "new_priority": None
        }
        
        # Check for VIP customers
        if ticket_data.get("is_vip", False):
            override["should_override"] = True
            override["reason"] = "VIP customer"
            override["new_priority"] = "critical"
        
        # Check for legal/compliance issues
        legal_keywords = ["legal", "lawyer", "attorney", "compliance", "regulatory"]
        text = ticket_data.get("content", "").lower()
        if any(keyword in text for keyword in legal_keywords):
            override["should_override"] = True
            override["reason"] = "Legal/compliance concern"
            override["new_priority"] = "critical"
        
        # Check for social media threats
        social_keywords = ["twitter", "facebook", "social media", "public", "review"]
        if any(keyword in text for keyword in social_keywords):
            override["should_override"] = True
            override["reason"] = "Social media escalation threat"
            override["new_priority"] = "high"
        
        return override
    
    def update_team_load(self, team: str, load_change: int = 1):
        """Update team load (for simulation purposes)"""
        if team in self.team_capacities:
            self.team_capacities[team]["current_load"] = max(
                0, self.team_capacities[team]["current_load"] + load_change
            )
    
    def get_team_status(self) -> Dict[str, Any]:
        """Get current status of all teams"""
        return {
            team: {
                "current_load": info["current_load"],
                "max_capacity": info["max_active"],
                "utilization": (info["current_load"] / info["max_active"]) * 100
            }
            for team, info in self.team_capacities.items()
        }
