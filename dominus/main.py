import logging
import socket
from fastapi import FastAPI
from .core.config import USE_HTTPS, SSL_CERTFILE, SSL_KEYFILE
from .services.mongodb_service import mongodb_service
from .api.status import router as status_router
import os

app = FastAPI()

app.include_router(status_router)

# Configure basic logger
logging.basicConfig(level=logging.INFO)

@app.on_event("startup")
def startup_event():
    hostname = socket.gethostname()
    logging.info(f"Starting service on host: {hostname}")
    
    # Check MongoDB connection
    try:
        # Test MongoDB connection
        mongodb_service._get_client().close()
        logging.info("MongoDB connection established successfully")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        logging.warning("Service started, but MongoDB connection is not available")

if __name__ == "__main__":
    import uvicorn
    uvicorn_kwargs = {
        "app": "infra_status.main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
    }
    if USE_HTTPS and SSL_CERTFILE and SSL_KEYFILE:
        uvicorn_kwargs["ssl_certfile"] = SSL_CERTFILE
        uvicorn_kwargs["ssl_keyfile"] = SSL_KEYFILE
    uvicorn.run(**uvicorn_kwargs) 