# Dominus MongoDB Status Service

[![CI/CD](https://github.com/Basyuk/dominus-mongo/actions/workflows/ci.yml/badge.svg)](https://github.com/Basyuk/dominus-mongo/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MongoDB 5.0+](https://img.shields.io/badge/mongodb-5.0+-green.svg)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/Basyuk/dominus-mongo)

Service for monitoring and managing server statuses in MongoDB clusters.

## Description

The service provides API for:
- Getting current server status in MongoDB replica set (primary, secondary, noset)
- Promoting current server priority to primary
- Automatic normalization of all server priorities in the cluster

## Features

### GET /status
Gets current server status in MongoDB cluster:
- **primary** - if current server has maximum or equal to maximum priority
- **secondary** - if current server priority is not maximum
- **noset** - if server is not found in replica set or an error occurred

### PUT /state or PUT /status
Promotes current server to primary:
1. Checks if server is not a voter (priority 0)
2. Gets maximum priority in the cluster
3. Increases current server priority by 200
4. Waits until server becomes primary
5. Normalizes all server priorities (decreases by 100)

**Voter server protection**: Servers with priority 0 (voters) cannot change their priority and receive 403 error.

## Installation and Configuration

### Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection URI | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | MongoDB database | `admin` |
| `MONGODB_COLLECTION` | MongoDB collection | `status` |
| `MONGODB_SERVER_NAME` | MongoDB server name in replica set | `hostname` |
| `MONGODB_PRIORITY_STEP` | Priority step for changing server status | `100` |
| `SERVICE_NAME` | Service name | `infra-status` |
| `AUTH_TYPE` | Authentication type (`local` or `keycloak`) | `local` |
| `MANAGE_USERNAME` | Username for local authentication | `admin` |
| `MANAGE_PASSWORD` | Password for local authentication | `password` |
| `REQUIRED_ROLE` | Role required for API access (for Keycloak) | `infra-admin` |

### Running

#### 1. Create .env file in project root:
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

#### 2. Run service:
```bash
# Local authentication
export AUTH_TYPE=local
export MONGODB_URI=mongodb://your-mongodb-host:27017
export MONGODB_SERVER_NAME=your-mongodb-server-name
export MONGODB_PRIORITY_STEP=100

# Run service
python -m dominus.main
```

## Docker

### Build image
```bash
docker build -t dominus-mongo .
```

### Run container
```bash
docker run -d \
  --name dominus-mongo \
  -p 8000:8000 \
  -e MONGODB_URI=mongodb://your-mongodb-host:27017 \
  -e MONGODB_SERVER_NAME=your-mongodb-server-name \
  -e MONGODB_PRIORITY_STEP=100 \
  -e AUTH_TYPE=local \
  dominus-mongo
```

## Docker Compose

```yaml
version: '3.8'
services:
  dominus-mongo:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017
      - MONGODB_SERVER_NAME=your-mongodb-server-name
      - MONGODB_PRIORITY_STEP=100
      - AUTH_TYPE=local
      - SERVICE_NAME=dominus-mongo
    depends_on:
      - mongodb
    restart: unless-stopped

  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    command: mongod --replSet rs0
    restart: unless-stopped
```

## API Endpoints

### GET /status
Get current server status.

**Response:**
```json
{
  "service_name": "dominus-mongo",
  "state": "primary",
  "hostname": "server-1",
  "user": "admin",
  "auth_type": "local"
}
```

### PUT /state
Promote current server to primary.

**Response:**
```json
{
  "service_name": "dominus-mongo",
  "state": "primary",
  "hostname": "server-1",
  "user": "admin",
  "auth_type": "local",
  "message": "Server successfully promoted to primary"
}
```

## Logging

Service maintains detailed logs of all operations:
- MongoDB connections
- Server status determination
- Priority changes
- Errors and warnings

## Security

- Supports local authentication and Keycloak
- All priority operations require authentication
- GET /status requires basic authentication
- PUT /state and PUT /status require `infra-admin` role (for Keycloak)

## Testing

### Quick cluster startup
```bash
# Start entire cluster (MongoDB + Dominus services)
./start-cluster.sh

# Test API
python test-api.py
```

### Manual testing
```bash
# Check status
curl -u admin:admin123 http://localhost:8000/status

# Promote to primary (works only for non-voter servers)
curl -X PUT -u admin:admin123 http://localhost:8000/state

# Test voter server (should return 403 error)
curl -X PUT -u admin:admin123 http://localhost:8003/state
```

## MongoDB Requirements

- MongoDB must be configured as replica set
- Service must have permissions to execute `replSetGetStatus` and `replSetReconfig` commands
- Server name in MONGODB_SERVER_NAME must match the name in replica set configuration

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/Basyuk/dominus-mongo.git
cd dominus-mongo
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
./start-cluster.sh
python test-api.py
```

## 📋 Roadmap

- [ ] Support for multiple authentication backends
- [ ] Metrics and monitoring integration (Prometheus/Grafana)
- [ ] Web UI for cluster management
- [ ] Kubernetes operator
- [ ] Multi-cluster support
- [ ] Advanced priority management strategies
- [ ] Integration with service discovery (Consul, etcd)

## 🐛 Issues and Bug Reports

Found a bug? Have a feature request? Please check our [Issues](https://github.com/Basyuk/dominus-mongo/issues) page.

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Use issue templates** for better organization
3. **Provide detailed information**:
   - Environment details (OS, Python version, MongoDB version)
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs

### Issue Types

- [🐛 **Bug Report**](https://github.com/Basyuk/dominus-mongo/issues/new?assignees=&labels=bug%2Cneeds-triage&template=bug_report.yml&title=%5BBUG%5D+) - Something isn't working
- [✨ **Feature Request**](https://github.com/Basyuk/dominus-mongo/issues/new?assignees=&labels=enhancement%2Cneeds-triage&template=feature_request.yml&title=%5BFEATURE%5D+) - Suggest new functionality  
- [❓ **Question**](https://github.com/Basyuk/dominus-mongo/issues/new?assignees=&labels=question%2Cneeds-triage&template=question.yml&title=%5BQUESTION%5D+) - Ask for help or clarification

## 💖 Support the Project

If this project helps you, consider supporting its development:

## Donation

## ₿ Cryptocurrency Donations

**Perfect for saying "thanks" with your favorite cryptocurrency!**

### 🚀 Easy Method - NOWPayments

**[₿ Donate with Crypto →](https://nowpayments.io/donation/dominus)**

- **100+ cryptocurrencies** supported
- **Credit card to crypto** option available
- **Secure and trusted** payment processor  ч
- **Email notifications** for successful donations
- **Global availability**

**Popular supported cryptocurrencies:**
- Bitcoin (BTC) ₿
- Ethereum (ETH) ⟠
- Dogecoin (DOGE) 🐕
- Litecoin (LTC) 🥈
- Bitcoin Cash (BCH) 💚
- Cardano (ADA) 🎯
- Polkadot (DOT) 🔴
- And 90+ more!

### 🏠 Direct Wallet Donations

**For experienced crypto users who prefer direct transfers:**

- **Bitcoin (BTC):** `1FaUsKnBeS3fByxgi74fLgJJDDSEbmXUyn`
- **Ethereum (ETH):** `0x1bba0e0d37cba3308f296413762f802367b62e29`
- **Bitcoin Cash (BCH):** `bitcoincash:qz07dsqamckgpd2lwexaql73e6knnue2s57m6ru9jc`
- **Litecoin (LTC):** `LZoS8Y61j6HiSneqtF3xchN4RRoWpGDWbE`
- **Dogecoin (DOGE):** `DKiaQaipwqwwiz9HSh4DtSTu6MAY1LLL33`

### Other Ways to Support

- ⭐ **Star the repository** on GitHub
- 🐛 **Report bugs** and help improve the project
- 📝 **Contribute code** or documentation
- 💬 **Share the project** with others who might find it useful
- 📢 **Write about it** in blog posts or social media

Every contribution, no matter how small, is greatly appreciated! 🙏

## 🏆 Contributors

Thanks to all contributors who have helped make this project better!

<!-- This section will be automatically updated by GitHub -->
<a href="https://github.com/Basyuk/dominus-mongo/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Basyuk/dominus-mongo" />
</a>

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [GitHub Wiki](https://github.com/Basyuk/dominus-mongo/wiki)
- **Docker Hub**: [dominus-mongo](https://hub.docker.com/r/Basyuk/dominus-mongo)
- **Issue Tracker**: [GitHub Issues](https://github.com/Basyuk/dominus-mongo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Basyuk/dominus-mongo/discussions)
- **Releases**: [GitHub Releases](https://github.com/Basyuk/dominus-mongo/releases)

## 🔒 Security

Security is important to us. If you discover a security vulnerability, please read our security policy and report it responsibly.

- **Security Policy**: [SECURITY.md](SECURITY.md)
- **Report vulnerabilities**: [Security Advisories](https://github.com/Basyuk/dominus-mongo/security/advisories)

---

<div align="center">

**[⬆ Back to Top](#dominus-mongodb-status-service)**

Made with ❤️ for the MongoDB community

</div>