import os
import secrets
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPBasic, HTTPBasicCredentials
from .keycloak import get_current_user, require_role
from .config import AUTH_TYPE, MANAGE_USERNAME, MANAGE_PASSWORD

# Логирование
logger = logging.getLogger("infra_status.auth")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s'))
    logger.addHandler(_handler)
logger.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO))
logger.propagate = False

# Инициализация схем аутентификации
http_bearer = HTTPBearer(auto_error=False)
http_basic = HTTPBasic(auto_error=False)

def local_check_auth(credentials: HTTPBasicCredentials = Depends(http_basic)):
    """Локальная аутентификация через HTTP Basic"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    correct_username = secrets.compare_digest(credentials.username, MANAGE_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, MANAGE_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return {"username": credentials.username, "auth_type": "local"}

def local_get_current_user(credentials: HTTPBasicCredentials = Depends(http_basic)) -> Dict[str, Any]:
    """Зависимость для получения текущего пользователя (локальная аутентификация)"""
    return local_check_auth(credentials)

def local_require_role(required_role: str):
    """Декоратор для проверки роли пользователя (локальная аутентификация)"""
    def role_checker(current_user: Dict[str, Any] = Depends(local_get_current_user)):
        # В локальной аутентификации все аутентифицированные пользователи имеют все права
        logger.debug("Local auth - all roles allowed for user: %s", current_user.get("username"))
        return current_user
    return role_checker

def hybrid_auth(
    bearer_credentials: Optional[HTTPBearer] = Depends(http_bearer),
    basic_credentials: Optional[HTTPBasicCredentials] = Depends(http_basic)
) -> Dict[str, Any]:
    """Гибридная аутентификация - поддерживает и Bearer, и Basic"""
    logger.debug("hybrid_auth: auth_type=%s", AUTH_TYPE)
    
    if AUTH_TYPE == "keycloak":
        # Пытаемся использовать Keycloak аутентификацию
        if bearer_credentials:
            logger.debug("Using Keycloak Bearer authentication")
            return get_current_user(bearer_credentials)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token required for Keycloak authentication",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        # Используем локальную аутентификацию
        if basic_credentials:
            logger.debug("Using local Basic authentication")
            return local_get_current_user(basic_credentials)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Basic authentication required",
                headers={"WWW-Authenticate": "Basic"},
            )

def hybrid_role_check(required_role: str):
    """Гибридная проверка ролей"""
    def role_checker(current_user: Dict[str, Any] = Depends(hybrid_auth)):
        logger.debug(
            "hybrid_role_check: auth_type=%s, required_role=%s, user_keys=%s",
            AUTH_TYPE, required_role, ",".join(sorted(current_user.keys()))
        )
        
        if AUTH_TYPE == "keycloak":
            # Для Keycloak используем обновленную функцию проверки ролей
            logger.debug("Using Keycloak role check for role: %s", required_role)
            return require_role(required_role)(current_user)
        else:
            # Для локальной аутентификации все аутентифицированные пользователи имеют все права
            logger.debug("Using local auth - all roles allowed")
            return current_user
    return role_checker 