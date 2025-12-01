#include <bits/stdc++.h>
using namespace std;

unordered_map<int, vector<int>> readGraphFromInput(int n) {
    unordered_map<int, vector<int>> graph;
    for (int i = 0; i < n; ++i) {
        int u, v;
        cin >> u >> v;
        graph[u].push_back(v);
        graph[v].push_back(u);  // For undirected graph
    }
    return graph;
}

// Edge contraction algorithm (O(V+E))
void contractEdge(unordered_map<int, vector<int>>& G, int u, int v) {
    G[u].insert(G[u].end(), G[v].begin(), G[v].end()); // Merge neighbors of v into u
    for (auto& [x, nbrs] : G) {
        for (auto& w : nbrs) if (w == v) w = u; // redirect edges from v to u
    }
    auto& nbrs = G[u];
    nbrs.erase(remove(nbrs.begin(), nbrs.end(), u), nbrs.end()); // Remove self-loops
    G.erase(v); // remove vertex v
}

// Karger's Min Cut Algorithm
int kargerMinCut(unordered_map<int, vector<int>> G, unsigned seed) {
    srand(seed); // Seed for randomness
    while (G.size() > 2) {
        vector<int> vertices;
        for(auto i:G)vertices.push_back(i.first); // Collect current vertices into new vector
        int u = vertices[rand()%vertices.size()]; // select random vertex u
        if (G[u].empty()) continue; // Skip if no edges
        int v = G[u][rand()%G[u].size()]; // select random vertex v connected to u
        contractEdge(G, u, v); // contract the edge
    }
    return G.begin()->second.size(); // Return the number of crossing edges
}

int main() {
    srand(time(NULL)); // Seed for randomness
    /* Input format:
    First line: three integers V (number of vertices), n (number of edges), number of trials
    Next n lines: two integers u and v representing an undirected edge between them (index 0)
    */
    int V, n, trials;
    cin >> V >> n >> trials;
    unordered_map<int, vector<int>> original = readGraphFromInput(n);
    // Here we are using unordered map of vertex and the vector of vertices 
    // connected to it to represent the adjacency list of the graph since it allows 
    // efficient representation without any empty vertices, thus saving space.

    // Success probability ≥ 1 - (1-2/(V(V-1)))^trials
    double theoretical_prob = 2.0 / (V * (V - 1.0));
    double expected_success = 1.0 - pow(1.0 - theoretical_prob, trials);
    cout << "Theoretical analysis:\n";
    cout << "  - Single trial success prob: " << (theoretical_prob * 100) << "%\n";
    cout << "  - Expected success after " << trials << " trials: " << (expected_success * 100) << "%\n";

    int bestCut = INT_MAX; // Initialized to a very large value
    for (int i = 0; i < trials; ++i) {
        int cut = kargerMinCut(original, rand()); // The algorithm takes a copy of original graph (pass by value) and a random seed
        bestCut = min(bestCut, cut); // Check whether it is the minimum cut and store it
    }

    cout << "Minimum cut found over " << trials << " trials: " << bestCut << "\n";
    return 0;
}
