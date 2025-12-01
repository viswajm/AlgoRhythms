# Main Makefile for Hybrid Python + C++ Primality Testing Project
# Linux/Unix only
#
# Targets:
#   make setup              - Initial setup (run first!)
#   make build              - Build C++ components
#   make run                - Run demonstration
#   make test-number        - Test specific number (n=<number> k=<iterations>)
#   make test-carmichael    - Test Carmichael numbers
#   make experiments        - Run full experimental suite
#   make benchmark          - Run Fermat benchmarks
#   make comprehensive      - Run comprehensive analysis
#   make asymptotic         - Run asymptotic complexity analysis
#   make analyze            - Analyze results
#   make plot               - Generate basic plots
#   make plot-fermat        - Generate Fermat analysis plots
#   make plot-fermat-benchmarks - Generate Fermat benchmark plots
#   make plot-comprehensive - Generate comprehensive plots
#   make plot-all           - Generate all plots
#   make full-run           - Run basic workflow
#   make full-analysis      - Run complete analysis workflow
#   make show-results       - Display results directory structure
#   make all                - Build everything
#   make clean              - Clean build files
#   make help               - Show this help

.PHONY: setup build run experiments benchmark comprehensive asymptotic analyze plot plot-fermat plot-fermat-benchmarks plot-comprehensive plot-all all clean help full-run full-analysis show-results

# Default target
all: build

# Show help
help:
	@echo "Primality Testing Project - Makefile"
	@echo "===================================="
	@echo ""
	@echo "Initial setup (required first time):"
	@echo "  make setup"
	@echo ""
	@echo "Common tasks:"
	@echo "  make build       - Build C++ components"
	@echo "  make run         - Run demo"
	@echo "  make experiments - Run all experiments"
	@echo "  make analyze     - Show results analysis"
	@echo "  make plot        - Generate basic plots"
	@echo ""
	@echo "Advanced analysis:"
	@echo "  make benchmark      - Run Fermat benchmarks"
	@echo "  make comprehensive  - Run comprehensive analysis"
	@echo "  make asymptotic     - Run asymptotic complexity analysis"
	@echo ""
	@echo "Plotting:"
	@echo "  make plot-fermat            - Generate Fermat analysis plots"
	@echo "  make plot-fermat-benchmarks - Generate Fermat benchmark plots"
	@echo "  make plot-comprehensive     - Generate comprehensive plots"
	@echo "  make plot-all               - Generate all plots"
	@echo ""
	@echo "Workflows:"
	@echo "  make full-run      - Run basic workflow (experiments + plots)"
	@echo "  make full-analysis - Run complete analysis workflow"
	@echo ""
	@echo "Utilities:"
	@echo "  make show-results  - Display results directory structure"
	@echo "  make clean         - Clean build files"
	@echo ""
	@echo "Testing specific numbers:"
	@echo "  make test-number n=561 k=10"
	@echo "  make test-carmichael"
	@echo ""

# Setup project
setup:
	@echo "Running setup..."
	@bash setup.sh

# Build C++ project
build:
	@echo "Building C++ components..."
	@cd cpp && make all
	@echo "Build complete! Executable: ./cpp/primality_test"

# Run demonstration
run: build
	@echo "Running demonstration..."
	@./cpp/primality_test

# Test specific number
test-number: build
	@if [ -z "$(n)" ] || [ -z "$(k)" ]; then \
		echo "Usage: make test-number n=<number> k=<iterations>"; \
		echo "Example: make test-number n=561 k=10"; \
	else \
		./cpp/primality_test $(n) $(k); \
	fi

# Test Carmichael numbers
test-carmichael: build
	@echo "Testing Carmichael numbers..."
	@./cpp/primality_test 561 10 0
	@./cpp/primality_test 1105 10 0
	@./cpp/primality_test 1729 10 0

# Run full experiments
experiments: build
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Running experiments..."
	@source venv/bin/activate && cd python && python3 experiment_runner.py ../cpp/primality_test

