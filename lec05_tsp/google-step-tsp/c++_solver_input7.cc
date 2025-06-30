#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <algorithm>
#include <limits>
#include <set>
#include <chrono>
#include <cassert>
#include <fstream>
#include <sstream>

struct City {
    double x, y;
    City(double x = 0, double y = 0) : x(x), y(y) {}
};

class TSPSolver {
private:
    std::vector<City> cities;
    std::vector<std::vector<double>> dist_matrix;
    std::mt19937 rng;



public:
    TSPSolver(const std::vector<City>& cities) : cities(cities), rng(std::random_device{}()) {
        buildDistanceMatrix();
    }
    
    double distance(const City& c1, const City& c2) const {
        double dx = c1.x - c2.x;
        double dy = c1.y - c2.y;
        return std::sqrt(dx * dx + dy * dy);
    }
    
    void buildDistanceMatrix() {
        int n = cities.size();
        dist_matrix.assign(n, std::vector<double>(n, 0.0));
        
        for (int i = 0; i < n; i++) {
            for (int j = i; j < n; j++) {
                double dist = distance(cities[i], cities[j]);
                dist_matrix[i][j] = dist_matrix[j][i] = dist;
            }
        }
    }
    
    double totalDistance(const std::vector<int>& tour) const {
        double total = 0.0;
        int n = tour.size();
        
        for (int i = 0; i < n - 1; i++) {
            total += dist_matrix[tour[i]][tour[i + 1]];
        }
        total += dist_matrix[tour[n - 1]][tour[0]]; // return to start
        
        return total;
    }
    
    std::vector<int> solveOpt2(std::vector<int> tour) {
        bool improved = true;
        int n = tour.size();
        
        while (improved) {
            improved = false;
            for (int i = 1; i < n - 2; i++) {
                for (int j = i + 1; j < n - 1; j++) {
                    int a = tour[i - 1], b = tour[i];
                    int c = tour[j], d = tour[j + 1];
                    
                    if (dist_matrix[a][b] + dist_matrix[c][d] > 
                        dist_matrix[a][c] + dist_matrix[b][d]) {
                        std::reverse(tour.begin() + i, tour.begin() + j + 1);
                        improved = true;
                    }
                }
            }
        }
        return tour;
    }
    std::vector<int> solveGreedyMultiStart() {
    int n = cities.size();
    int start_points_count = std::min(300, n);

    std::vector<int> indices(n);
    std::iota(indices.begin(), indices.end(), 0);
    if (start_points_count < n) {
        std::shuffle(indices.begin(), indices.end(), rng);
    }
    // start_points_count == n の場合はシャッフルせず全ての都市を開始点にする

    std::vector<int> best_tour;
    double best_distance = std::numeric_limits<double>::infinity();

    for (int s = 0; s < start_points_count; s++) {
        int start = indices[s];
        std::vector<int> tour = {start};
        std::set<int> unvisited;
        for (int i = 0; i < n; i++) {
            if (i != start) unvisited.insert(i);
        }

        int current = start;
        while (!unvisited.empty()) {
            int next_city = *std::min_element(unvisited.begin(), unvisited.end(),
                [&](int a, int b) {
                    return dist_matrix[current][a] < dist_matrix[current][b];
                });

            tour.push_back(next_city);
            unvisited.erase(next_city);
            current = next_city;
        }

        double dist = totalDistance(tour);
        if (dist < best_distance) {
            best_tour = tour;
            best_distance = dist;
        }
    }

    return best_tour;
}

   

 

    
    void solve() {
        auto start_time = std::chrono::high_resolution_clock::now();
        
        std::vector<int> tour = solveGreedyMultiStart();
        std::cout << "greedy = " << totalDistance(tour) << std::endl;
        
        tour = solveOpt2(tour);
        std::cout << "opt2 = " << totalDistance(tour) << std::endl;
       
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        std::cout << "Total time: " << duration.count() << " ms" << std::endl;
    }
};
std::vector<City> readCitiesFromCSV(const std::string& filename) {
    std::vector<City> cities;
    std::ifstream infile(filename);
    std::string line;
    while (std::getline(infile, line)) {
        std::istringstream iss(line);
        double x, y;
        char comma;
        if (iss >> x >> comma >> y) {
            cities.emplace_back(x, y);
        }
    }
    return cities;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " input.csv" << std::endl;
        return 1;
    }

    std::vector<City> cities = readCitiesFromCSV(argv[1]);
    TSPSolver solver(cities);
    solver.solve();
    
    return 0;
}
