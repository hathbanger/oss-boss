SHELL := /bin/bash

PYTHON := python
PIP := pip
DOCKER_COMPOSE := docker-compose

ENV_FILE := .env

.PHONY: help install lint format test build up down logs run-cli run-api run-telegram run-all clean

help:
	@echo "OSS BOSS Makefile commands:"
	@echo "  make install      Install Python dependencies"
	@echo "  make lint         Run linters (flake8, isort)"
	@echo "  make format       Format code (black, isort)"
	@echo "  make test         Run tests"
	@echo "  make build        Build Docker images"
	@echo "  make up           Start services in background"
	@echo "  make down         Stop services and remove containers"
	@echo "  make logs         Follow Docker Compose logs"
	@echo "  make run-cli      Run CLI interface"
	@echo "  make run-api      Run API server"
	@echo "  make run-telegram Run Telegram bot"
	@echo "  make run-all      Run all interfaces locally"
	@echo "  make clean        Remove Python cache files"

install:
	$(PIP) install -r requirements.txt

lint:
	flake8 .
	isort --check-only .

format:
	black .
	isort .

test:
	pytest

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

run-cli:
	$(PYTHON) main.py --cli

run-api:
	$(PYTHON) main.py --api

run-telegram:
	$(PYTHON) main.py --telegram

run-all:
	$(PYTHON) main.py --all

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
