import os

SERVICE_NAME = os.getenv("SERVICE_NAME", "infra-status")
STATE_PATH = os.getenv("STATE_PATH", "state.bin")
STATE_VALUES = ("primary", "secondary", "notset", "noset")
DEFAULT_STATE = "noset"

# MongoDB настройки
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "admin")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "status")
MONGODB_SERVER_NAME = os.getenv("MONGODB_SERVER_NAME", "")
MONGODB_PRIORITY_STEP = int(os.getenv("MONGODB_PRIORITY_STEP", "100"))

# Тип аутентификации: "keycloak" или "local"
AUTH_TYPE = os.getenv("AUTH_TYPE", "local")

# Локальная аутентификация (для AUTH_TYPE=local)
MANAGE_USERNAME = os.getenv("MANAGE_USERNAME", "admin")
MANAGE_PASSWORD = os.getenv("MANAGE_PASSWORD", "password")

# Keycloak настройки (для AUTH_TYPE=keycloak)
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "master")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "infra-status")
KEYCLOAK_PUBLIC_KEY = os.getenv("KEYCLOAK_PUBLIC_KEY", "")

# Роли для доступа к API (для Keycloak)
REQUIRED_ROLE = os.getenv("REQUIRED_ROLE", "infra-admin")

# HTTPS настройки
USE_HTTPS = os.getenv("USE_HTTPS", "false").lower() == "true"
SSL_CERTFILE = os.getenv("SSL_CERTFILE", "")
SSL_KEYFILE = os.getenv("SSL_KEYFILE", "") 