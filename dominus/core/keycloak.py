import os
import logging
import requests
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Настройки Keycloak
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "master")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "infra-status")
KEYCLOAK_PUBLIC_KEY = os.getenv("KEYCLOAK_PUBLIC_KEY", "")
KEYCLOAK_VERIFY_AUD = os.getenv("KEYCLOAK_VERIFY_AUD", "true").lower() == "true"
KEYCLOAK_USE_JWKS = os.getenv("KEYCLOAK_USE_JWKS", "true").lower() == "true"
KEYCLOAK_JWKS_TTL_SECONDS = int(os.getenv("KEYCLOAK_JWKS_TTL_SECONDS", "300"))
KEYCLOAK_ROLE_CLIENT_ID = os.getenv("KEYCLOAK_ROLE_CLIENT_ID", KEYCLOAK_CLIENT_ID)
KEYCLOAK_FALLBACK_REALM_ROLES = os.getenv("KEYCLOAK_FALLBACK_REALM_ROLES", "true").lower() == "true"
KEYCLOAK_VERIFY_AZP = os.getenv("KEYCLOAK_VERIFY_AZP", "false").lower() == "true"

security = HTTPBearer()

# Логирование (можно управлять уровнем через переменную окружения LOG_LEVEL)
logger = logging.getLogger("infra_status.keycloak")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s'))
    logger.addHandler(_handler)
logger.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO))
logger.propagate = False

def _key_preview(pem: str, keep: int = 24) -> str:
    if not pem:
        return "<empty>"
    # Убираем переводы строк для компактности предпросмотра
    flat = pem.replace("\n", "")
    if len(flat) <= keep * 2:
        return flat
    return f"{flat[:keep]}...{flat[-keep:]} (len={len(flat)})"

