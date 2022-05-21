
#venv: $(VENV)/Scripts/Activate.ps1

PY = python
VENV = .venv
BIN=$(VENV)/Scripts


all: lint clean
#pip3 freeze > requirements.txt
$(VENV): requirements.txt
		$(BIN)/pip install --upgrade -r requirements.txt

.PHONY: format
format:	$(VENV)
	@$(BIN)/isort .
	@$(BIN)/blue .

.PHONY: lint
lint: $(VENV)
	@$(BIN)/isort . --check
	@$(BIN)/blue . --check



