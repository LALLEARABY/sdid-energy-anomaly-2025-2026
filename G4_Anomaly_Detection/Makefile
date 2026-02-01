# G4 - Anomaly Detection Makefile
# Simplifies common commands

.PHONY: help install setup train score roi clean test notebook

help:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "G4 - Anomaly Detection Engine - Available Commands"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  make install     - Install Python dependencies"
	@echo "  make setup       - Run quick setup and verification"
	@echo "  make train       - Train the anomaly detection model"
	@echo "  make score       - Run scoring engine (continuous mode)"
	@echo "  make score-once  - Run scoring engine once (for testing)"
	@echo "  make roi         - Calculate ROI analysis"
	@echo "  make test        - Run unit tests"
	@echo "  make notebook    - Launch Jupyter notebook"
	@echo "  make clean       - Clean temporary files"
	@echo "  make help        - Show this help message"
	@echo ""
	@echo "════════════════════════════════════════════════════════════════"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

setup:
	@echo "Running quick setup..."
	python quickstart.py

train:
	@echo "Training anomaly detection model..."
	python train_model.py

train-validate:
	@echo "Training and validating model..."
	python train_model.py --validate

score:
	@echo "Starting continuous scoring engine..."
	python src/scoring_engine.py --mode continuous

score-once:
	@echo "Running single scoring iteration..."
	python src/scoring_engine.py --mode once

roi:
	@echo "Calculating ROI..."
	python src/roi_calculator.py

test:
	@echo "Running tests..."
	pytest tests/ -v

notebook:
	@echo "Launching Jupyter notebook..."
	jupyter notebook notebooks/analysis.ipynb

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup complete"

# Database commands
db-test:
	@echo "Testing database connection..."
	python -c "from src.database import DatabaseConnection; db = DatabaseConnection(); db.connect() and db.test_connection() and db.disconnect()"

db-stats:
	@echo "Getting database statistics..."
	python -c "from src.database import DatabaseConnection; db = DatabaseConnection(); db.connect(); print(db.get_anomaly_statistics()); db.disconnect()"

# Model commands
model-info:
	@echo "Getting model information..."
	python -c "from src.anomaly_detector import AnomalyDetector; d = AnomalyDetector(); d.load_model(); print(d.get_model_info())"