class KeycloakAuth:
    def __init__(self):
        self.public_key = None
        self._jwks_cache: Dict[str, Any] = {"keys": [], "fetched_at": 0}
        self._load_public_key()
        logger.info(
            "Keycloak config: url=%s realm=%s client_id=%s key_from_env=%s",
            KEYCLOAK_URL,
            KEYCLOAK_REALM,
            KEYCLOAK_CLIENT_ID,
            bool(KEYCLOAK_PUBLIC_KEY),
        )
    
    def _load_public_key(self):
        """Загружает публичный ключ из Keycloak"""
        if KEYCLOAK_PUBLIC_KEY:
            # Если ключ задан в переменной окружения
            has_headers = "-----BEGIN" in KEYCLOAK_PUBLIC_KEY
            logger.debug(
                "Using KEYCLOAK_PUBLIC_KEY from env; has_headers=%s, preview=%s",
                has_headers,
                _key_preview(KEYCLOAK_PUBLIC_KEY),
            )
            self.public_key = (
                KEYCLOAK_PUBLIC_KEY
                if has_headers
                else f"-----BEGIN PUBLIC KEY-----\n{KEYCLOAK_PUBLIC_KEY}\n-----END PUBLIC KEY-----"
            )
            logger.debug("Effective PEM preview=%s", _key_preview(self.public_key))
        else:
            # Загружаем ключ из Keycloak
            try:
                url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
                logger.info("Fetching realm info from %s", url)
                response = requests.get(url, timeout=10)
                logger.info("Realm info response status=%s", response.status_code)
                response.raise_for_status()
                realm_info = response.json()
                logger.debug(
                    "Realm info keys=%s", ",".join(sorted(realm_info.keys()))
                )
                pk = realm_info.get('public_key')
                if not pk:
                    logger.error("'public_key' not found in realm info: %s", realm_info)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Public key not found in Keycloak realm info",
                    )
                self.public_key = f"-----BEGIN PUBLIC KEY-----\n{pk}\n-----END PUBLIC KEY-----"
                logger.debug("Fetched PEM preview=%s", _key_preview(self.public_key))
            except Exception as e:
                logger.exception("Failed to load Keycloak public key: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to load Keycloak public key: {str(e)}"
                )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Проверяет JWT токен"""
        # Логируем заголовок JWT без проверки подписи
        try:
            header = jwt.get_unverified_header(token)
            logger.debug(
                "JWT header: alg=%s kid=%s typ=%s",
                header.get("alg"), header.get("kid"), header.get("typ")
            )
        except Exception as e:
            logger.warning("Cannot parse JWT header: %s", e)

        # Логируем некоторые клаймы без проверки подписи
        unverified_claims = {}
        try:
            unverified_claims = jwt.get_unverified_claims(token)
            logger.debug(
                "JWT claims (unverified): iss=%s aud=%s azp=%s exp=%s",
                unverified_claims.get("iss"),
                unverified_claims.get("aud"),
                unverified_claims.get("azp"),
                unverified_claims.get("exp"),
            )
        except Exception as e:
            logger.warning("Cannot parse JWT claims: %s", e)

        # Попытка проверки подписи через JWKS по kid
        key_candidate = None
        kid = None
        try:
            kid = header.get("kid")
        except Exception:
            pass

        if KEYCLOAK_USE_JWKS and kid:
            try:
                key_candidate = self._get_jwk_by_kid(kid)
                if key_candidate:
                    logger.debug("Found JWK by kid=%s (kty=%s alg=%s)", kid, key_candidate.get("kty"), key_candidate.get("alg"))
            except Exception as e:
                logger.warning("JWKS lookup failed for kid=%s: %s", kid, e)

        logger.debug(
            "Decoding JWT with verify_aud=%s verify_azp=%s client_id=%s issuer=%s using RS256; PEM has_headers=%s, preview=%s",
            KEYCLOAK_VERIFY_AUD,
            KEYCLOAK_VERIFY_AZP,
            KEYCLOAK_CLIENT_ID,
            f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}",
            (self.public_key or "").startswith("-----BEGIN"),
            _key_preview(self.public_key or ""),
        )
        try:
            verify_kwargs = {
                "algorithms": ["RS256"],
                "issuer": f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}",
            }
            
            # Настройка проверки audience/azp
            if KEYCLOAK_VERIFY_AZP:
                # Проверяем azp вместо aud
                verify_kwargs["options"] = {"verify_aud": False}
            elif KEYCLOAK_VERIFY_AUD:
                # Проверяем aud
                verify_kwargs["audience"] = KEYCLOAK_CLIENT_ID
            else:
                # Не проверяем ни aud, ни azp
                verify_kwargs["options"] = {"verify_aud": False}

            # Если нашли JWK по kid — используем его. Иначе — PEM публичный ключ
            verifying_key = key_candidate if key_candidate else self.public_key
            payload = jwt.decode(token, verifying_key, **verify_kwargs)
            
            # Дополнительная проверка azp если включена
            if KEYCLOAK_VERIFY_AZP:
                azp = payload.get("azp")
                if azp != KEYCLOAK_CLIENT_ID:
                    logger.error(
                        "AZP verification failed: expected=%s, got=%s",
                        KEYCLOAK_CLIENT_ID, azp
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid azp: expected {KEYCLOAK_CLIENT_ID}, got {azp}"
                    )
                logger.debug("AZP verification passed: %s", azp)
            
            logger.debug("JWT payload keys=%s", ",".join(sorted(payload.keys())))
            return payload
        except JWTError as e:
            logger.error(
                "JWT verification failed: %s (client_id=%s, token aud=%s, azp=%s, verify_aud=%s, verify_azp=%s)",
                e,
                KEYCLOAK_CLIENT_ID,
                unverified_claims.get("aud"),
                unverified_claims.get("azp"),
                KEYCLOAK_VERIFY_AUD,
                KEYCLOAK_VERIFY_AZP,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )

    def _get_jwks(self) -> Dict[str, Any]:
        """Возвращает JWKS с кешированием"""
        import time
        now = int(time.time())
        age = now - int(self._jwks_cache.get("fetched_at", 0))
        if self._jwks_cache.get("keys") and age < KEYCLOAK_JWKS_TTL_SECONDS:
            return self._jwks_cache

        jwks_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
        logger.info("Fetching JWKS from %s", jwks_url)
        resp = requests.get(jwks_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict) or "keys" not in data:
            raise ValueError("Invalid JWKS response format")
        self._jwks_cache = {"keys": data.get("keys", []), "fetched_at": now}
        logger.debug("JWKS keys fetched: %s", len(self._jwks_cache["keys"]))
        return self._jwks_cache

    def _get_jwk_by_kid(self, kid: str) -> Optional[Dict[str, Any]]:
        """Ищет JWK по kid (с кешированием)"""
        jwks = self._get_jwks()
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                return jwk
        # Если сразу не нашли — обновим JWKS и попробуем ещё раз (ротация)
        self._jwks_cache = {"keys": [], "fetched_at": 0}
        jwks = self._get_jwks()
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                return jwk
        return None

# Глобальный экземпляр для аутентификации
keycloak_auth = KeycloakAuth()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Зависимость для получения текущего пользователя из токена"""
    token = credentials.credentials
    return keycloak_auth.verify_token(token)

def require_role(required_role: str):
    """Декоратор для проверки роли пользователя"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        logger.debug(
            "Role check: required_role=%s, client_id=%s, fallback_realm=%s",
            required_role, KEYCLOAK_ROLE_CLIENT_ID, KEYCLOAK_FALLBACK_REALM_ROLES
        )
        logger.debug("Current user keys: %s", ",".join(sorted(current_user.keys())))

        # Пытаемся получить роли из resource_access по имени клиента
        resource_roles = (
            current_user.get("resource_access", {})
            .get(KEYCLOAK_ROLE_CLIENT_ID, {})
            .get("roles", [])
        )
        logger.debug(
            "Resource roles from %s: %s",
            KEYCLOAK_ROLE_CLIENT_ID, resource_roles
        )

        # При необходимости фоллбэк на realm_access
        realm_roles = current_user.get("realm_access", {}).get("roles", []) if KEYCLOAK_FALLBACK_REALM_ROLES else []
        logger.debug("Realm roles: %s", realm_roles)

        user_roles = resource_roles or realm_roles
        logger.debug("Final user roles: %s", user_roles)

        if not user_roles:
            logger.warning("No roles found in resource_access[%s] or realm_access", KEYCLOAK_ROLE_CLIENT_ID)

        if required_role not in user_roles:
            logger.error(
                "Role check failed: required=%s, available=%s",
                required_role, user_roles
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Required role '{required_role}' not found in resource_access['{KEYCLOAK_ROLE_CLIENT_ID}']"
                    + (" or realm_access" if KEYCLOAK_FALLBACK_REALM_ROLES else "")
                )
            )
        logger.debug("Role check passed for role: %s", required_role)
        return current_user
    return role_checker 