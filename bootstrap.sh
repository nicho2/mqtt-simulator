#!/bin/sh
set -euo pipefail

# Create a Python 3.12 virtual environment
create_venv() {
    if [ ! -d ".venv" ]; then
        python3.12 -m venv .venv
    fi
}

# Install required packages into the virtual environment
install_deps() {
    . .venv/bin/activate
    pip install --upgrade pip
    pip install \
        "fastapi[all]" \
        "uvicorn[standard]" \
        paho-mqtt \
        "pydantic>=2" \
        prometheus-fastapi-instrumentator \
        python-dotenv \
        aiosqlite \
        pytest \
        pytest-asyncio \
        coverage
}

# Generate pinned requirements.txt
freeze_requirements() {
    . .venv/bin/activate
    pip freeze > requirements.txt
}

# Display basic usage instructions
print_usage() {
    cat <<USAGE
Virtual environment created in .venv
Activate it with: source .venv/bin/activate
Run tests with: pytest
Generate coverage with: coverage run -m pytest && coverage html
USAGE
}

main() {
    create_venv
    install_deps
    freeze_requirements
    print_usage
}

main "$@"
