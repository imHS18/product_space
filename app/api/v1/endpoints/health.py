"""
Health check endpoints
"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "sentiment-watchdog"}


@router.get("/detailed")
async def detailed_health_check(request: Request):
    """Detailed health check with component status"""
    try:
        # Check if agent manager is initialized
        agent_manager = getattr(request.app.state, 'agent_manager', None)
        agents_healthy = agent_manager is not None and agent_manager._initialized
        
        # Get workflow status if available
        workflow_status = None
        if agent_manager and agent_manager._initialized:
            try:
                workflow_status = await agent_manager.get_workflow_status()
            except Exception as e:
                workflow_status = {"error": str(e)}
        
        return {
            "status": "healthy",
            "service": "sentiment-watchdog",
            "components": {
                "agents": agents_healthy,
                "workflow": workflow_status,
                "database": True,  # Would check DB connection in real implementation
                "slack": bool(getattr(request.app.state, 'slack_service', None))
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "sentiment-watchdog",
            "error": str(e)
        }


@router.get("/workflow")
async def workflow_status(request: Request):
    """Get detailed workflow status"""
    try:
        agent_manager = getattr(request.app.state, 'agent_manager', None)
        
        if not agent_manager or not agent_manager._initialized:
            return {
                "status": "not_initialized",
                "message": "Agent manager not initialized"
            }
        
        workflow_status = await agent_manager.get_workflow_status()
        
        return {
            "status": "success",
            "workflow": workflow_status,
            "timestamp": workflow_status.get('timestamp', 'unknown')
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to get workflow status"
        }
