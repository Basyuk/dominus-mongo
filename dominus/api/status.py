from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Literal, Dict, Any, Optional
from ..services.mongodb_service import get_current_status, promote_to_primary, SERVICE_NAME
from ..core.auth import hybrid_auth, hybrid_role_check
from ..core.config import REQUIRED_ROLE
import socket

router = APIRouter()

@router.get("/status")
def get_status():
    """Get current service status from MongoDB cluster (without authentication)"""
    try:
        status = get_current_status()
        hostname = socket.gethostname()
        
        return {
            "service_name": SERVICE_NAME, 
            "state": status, 
            "hostname": hostname
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@router.put("/state")
def set_state(
    new_state: Optional[str] = Query(None, description="Requested status (primary, secondary)"),
    current_user: Dict[str, Any] = Depends(hybrid_role_check(REQUIRED_ROLE)),
):
    """Promote current server to primary in MongoDB cluster or check secondary status (requires infra-admin role for Keycloak or authentication for local)"""
    try:
        hostname = socket.gethostname()
        current_status = get_current_status()
        
        # If secondary is requested, only check status
        if new_state == "secondary":
            if current_status == "secondary":
                return {
                    "service_name": SERVICE_NAME, 
                    "state": current_status, 
                    "hostname": hostname,
                    "user": current_user.get("preferred_username", current_user.get("username", "unknown")),
                    "auth_type": current_user.get("auth_type", "keycloak"),
                    "message": "Server is already secondary"
                }
            else:
                return {
                    "service_name": SERVICE_NAME, 
                    "state": current_status, 
                    "hostname": hostname,
                    "user": current_user.get("preferred_username", current_user.get("username", "unknown")),
                    "auth_type": current_user.get("auth_type", "keycloak"),
                    "message": f"Server is not secondary (current status: {current_status})"
                }
        
        # If primary is requested or parameter not specified, promote to primary
        if new_state == "primary" or new_state is None:
            # Promote server to primary
            success = promote_to_primary()
            
            if not success:
                raise HTTPException(status_code=500, detail="Failed to promote server to primary")
            
            # Get new status
            new_status = get_current_status()
            
            return {
                "service_name": SERVICE_NAME, 
                "state": new_status, 
                "hostname": hostname,
                "user": current_user.get("preferred_username", current_user.get("username", "unknown")),
                "auth_type": current_user.get("auth_type", "keycloak"),
                "message": "Server successfully promoted to primary"
            }
        
        # If unknown status specified
        raise HTTPException(status_code=400, detail=f"Unknown status: {new_state}. Supported values: primary, secondary")
        
    except ValueError as e:
        # Handle voter server error
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error changing status: {str(e)}")

@router.put("/status")
def set_status_via_status_endpoint(
    new_state: Optional[str] = Query(None, description="Requested status (primary, secondary)"),
    current_user: Dict[str, Any] = Depends(hybrid_role_check(REQUIRED_ROLE)),
):
    """Alternative endpoint for promoting to primary via /status (for compatibility)"""
    return set_state(new_state=new_state, current_user=current_user) 