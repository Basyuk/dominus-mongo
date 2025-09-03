# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Web UI for cluster management
- Prometheus metrics integration
- Kubernetes operator
- Support for multiple authentication backends
- Advanced priority management strategies

## [1.0.0] - 2024-01-XX

### Added
- Initial release of Dominus MongoDB Status Service
- FastAPI-based REST API for MongoDB replica set management
- Support for promoting servers to primary
- Voter server protection mechanism
- Local and Keycloak authentication support
- Docker and Docker Compose support
- Comprehensive test suite
- API endpoints:
  - `GET /status` - Get current server status
  - `PUT /state` - Promote server to primary
  - `PUT /status` - Alternative endpoint for promotion
- Environment-based configuration
- Detailed logging system
- Priority normalization after promotion
- Protection against unauthorized priority changes

### Security
- Role-based access control
- Secure token handling
- Input validation
- Rate limiting capabilities
- HTTPS support

### Documentation
- Complete README with installation and usage instructions
- Contributing guidelines
- Security policy
- Issue and PR templates
- API documentation
- Docker deployment guides

### Testing
- Unit tests for core functionality
- Integration tests with MongoDB
- API endpoint testing
- Voter protection testing
- CI/CD pipeline with GitHub Actions

### Infrastructure
- GitHub Actions for CI/CD
- Docker Hub integration
- Multi-architecture Docker builds
- Security scanning with Bandit and Safety
- Code quality checks with Black, isort, and flake8

## [0.1.0] - 2024-01-XX

### Added
- Initial project structure
- Basic MongoDB integration
- Core status management logic

---

## Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

## Release Process

1. Update version number in `setup.py`
2. Update CHANGELOG.md with new version
3. Create git tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will automatically build and publish

## Migration Guides

### From 0.x to 1.0.0

This is the initial stable release. If you were using pre-release versions:

1. Update configuration environment variables
2. Update Docker image tags
3. Review security settings
4. Test authentication configuration

For detailed migration instructions, see the [Migration Guide](docs/MIGRATION.md).
