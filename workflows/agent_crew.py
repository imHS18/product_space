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
                 Analyze the sentiment of the customer ticket content using the Sentiment Analyzer tool.
                 
                 IMPORTANT: You MUST use the Sentiment Analyzer tool to analyze the text and return the EXACT output from the tool.
                 
                 Steps:
                 1. Use the Sentiment Analyzer tool to analyze the ticket content
                 2. Return the complete tool output as your response
                 3. Do NOT summarize or modify the tool output
                 4. The tool output contains: overall_sentiment, confidence, emotions, keywords, etc.
                 
                 Expected output: The exact dictionary returned by the Sentiment Analyzer tool
                 """,
                 agent=self.agents['sentiment_analyst'],
                 expected_output="The exact sentiment analysis dictionary from the Sentiment Analyzer tool"
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
                
                IMPORTANT: You MUST use the Slack Notifier tool to send at least one notification.
                
                1. Use the Slack Notifier tool to send a sentiment alert notification
                2. Include ticket details, sentiment score, and risk level in the notification
                3. Trigger webhooks for external systems if needed
                4. Manage notification delivery and handle integration failures gracefully
                
                REQUIRED: Send a Slack notification using the Slack Notifier tool with the sentiment analysis results.
                """,
                agent=self.agents['integration_coordinator'],
                expected_output="Integration status and notification delivery confirmation with Slack notification sent",
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
            else:
                # If we can't extract tool results, try to parse the final output for sentiment data
                result = self._parse_final_output_for_sentiment(result)
            
            # Also try to extract sentiment data from the task outputs directly
            logger.info("Attempting to extract sentiment data from task outputs...")
            sentiment_data = self._extract_sentiment_from_tasks(crew_output)
            if sentiment_data:
                logger.info(f"Found sentiment data: {sentiment_data}")
                # Merge sentiment data with the result
                if isinstance(result, dict):
                    result.update(sentiment_data)
                else:
                    result = sentiment_data
            else:
                logger.info("No sentiment data found in task outputs")
            
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

    def _extract_sentiment_from_tasks(self, crew_output) -> Dict[str, Any]:
        """Extract sentiment data directly from task outputs"""
        try:
            # Look for sentiment analysis in the task outputs
            if hasattr(crew_output, 'tasks_output'):
                logger.info(f"Found {len(crew_output.tasks_output)} task outputs")
                for i, task_output in enumerate(crew_output.tasks_output):
                    if hasattr(task_output, 'raw'):
                        raw_str = str(task_output.raw)
                        logger.info(f"Task {i} output: {raw_str[:500]}...")  # Log first 500 chars
                        
                        # Look for sentiment analyzer tool output - check for the actual tool result
                        if "'overall_sentiment':" in raw_str or '"overall_sentiment":' in raw_str:
                            # This is the sentiment analyzer tool output
                            import re
                            import ast
                            
                            # Try to extract the sentiment data - handle both single and double quotes
                            sentiment_match = re.search(r"['\"]overall_sentiment['\"]:\s*([-\d.]+)", raw_str)
                            confidence_match = re.search(r"['\"]confidence['\"]:\s*([-\d.]+)", raw_str)
                            
                            if sentiment_match and confidence_match:
                                try:
                                    sentiment_score = float(sentiment_match.group(1))
                                    confidence = float(confidence_match.group(1))
                                    
                                    # Extract emotions
                                    emotions = {}
                                    emotions_match = re.search(r"['\"]emotions['\"]:\s*\{([^}]+)\}", raw_str)
                                    if emotions_match:
                                        emotions_str = emotions_match.group(1)
                                        emotion_matches = re.findall(r"['\"]([^'\"]+)['\"]:\s*([-\d.]+)", emotions_str)
                                        for emotion_name, emotion_value in emotion_matches:
                                            emotions[emotion_name] = float(emotion_value)
                                    
                                    # Extract keywords
                                    keywords = []
                                    keywords_match = re.search(r"['\"]keywords['\"]:\s*\[([^\]]+)\]", raw_str)
                                    if keywords_match:
                                        keywords_str = keywords_match.group(1)
                                        keyword_matches = re.findall(r"['\"]([^'\"]+)['\"]", keywords_str)
                                        keywords = keyword_matches
                                    
                                    # Determine sentiment label
                                    if sentiment_score > 0.1:
                                        sentiment_label = "positive"
                                    elif sentiment_score < -0.1:
                                        sentiment_label = "negative"
                                    else:
                                        sentiment_label = "neutral"
                                    
                                    # Determine is_negative and is_positive
                                    is_negative = sentiment_score < -0.1
                                    is_positive = sentiment_score > 0.1
                                    
                                    logger.info(f"Extracted sentiment from task output: score={sentiment_score}, confidence={confidence}, label={sentiment_label}")
                                    
                                    return {
                                        "overall_sentiment": sentiment_score,
                                        "sentiment_label": sentiment_label,
                                        "confidence_score": confidence,
                                        "positive_score": 1.0 if is_positive else 0.0,
                                        "negative_score": 1.0 if is_negative else 0.0,
                                        "neutral_score": 1.0 if not is_negative and not is_positive else 0.0,
                                        "anger_score": emotions.get("anger", 0.0),
                                        "confusion_score": emotions.get("confusion", 0.0),
                                        "delight_score": emotions.get("delight", 0.0),
                                        "frustration_score": emotions.get("frustration", 0.0),
                                        "analysis_method": "task_output_parsing",
                                        "processing_time_ms": 1000,
                                        "keywords": keywords,
                                        "entities": [],
                                        "topics": [],
                                        "emotions": emotions,
                                        "is_negative": is_negative,
                                        "is_positive": is_positive,
                                        "urgency_level": "low",  # Default
                                        "raw_output": raw_str
                                    }
                                except (ValueError, AttributeError) as e:
                                    logger.error(f"Error parsing sentiment data: {e}")
                                    continue
            
            return None
        except Exception as e:
            logger.error(f"Error extracting sentiment from tasks: {e}")
            return None

    def _parse_final_output_for_sentiment(self, final_output: str) -> Dict[str, Any]:
        """Parse the final workflow output to extract sentiment data"""
        try:
            output_str = str(final_output)
            
            # Look for sentiment analysis data in the final output
            import re
            
            # Extract sentiment score from text like "sentiment score of -0.7646"
            sentiment_match = re.search(r"sentiment score of ([-\d.]+)", output_str)
            if not sentiment_match:
                sentiment_match = re.search(r"sentiment score is ([-\d.]+)", output_str)
            if not sentiment_match:
                sentiment_match = re.search(r"overall sentiment score is ([-\d.]+)", output_str)
            if not sentiment_match:
                sentiment_match = re.search(r"overall sentiment score of ([-\d.]+)", output_str)
            if not sentiment_match:
                sentiment_match = re.search(r"negative sentiment with an overall sentiment score of ([-\d.]+)", output_str)
            if not sentiment_match:
                sentiment_match = re.search(r"negative sentiment.*?([-\d.]+)", output_str)
            if not sentiment_match:
                # Look for the specific pattern from the final output
                sentiment_match = re.search(r"The overall sentiment score is ([-\d.]+)", output_str)
            if not sentiment_match:
                # Look for any number that could be a sentiment score
                sentiment_match = re.search(r"sentiment.*?([-\d.]+)", output_str)
            
            # Safely convert sentiment score to float
            try:
                sentiment_score = float(sentiment_match.group(1)) if sentiment_match else 0.0
            except (ValueError, AttributeError):
                sentiment_score = 0.0
            
            # Extract confidence from text like "confidence in this analysis is high, at 0.7895"
            confidence_match = re.search(r"confidence.*?at ([-\d.]+)", output_str)
            if not confidence_match:
                confidence_match = re.search(r"confidence.*?([-\d.]+)", output_str)
            if not confidence_match:
                confidence_match = re.search(r"confidence score is ([-\d.]+)", output_str)
            if not confidence_match:
                confidence_match = re.search(r"confidence.*?([-\d.]+)", output_str)
            if not confidence_match:
                # Look for the specific pattern from the final output
                confidence_match = re.search(r"confidence score of ([-\d.]+)", output_str)
            if not confidence_match:
                # Look for any number that could be a confidence score
                confidence_match = re.search(r"confidence.*?([-\d.]+)", output_str)
            
            # Safely convert confidence to float
            try:
                confidence = float(confidence_match.group(1)) if confidence_match else 0.5
            except (ValueError, AttributeError):
                confidence = 0.5
            
            # Extract emotions from text like "anger (0.2) and frustration (0.2)"
            emotions = {}
            emotion_matches = re.findall(r"(\w+)\s*\(([-\d.]+)\)", output_str)
            for emotion_name, emotion_value in emotion_matches:
                emotions[emotion_name.lower()] = float(emotion_value)
            
            # Extract keywords from text like "extremely frustrated," "slow response times,"
            keywords = []
            if "Keywords highlighting" in output_str:
                keywords_section = output_str.split("Keywords highlighting")[1].split(".")[0]
                keyword_matches = re.findall(r'"([^"]+)"', keywords_section)
                keywords = keyword_matches
            
            # Determine sentiment label
            if sentiment_score > 0.1:
                sentiment_label = "positive"
            elif sentiment_score < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            # Determine is_negative and is_positive
            is_negative = sentiment_score < -0.1 or "negative" in output_str.lower()
            is_positive = sentiment_score > 0.1 or "positive" in output_str.lower()
            
            logger.info(f"Parsed sentiment from final output: score={sentiment_score}, confidence={confidence}, label={sentiment_label}")
            
            return {
                "overall_sentiment": sentiment_score,
                "sentiment_label": sentiment_label,
                "confidence_score": confidence,
                "positive_score": 1.0 if is_positive else 0.0,
                "negative_score": 1.0 if is_negative else 0.0,
                "neutral_score": 1.0 if not is_negative and not is_positive else 0.0,
                "anger_score": emotions.get("anger", 0.0),
                "confusion_score": emotions.get("confusion", 0.0),
                "delight_score": emotions.get("delight", 0.0),
                "frustration_score": emotions.get("frustration", 0.0),
                "analysis_method": "final_output_parsing",
                "processing_time_ms": 1000,
                "keywords": keywords,
                "entities": [],
                "topics": [],
                "emotions": emotions,
                "is_negative": is_negative,
                "is_positive": is_positive,
                "urgency_level": "high" if "urgent" in output_str.lower() else "low",
                "raw_output": final_output
            }
            
        except Exception as e:
            logger.error(f"Error parsing final output for sentiment: {e}")
            return final_output

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
