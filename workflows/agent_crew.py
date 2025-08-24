"""
Customer Sentiment Watchdog - Multi-Agent Workflow
Orchestrates the collaboration between different AI agents for sentiment analysis and alert management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from crewai.llm import LLM
from litellm import completion
import os

# Import our custom tools
from tools.sentiment_analyzer import SentimentAnalyzer
from tools.confidence_scorer import ConfidenceScorer
from tools.risk_assessor import RiskAssessor
from tools.escalation_router import EscalationRouter
from tools.response_creator import ResponseCreator
from tools.tone_matcher import ToneMatcher
from tools.slack_notifier import SlackNotifier
from tools.webhook_handler import WebhookHandler
from tools.database_manager import DatabaseManager
from tools.task_router import TaskRouter

# Import our agent creation functions
from agent.sentiment_analyst import create_sentiment_agent
from agent.alert_manager import create_alert_agent
from agent.response_generator import create_response_agent
from agent.integration_coordinator import create_integration_agent
from agent.orchestrator import create_orchestrator_agent

logger = logging.getLogger(__name__)


class SentimentWatchdogWorkflow:
    """
    Main workflow orchestrator for the Customer Sentiment Watchdog system.
    Manages the collaboration between different AI agents to process tickets,
    analyze sentiment, generate alerts, and coordinate responses.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the workflow with configuration.
        
        Args:
            config: Configuration dictionary containing API keys and settings
        """
        self.config = config
        self.agents = {}
        self.tools = {}
        self.crew = None
        self.llm = self._initialize_llm()
        self._initialize_tools()
        self._initialize_agents()
        self._create_crew()
    
    def _initialize_llm(self):
        """Initialize the LLM with Google Gemini using LiteLLM"""
        try:
            api_key = self.config.get('GOOGLE_GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_GEMINI_API_KEY is required")
            
            # Set the API key as environment variable for LiteLLM
            os.environ["GEMINI_API_KEY"] = api_key
            
            # Use CrewAI's LLM class with LiteLLM
            llm = LLM(
                model="gemini/gemini-2.0-flash-lite",
                temperature=0.1,
                max_tokens=2048
            )
            
            logger.info("Google Gemini LLM (LiteLLM) initialized successfully")
            return llm
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise
    
    def _initialize_tools(self):
        """Initialize all the tools that agents will use."""
        try:
            self.tools = {
                'sentiment_analyzer': SentimentAnalyzer(),
                'confidence_scorer': ConfidenceScorer(),
                'risk_assessor': RiskAssessor(),
                'escalation_router': EscalationRouter(),
                'response_creator': ResponseCreator(),
                'tone_matcher': ToneMatcher(),
                'slack_notifier': SlackNotifier(),
                'webhook_handler': WebhookHandler(),
                'database_manager': DatabaseManager(),
                'task_router': TaskRouter()
            }
            logger.info("All tools initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing tools: {e}")
            raise
    
    def _initialize_agents(self):
        """Initialize all the CrewAI agents with their respective tools."""
        try:
            # Create agents using the existing functions with LLM
            self.agents['sentiment_analyst'] = create_sentiment_agent(llm=self.llm)
            self.agents['alert_manager'] = create_alert_agent(llm=self.llm)
            self.agents['response_generator'] = create_response_agent(llm=self.llm)
            self.agents['integration_coordinator'] = create_integration_agent(llm=self.llm)
            self.agents['orchestrator'] = create_orchestrator_agent(llm=self.llm)
            
            logger.info("All agents initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing agents: {e}")
            raise
    
    def _create_crew(self):
        """Create the CrewAI crew with all agents and their tasks."""
        try:
            # Create tasks first without context dependencies
            task1 = Task(
                description="""
                Analyze the sentiment of the customer ticket content.
                1. Use the sentiment analyzer to get comprehensive sentiment analysis
                2. Evaluate the confidence of the analysis
                3. Extract key emotions and keywords
                4. Assess urgency indicators
                """,
                agent=self.agents['sentiment_analyst'],
                expected_output="Detailed sentiment analysis with confidence scores and emotional insights"
            )
            
            task2 = Task(
                description="""
                Based on the sentiment analysis, assess the risk level and determine if alerts are needed.
                1. Evaluate churn risk and escalation potential
                2. Consider customer tier and business impact
                3. Determine appropriate escalation routing
                4. Calculate priority scores
                """,
                agent=self.agents['alert_manager'],
                expected_output="Risk assessment with alert recommendations and escalation plan",
                context=[task1]
            )
            
            task3 = Task(
                description="""
                Create personalized response recommendations for the customer.
                1. Generate appropriate response content
                2. Match tone to customer's emotional state
                3. Include urgency handling instructions
                4. Suggest follow-up actions
                """,
                agent=self.agents['response_generator'],
                expected_output="Personalized response recommendations with tone guidance",
                context=[task1, task2]
            )
            
            task4 = Task(
                description="""
                Handle external integrations and notifications.
                1. Send Slack alerts if needed
                2. Trigger webhooks for external systems
                3. Manage notification delivery
                4. Handle integration failures gracefully
                """,
                agent=self.agents['integration_coordinator'],
                expected_output="Integration status and notification delivery confirmation",
                context=[task1, task2, task3]
            )
            
            task5 = Task(
                description="""
                Coordinate the overall workflow and persist all data.
                1. Save ticket and analysis data to database
                2. Update trend aggregations
                3. Route tasks efficiently
                4. Monitor workflow performance
                """,
                agent=self.agents['orchestrator'],
                expected_output="Complete workflow summary with data persistence confirmation",
                context=[task1, task2, task3, task4]
            )
            
            # Define the workflow tasks list
            tasks = [task1, task2, task3, task4, task5]
            
            # Create the crew
            self.crew = Crew(
                agents=list(self.agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            logger.info("Crew created successfully with sequential workflow")
        except Exception as e:
            logger.error(f"Error creating crew: {e}")
            raise
    
    async def process_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a customer ticket through the complete workflow.
        
        Args:
            ticket_data: Dictionary containing ticket information
            
        Returns:
            Dictionary containing workflow results and recommendations
        """
        try:
            logger.info(f"Starting workflow for ticket: {ticket_data.get('id', 'unknown')}")
            start_time = datetime.now()
            
            # Execute the crew workflow (CrewAI kickoff is not async)
            # Pass the ticket data as inputs to the crew
            crew_inputs = {
                "ticket_content": ticket_data.get('content', ''),
                "ticket_id": ticket_data.get('id', ''),
                "customer_info": {
                    "customer_id": ticket_data.get('customer_id', ''),
                    "channel": ticket_data.get('channel', ''),
                    "priority": ticket_data.get('priority', ''),
                    "source": ticket_data.get('source', '')
                }
            }
            
            crew_output = self.crew.kickoff(inputs=crew_inputs)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Extract the result from CrewOutput object
            # CrewOutput has properties like .raw, .pydantic, .json_dict, etc.
            if hasattr(crew_output, 'raw'):
                result = crew_output.raw
            elif hasattr(crew_output, 'json_dict'):
                result = crew_output.json_dict
            else:
                result = str(crew_output)
            
            # Log the crew output for debugging
            logger.info(f"Crew output type: {type(crew_output)}")
            logger.info(f"Crew output result: {result}")
            
            # Try to extract tool results from the crew execution
            # The sentiment analyzer tool results should be available
            extracted_data = self._extract_tool_results(crew_output)
            if extracted_data:
                result = extracted_data
            
            # Prepare the response
            workflow_result = {
                'ticket_id': ticket_data.get('id'),
                'processing_time': processing_time,
                'workflow_status': 'completed',
                'result': result,
                'timestamp': end_time.isoformat(),
                'agents_used': list(self.agents.keys())
            }
            
            logger.info(f"Workflow completed in {processing_time:.2f} seconds")
            return workflow_result
            
        except Exception as e:
            logger.error(f"Error in workflow execution: {e}")
            return {
                'ticket_id': ticket_data.get('id'),
                'processing_time': 0,
                'workflow_status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def process_bulk_tickets(self, tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple tickets in parallel.
        
        Args:
            tickets: List of ticket data dictionaries
            
        Returns:
            List of workflow results for each ticket
        """
        try:
            logger.info(f"Processing {len(tickets)} tickets in bulk")
            
            # Process tickets concurrently
            tasks = [self.process_ticket(ticket) for ticket in tickets]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'ticket_id': tickets[i].get('id'),
                        'processing_time': 0,
                        'workflow_status': 'failed',
                        'error': str(result),
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    processed_results.append(result)
            
            logger.info(f"Bulk processing completed: {len(processed_results)} results")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in bulk processing: {e}")
            raise
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get the current status of the workflow system.
        
        Returns:
            Dictionary containing workflow status information
        """
        try:
            status = {
                'workflow_status': 'active',
                'agents_count': len(self.agents),
                'tools_count': len(self.tools),
                'crew_status': 'initialized' if self.crew else 'not_initialized',
                'timestamp': datetime.now().isoformat(),
                'agents': list(self.agents.keys()),
                'tools': list(self.tools.keys())
            }
            
            # Check tool status
            tool_status = {}
            for tool_name, tool in self.tools.items():
                tool_status[tool_name] = {
                    'status': 'available',
                    'type': type(tool).__name__
                }
            
            status['tool_status'] = tool_status
            return status
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {
                'workflow_status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _extract_tool_results(self, crew_output) -> Dict[str, Any]:
        """Extract tool execution results from crew output"""
        try:
            # Try to access the crew execution data to get tool results
            if hasattr(crew_output, 'tasks_output'):
                for task_output in crew_output.tasks_output:
                    if hasattr(task_output, 'raw') and 'overall_sentiment' in str(task_output.raw):
                        # Found sentiment analysis result
                        import json
                        try:
                            # Try to parse as JSON if it looks like sentiment data
                            raw_str = str(task_output.raw)
                            if '{' in raw_str and 'overall_sentiment' in raw_str:
                                # Extract JSON-like data from the text
                                start = raw_str.find('{')
                                end = raw_str.rfind('}') + 1
                                if start >= 0 and end > start:
                                    json_str = raw_str[start:end]
                                    return json.loads(json_str)
                        except:
                            pass
            
            # If we can't extract tool results, return None
            return None
        except Exception as e:
            logger.error(f"Error extracting tool results: {e}")
            return None

    async def cleanup(self):
        """Clean up resources and close connections."""
        try:
            logger.info("Cleaning up workflow resources")
            
            # Clean up tools if they have cleanup methods
            for tool_name, tool in self.tools.items():
                if hasattr(tool, 'cleanup') and callable(getattr(tool, 'cleanup')):
                    await tool.cleanup()
            
            # Clear references
            self.agents.clear()
            self.tools.clear()
            self.crew = None
            
            logger.info("Workflow cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Factory function to create workflow instances
def create_sentiment_workflow(config: Dict[str, Any]) -> SentimentWatchdogWorkflow:
    """
    Factory function to create a new SentimentWatchdogWorkflow instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Initialized SentimentWatchdogWorkflow instance
    """
    return SentimentWatchdogWorkflow(config)


# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        'GOOGLE_GEMINI_API_KEY': 'your_gemini_key_here',
        'SLACK_WEBHOOK_URL': 'your_slack_webhook_here',
        'DATABASE_URL': 'sqlite+aiosqlite:///sentiment_watchdog.db'
    }
    
    # Create and test workflow
    async def test_workflow():
        workflow = create_sentiment_workflow(config)
        
        # Test ticket data
        test_ticket = {
            'id': 'test-001',
            'content': 'I am very frustrated with your service. This is the third time I have this issue!',
            'customer_id': 'cust-123',
            'channel': 'email',
            'priority': 'high'
        }
        
        # Process the ticket
        result = await workflow.process_ticket(test_ticket)
        print(f"Workflow result: {result}")
        
        # Get status
        status = await workflow.get_workflow_status()
        print(f"Workflow status: {status}")
        
        # Cleanup
        await workflow.cleanup()
    
    # Run the test
    asyncio.run(test_workflow())


class SentimentWatchdogCrew:
    """
    Simplified crew class for the main application
    """
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.workflow = None
        logger.info("SentimentWatchdogCrew initialized")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using available agents"""
        try:
            # Use sentiment analyzer tool directly
            from tools.sentiment_analyzer import SentimentAnalyzer
            analyzer = SentimentAnalyzer()
            result = analyzer.analyze_sentiment(text)
            return result
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                "text": text,
                "error": str(e),
                "sentiment": "neutral",
                "confidence": 0.0
            }
    
    def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook data"""
        try:
            return {
                "status": "processed",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
