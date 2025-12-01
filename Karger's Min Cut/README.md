# Karger's Min Cut Algorithm

Implementation and experimental analysis of Karger's randomized algorithm for finding the minimum cut in an undirected graph.

## Overview

Karger's algorithm is a randomized algorithm that finds a minimum cut of a connected graph with high probability. The algorithm repeatedly contracts random edges until only two vertices remain, and the number of edges between these vertices is the cut size.

## Algorithm Description

The algorithm works as follows:
1. Start with an undirected graph G = (V, E)
2. While there are more than 2 vertices:
   - Select a random edge (u, v)
   - Contract the edge by merging vertex v into vertex u
   - Remove self-loops
3. Return the number of remaining edges (the cut size)

### Time Complexity
- Single run: O(V²) where V is the number of vertices
- Success probability: At least 2/(V(V-1)) per trial
- Expected success after k trials: 1 - (1 - 2/(V(V-1)))^k

## Files

- `kargermincut.cpp` - Core implementation of Karger's algorithm
- `run_experiments.py` - Python script to run experiments and generate performance graphs

## Implementation Details

### Graph Representation
The implementation uses an `unordered_map<int, vector<int>>` to represent the adjacency list:
- Efficient space usage by avoiding empty vertices
- Supports dynamic vertex removal during edge contraction
- O(1) average-case vertex lookup

### Edge Contraction
The `contractEdge()` function performs the following operations:
1. Merges all neighbors of vertex v into vertex u
2. Redirects all edges pointing to v to point to u instead
3. Removes self-loops at u
4. Removes vertex v from the graph

## Usage

### Compilation
```bash
g++ -o kargermincut kargermincut.cpp -std=c++17
```

### Input Format
```
V n trials
u1 v1
u2 v2
...
un vn
```

Where:
- `V` = number of vertices
- `n` = number of edges
- `trials` = number of times to run the algorithm
- Each subsequent line contains an edge (u, v)

### Example
```
8 14 200
0 1
0 2
0 3
0 4
1 2
1 3
2 3
4 5
4 6
4 7
5 6
5 7
6 7
3 4
```

### Output
The program outputs:
- Theoretical single trial success probability
- Expected success probability after k trials
- Minimum cut found across all trials

## Experimental Analysis

The `run_experiments.py` script performs various experiments:

### Experiment Types

1. **Success Rate vs Number of Trials**
   - Tests how success rate improves with more trials
   - Uses graphs with known minimum cuts

2. **Different Graph Types**
   - Complete graphs (Kn)
   - Cycle graphs (Cn)
   - Path graphs
   - Two-cluster graphs with bridge edges

3. **Performance Analysis**
   - Runtime scaling with graph size
   - Success probability validation

### Running Experiments
```bash
# Windows
python run_experiments.py

# Linux/Mac
python3 run_experiments.py
```

## Theoretical Analysis

For a graph with V vertices:
- **Minimum cut probability per trial**: ≥ 2/(V(V-1))
- **Success probability after k trials**: ≥ 1 - (1 - 2/(V(V-1)))^k
- **Trials for constant success probability**: O(V² ln V)

For example, with V=8:
- Single trial success: ~3.57%
- After 100 trials: ~97.5% success
- After 200 trials: ~99.9% success

## Example Results

```
Theoretical analysis:
  - Single trial success prob: 3.57143%
  - Expected success after 200 trials: 99.9%
Minimum cut found over 200 trials: 2
```

## Dependencies

### C++ Code
- C++11 or later
- Standard library headers: `<bits/stdc++.h>` or equivalent

### Python Scripts
- Python 3.6+
- matplotlib
- numpy

Install Python dependencies:
```bash
pip install matplotlib numpy
```