#!/bin/bash

echo "Starting MongoDB cluster and Dominus services..."

# Stop and remove existing containers
echo "Stopping existing containers..."
docker-compose down

# Start MongoDB containers
echo "Starting MongoDB containers..."
docker-compose up -d mongodb1 mongodb2 mongodb3

# Wait for MongoDB containers to start
echo "Waiting for MongoDB containers to start..."
sleep 10

# Initialize replica set
echo "Initializing MongoDB Replica Set..."
docker exec mongodb1 mongosh --eval "
rs.initiate({
  _id: 'rs0',
  members: [
    {_id: 0, host: 'mongodb1:27017', priority: 500},
    {_id: 1, host: 'mongodb2:27017', priority: 400},
    {_id: 2, host: 'mongodb3:27017', priority: 0, votes: 1}
  ]
});
"

# Wait for replica set to become active
echo "Waiting for Replica Set activation..."
sleep 15

# Check replica set status
echo "Checking Replica Set status..."
docker exec mongodb1 mongosh --eval "rs.status()"

# Start Dominus services
echo "Starting Dominus services..."
docker-compose up -d dominus-mongo1 dominus-mongo2 dominus-mongo3

echo "Cluster successfully started!"
echo ""
echo "Available services:"
echo "- MongoDB1 (Primary): localhost:27017"
echo "- MongoDB2: localhost:27018" 
echo "- MongoDB3 (Voter): localhost:27019"
echo ""
echo "Dominus services:"
echo "- Dominus1 (msk-mng011): http://localhost:8000"
echo "- Dominus2 (vlg-mng01): http://localhost:8001"
echo "- Dominus3 (msk-mnga01): http://localhost:8002"
echo ""
echo "To check status:"
echo "curl -u admin:admin123 http://localhost:8000/status"