# Run Fermat benchmarks
benchmark-fermat: build
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Running Fermat benchmarks..."
	@source venv/bin/activate && cd python && python3 benchmark_fermat.py all

# Run Miller-Rabin benchmarks
benchmark-miller-rabin: build
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Running Miller-Rabin benchmarks..."
	@source venv/bin/activate && cd python && python3 benchmark_miller_rabin.py all

# Run both benchmarks
benchmark: benchmark-fermat benchmark-miller-rabin

# Run comprehensive analysis
comprehensive: build
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Running comprehensive analysis..."
	@source venv/bin/activate && cd python && python3 comprehensive_analysis.py

# Run asymptotic complexity analysis
asymptotic: build
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Running asymptotic complexity analysis..."
	@source venv/bin/activate && cd python && python3 asymptotic_benchmark.py

# Analyze results
analyze:
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@source venv/bin/activate && cd python && python3 results_analyzer.py

# Generate plots
plot:
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Generating basic plots..."
	@source venv/bin/activate && cd python && python3 plotter.py all

# Generate Fermat analysis plots
plot-fermat:
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Generating Fermat analysis plots..."
	@source venv/bin/activate && cd python && python3 plot_fermat_analysis.py

# Generate Miller-Rabin analysis plots
plot-miller-rabin:
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Generating Miller-Rabin analysis plots..."
	@source venv/bin/activate && cd python && python3 plot_miller_rabin_analysis.py

# Generate Fermat benchmark plots
plot-fermat-benchmarks:
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Generating Fermat benchmark plots..."
	@source venv/bin/activate && cd python && python3 plot_fermat_benchmarks.py all

# Generate Miller-Rabin benchmark plots
plot-miller-rabin-benchmarks:
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Generating Miller-Rabin benchmark plots..."
	@source venv/bin/activate && cd python && python3 plot_miller_rabin_benchmarks.py

# Generate comprehensive plots
plot-comprehensive:
	@if [ ! -d "venv" ]; then \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Generating comprehensive plots..."
	@source venv/bin/activate && cd python && python3 plot_comprehensive_results.py

# Generate all plots
plot-all: plot plot-fermat plot-miller-rabin plot-fermat-benchmarks plot-miller-rabin-benchmarks plot-comprehensive
	@echo ""
	@echo "=========================================="
	@echo "All plots generated!"
	@echo "=========================================="
	@echo "Check results/ directory for all visualizations"

# Clean build files
clean:
	@echo "Cleaning build files..."
	@cd cpp && make clean 2>/dev/null || true
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete!"

# Full workflow
full-run: setup experiments analyze plot
	@echo ""
	@echo "=========================================="
	@echo "Full workflow complete!"
	@echo "=========================================="
	@echo "Check results/plots/ for visualizations"

# Complete analysis workflow
full-analysis: setup benchmark comprehensive asymptotic plot-all
	@echo ""
	@echo "=========================================="
	@echo "Complete analysis workflow finished!"
	@echo "=========================================="
	@echo "Results saved in:"
	@echo "  - results/               (CSV files)"
	@echo "  - results/plots/         (Basic plots)"
	@echo "  - results/fermat_analysis/plots/       (Fermat analysis)"
	@echo "  - results/miller_rabin_analysis/plots/ (Miller-Rabin analysis)"
	@echo "  - results/fermat_benchmarks/           (Fermat benchmarks)"
	@echo "  - results/miller_rabin_benchmarks/     (Miller-Rabin benchmarks)"
	@echo "  - results/comprehensive/plots/         (Comprehensive comparison)"

# Show results directory structure
show-results:
	@echo "Results directory structure:"
	@echo "========================================"
	@if [ -d "results" ]; then \
		tree -L 3 results/ 2>/dev/null || find results/ -type f -o -type d | sort; \
	else \
		echo "No results directory found. Run 'make experiments' first."; \
	fi
