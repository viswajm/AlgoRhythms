#!/usr/bin/env bash
# @file setup.sh
# @brief Setup script for Linux - Primality Testing Project
# @author [Your Name]
# @date November 2025
#
# This script sets up the complete project environment on Linux
# Usage: bash setup.sh

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  PRIMALITY TESTING PROJECT - LINUX SETUP                          ║"
echo "║  Hybrid Python + C++ Implementation                               ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check system requirements
echo "[1/5] Checking system requirements..."

# Check for GCC
if ! command -v g++ &> /dev/null; then
    echo "ERROR: g++ not found. Install with:"
    echo "  Ubuntu/Debian: sudo apt-get install build-essential"
    echo "  Fedora: sudo dnf install gcc-c++"
    echo "  Arch: sudo pacman -S base-devel"
    exit 1
fi

GCC_VERSION=$(g++ --version | head -n 1)
echo "  ✓ g++: $GCC_VERSION"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Install with:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "  ✓ Python: $PYTHON_VERSION"

# Check for Make
if ! command -v make &> /dev/null; then
    echo "ERROR: make not found. Install with:"
    echo "  Ubuntu/Debian: sudo apt-get install make"
    echo "  Fedora: sudo dnf install make"
    echo "  Arch: sudo pacman -S make"
    exit 1
fi

echo "  ✓ make installed"
echo ""

# Create directory structure
echo "[2/5] Creating directory structure..."
mkdir -p cpp python data results/{plots}
echo "  ✓ Directories created:"
echo "    - cpp/"
echo "    - python/"
echo "    - data/"
echo "    - results/plots/"
echo ""

# Build C++ project
echo "[3/5] Building C++ implementation..."
cd cpp
make clean 2>/dev/null || true
make all
if [ $? -eq 0 ]; then
    echo "  ✓ C++ build successful"
    cd ..
else
    echo "  ERROR: C++ build failed"
    exit 1
fi
echo ""

# Install Python dependencies
echo "[4/5] Setting up Python environment..."

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  ✓ Virtual environment created"

    # Activate virtual environment
    source venv/bin/activate
    echo "  ✓ Virtual environment activated"
else
    source venv/bin/activate
    echo "  ✓ Virtual environment activated"
fi

# Install Python packages
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install numpy matplotlib pandas scipy > /dev/null 2>&1
echo "  ✓ Python packages installed:"
echo "    - numpy"
echo "    - matplotlib"
echo "    - pandas"
echo "    - scipy"
echo ""

# Generate test data
echo "[5/5] Generating test datasets..."
python3 python/data_generator.py
echo "  ✓ Test data generated"
echo ""

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  SETUP COMPLETE!                                                   ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Activate Python environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run demonstration:"
echo "     ./cpp/primality_test"
echo ""
echo "  3. Run full experiments:"
echo "     python3 python/experiment_runner.py ./cpp/primality_test"
echo ""
echo "  4. Analyze results:"
echo "     python3 python/results_analyzer.py"
echo ""
echo "  5. Generate plots:"
echo "     python3 python/plotter.py all"
echo ""
