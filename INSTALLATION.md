# Installation Guide - Student Expense Tracker

## Prerequisites

- **Python 3.10+** - Download from [python.org](https://www.python.org/downloads/)
- **pip** - Usually comes with Python
- **Git** (optional) - For cloning the repository

## Quick Start

### 1. Clone or Download the Project

```bash
git clone https://github.com/moamin/student-expense-tracker.git
cd student-expense-tracker
```

### 2. Create a Virtual Environment (Recommended)

```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

**Option A: Install from requirements.txt (Production)**
```bash
pip install -r requirements.txt
```

**Option B: Install in development mode with dev tools**
```bash
pip install -r requirements-dev.txt
```

**Option C: Install using pyproject.toml (Recommended)**
```bash
pip install -e ".[dev]"
```

## Running the Application

### GUI Application

```bash
python -m expense_tracker.app.gui.main
```

Or use the installed command:
```bash
mizaan
```

### CLI Application

```bash
python -m expense_tracker.app.cli
```

Or use the installed command:
```bash
student-expense-tracker
```

## Development Setup

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run Tests

```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=expense_tracker
```

Run specific test file:
```bash
pytest tests/unit/test_calculations.py -v
```

### Code Quality Tools

Format code with Black:
```bash
black src/
```

Sort imports with isort:
```bash
isort src/
```

Check code style with Ruff:
```bash
ruff check src/
```

Type checking with mypy:
```bash
mypy src/expense_tracker
```

### Pre-commit Hooks (Optional)

Set up pre-commit hooks to run checks automatically:
```bash
pip install pre-commit
pre-commit install
```

## File Structure

```
student-expense-tracker/
├── src/expense_tracker/
│   ├── app/
│   │   ├── gui/              # PyQt6 GUI application
│   │   ├── cli.py            # CLI interface
│   │   └── main.py           # GUI entry point
│   ├── application/
│   │   ├── calculations.py   # Business logic
│   │   └── services/         # Service layer
│   ├── domain/
│   │   ├── models/           # Domain models
│   │   └── validators.py     # Input validation
│   ├── infrastructure/
│   │   └── json/repositories/  # Data persistence
│   ├── ports/
│   │   └── repositories.py   # Repository interfaces
│   └── shared/
│       └── exceptions.py     # Custom exceptions
├── tests/
│   ├── unit/                 # Unit tests
│   └── conftest.py          # Pytest configuration
├── Docs/
│   └── *.md                 # Documentation
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml          # Project metadata & build config
└── setup.py                # Setup script
```

## Troubleshooting

### PyQt6 Installation Issues

On Linux, you might need to install additional system packages:

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip libgl1-mesa-glx

# Fedora
sudo dnf install python3-devel libGL
```

### Import Errors

If you get "ModuleNotFoundError: No module named 'expense_tracker'", make sure:
1. You're in the project directory
2. The virtual environment is activated
3. Dependencies are installed: `pip install -r requirements.txt`

### Permission Denied on Linux/macOS

Make entry points executable:
```bash
chmod +x venv/bin/mizaan
chmod +x venv/bin/student-expense-tracker
```

## Getting Help

- Check the [README.md](README.md) for project overview
- Review [ISSUES_FOUND.md](ISSUES_FOUND.md) for known issues
- Check [Docs/](Docs/) directory for design documents
- Open an issue on GitHub for bugs or feature requests

## Next Steps

1. **Run the GUI**: `mizaan` to see the application in action
2. **Read the concepts**: Check `Docs/concept.md` for the design philosophy
3. **Explore the code**: Start with `src/expense_tracker/app/main.py`
4. **Review tests**: Check `tests/unit/` for implementation examples

## Python Version Support

| Python Version | Status |
|---|---|
| 3.10 | ✅ Supported |
| 3.11 | ✅ Supported |
| 3.12 | ✅ Supported |
| 3.9 | ❌ Not supported |

## Dependencies Overview

| Package | Version | Purpose |
|---|---|---|
| PyQt6 | 6.7.0+ | GUI framework |
| pytest | 7.4.3+ | Testing framework |
| black | 23.12.0+ | Code formatter |
| isort | 5.13.2+ | Import sorter |
| mypy | 1.7.1+ | Type checker |
| ruff | 0.1.8+ | Linter |

See `requirements.txt` and `requirements-dev.txt` for complete dependency lists.
