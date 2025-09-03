# Contributing to Dominus MongoDB Status Service

Thank you for your interest in contributing to Dominus MongoDB Status Service! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- MongoDB knowledge (helpful)
- Basic understanding of replica sets

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/Basyuk/dominus-mongo.git
   cd dominus-mongo
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the development cluster**
   ```bash
   ./start-cluster.sh
   ```

5. **Run tests**
   ```bash
   python test-api.py
   python test-voter-protection.py
   ```

## 🐛 Reporting Issues

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the issue templates** when available
3. **Provide clear, detailed information**:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, MongoDB version)
   - Relevant logs or error messages

### Issue Types

- **🐛 Bug Report**: Something isn't working
- **✨ Feature Request**: Suggest new functionality
- **📚 Documentation**: Improve or add documentation
- **🔧 Enhancement**: Improve existing functionality
- **❓ Question**: Ask for help or clarification

## 🔧 Making Changes

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code improvements

### Code Style

- Follow [PEP 8](https://pep8.org/) for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and small
- Write comments for complex logic

### Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add voter server protection for primary promotion"
git commit -m "Fix MongoDB connection timeout handling"
git commit -m "Update README with installation instructions"

# Bad
git commit -m "fix stuff"
git commit -m "update"
```

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write tests for new functionality
   - Update documentation if needed
   - Ensure all tests pass

3. **Test your changes**
   ```bash
   python test-api.py
   python test-voter-protection.py
   ```

4. **Submit a pull request**
   - Use the PR template
   - Link related issues
   - Describe what changed and why
   - Include screenshots for UI changes

## 🧪 Testing

### Running Tests

```bash
# Test main API functionality
python test-api.py

# Test voter protection
python test-voter-protection.py

# Manual testing with curl
curl -u admin:admin123 http://localhost:8000/status
```

### Writing Tests

When adding new features:

1. Add test cases to existing test files
2. Create new test files for new modules
3. Test both success and error scenarios
4. Include edge cases

## 📚 Documentation

Help improve documentation by:

- Fixing typos or unclear explanations
- Adding examples and use cases
- Updating API documentation
- Creating tutorials or guides
- Translating documentation

## 🔐 Security

If you discover a security vulnerability:

1. **DO NOT** create a public issue
2. Email the maintainers directly
3. Provide detailed information about the vulnerability
4. Allow time for the issue to be addressed before disclosure

## 💡 Feature Requests

When suggesting new features:

1. **Check existing issues** first
2. **Explain the use case** - why is this needed?
3. **Describe the solution** you'd like to see
4. **Consider alternatives** you've thought about
5. **Provide examples** if helpful

## 🎯 Areas for Contribution

We especially welcome contributions in:

- **Testing**: More comprehensive test coverage
- **Documentation**: Tutorials, examples, API docs
- **Features**: Authentication methods, monitoring integrations
- **Performance**: Optimization and profiling
- **Security**: Security audits and improvements
- **Docker**: Multi-architecture builds, optimization

## 📞 Getting Help

- **Discord/Slack**: [Join our community](#) (if applicable)
- **GitHub Discussions**: For general questions
- **GitHub Issues**: For specific problems
- **Email**: [maintainer@example.com](#) (if applicable)

## 🏆 Recognition

Contributors are recognized in:

- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graphs

## 📄 License

By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) as the project.

---

Thank you for contributing to Dominus MongoDB Status Service! 🎉
