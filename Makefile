SHELL := /bin/bash
PYTHON ?= python3.9
PIP ?= pip3.9
VENV ?= venv

export

run:
	source $(VENV)/bin/activate && \
	uvicorn app.main:app --reload