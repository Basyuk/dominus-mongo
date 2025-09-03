# Dominus MongoDB Status Service Quick Start

## 1. Preparation

Make sure you have installed:
- Docker and Docker Compose
- Python 3.8+

## 2. Configuration Setup

Create `.env` file in project root:
```bash
# Authentication settings
AUTH_TYPE=local
MANAGE_USERNAME=admin
MANAGE_PASSWORD=admin123

# MongoDB settings
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=admin
MONGODB_COLLECTION=status
MONGODB_SERVER_NAME=your-mongodb-server-name
MONGODB_PRIORITY_STEP=100

# Service settings
SERVICE_NAME=dominus-mongo
```

## 3. Start Cluster

```bash
# Start MongoDB cluster and Dominus services
./start-cluster.sh
```

This script:
- Starts 3 MongoDB containers in replica set
- Initializes replica set
- Starts 3 Dominus services

## 4. Testing

```bash
# Automated testing
python test-api.py

# Test voter server protection
python test-voter-protection.py

# Or manual testing
curl -u admin:admin123 http://localhost:8000/status
curl -X PUT -u admin:admin123 http://localhost:8000/state

# Test voter server (should return 403 error)
curl -X PUT -u admin:admin123 http://localhost:8003/state
```

## 5. Available Services

- **MongoDB**: localhost:27017, 27018, 27019
- **Dominus API**: 
  - http://localhost:8000 (msk-app1)
  - http://localhost:8001 (vlg-app01)
  - http://localhost:8002 (msk-app01)

## 6. Stop

```bash
docker-compose down
```

## Troubleshooting

### Service Unavailable
```bash
# Check logs
docker-compose logs dominus-mongo1

# Restart
docker-compose restart dominus-mongo1
```

### MongoDB Connection Issues
```bash
# Check replica set status
docker exec mongodb1 mongosh --eval "rs.status()"

# Reinitialize replica set
docker exec mongodb1 mongosh --eval "rs.reconfig(rs.config())"
```
