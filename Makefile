
.PHONY: venv install run

venv:
	@echo "Creating virtual environment..."
	@python3 -m venv venv

install: venv
	@echo "Installing dependencies..."
	@venv/bin/pip install -r requirements.txt

run:
	@echo "Running the app..."
	@. venv/bin/activate && uvicorn backend.api:APP

run-debug:
	@echo "Running the app in debug mode..."
	@. venv/bin/activate && uvicorn backend.api:APP --reload --log-level debug
