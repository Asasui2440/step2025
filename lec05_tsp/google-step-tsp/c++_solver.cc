#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <random>
#include <set>
#include <fstream>
#include <sstream>
#include <string>
#include <limits>
#include <chrono>
#include<fstream>

struct City {
    double x, y;
    City(double x = 0, double y = 0) : x(x), y(y) {}
};

class TSPSolver {
private:
    std::vector<City> cities;
    std::vector<std::vector<double>> dist_matrix;
    std::mt19937 rng;
    
    double distance(const City& city1, const City& city2) {
        return std::sqrt((city1.x - city2.x) * (city1.x - city2.x) + 
                        (city1.y - city2.y) * (city1.y - city2.y));
    }
    
    void build_distance_matrix() {
        int n = cities.size();
        dist_matrix.assign(n, std::vector<double>(n, 0.0));
        for (int i = 0; i < n; i++) {
            for (int j = i; j < n; j++) {
                dist_matrix[i][j] = dist_matrix[j][i] = distance(cities[i], cities[j]);
            }
        }
    }
    
    double total_distance(const std::vector<int>& tour) {
        double total_dist = 0.0;
        int n = tour.size();
        for (int i = 0; i < n - 1; i++) {
            total_dist += dist_matrix[tour[i]][tour[i + 1]];
        }
        total_dist += dist_matrix[tour[n - 1]][tour[0]];
        return total_dist;
    }
    
    std::vector<int> solve_greedy_multi_start(int num_starts) {
        int n = cities.size();
        std::vector<int> start_points;
        
        if (n < num_starts) {
            for (int i = 0; i < n; i++) {
                start_points.push_back(i);
            }
        } else {
            std::vector<int> indices(n);
            std::iota(indices.begin(), indices.end(), 0);
            std::shuffle(indices.begin(), indices.end(), rng);
            start_points.assign(indices.begin(), indices.begin() + std::min(num_starts, n));
        }
        
        std::vector<int> best_tour;
        double best_distance = std::numeric_limits<double>::infinity();
        
        for (int start : start_points) {
            int current_city = start;
            std::set<int> unvisited_cities;
            for (int i = 0; i < n; i++) {
                unvisited_cities.insert(i);
            }
            
            std::vector<int> tour = {current_city};
            unvisited_cities.erase(current_city);
            
            while (!unvisited_cities.empty()) {
                int next_city = -1;
                double min_dist = std::numeric_limits<double>::infinity();
                
                for (int city : unvisited_cities) {
                    if (dist_matrix[current_city][city] < min_dist) {
                        min_dist = dist_matrix[current_city][city];
                        next_city = city;
                    }
                }
                
                tour.push_back(next_city);
                unvisited_cities.erase(next_city);
                current_city = next_city;
            }
            
            double dist = total_distance(tour);
            if (dist < best_distance) {
                best_tour = tour;
                best_distance = dist;
            }
        }
        
        return best_tour;
    }
    
    std::vector<int> solve_opt2(std::vector<int> tour) {
        bool improved = true;
        while (improved) {
            improved = false;
            for (int i = 1; i < (int)tour.size() - 2; i++) {
                for (int j = i + 1; j < (int)tour.size() - 1; j++) {
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
    
    std::vector<int> solve_opt3(std::vector<int> tour, int iterations = 100000) {
        bool improved = true;
        int iter = 0;
        
        while (improved && iter < iterations) {
            improved = false;
            for (int i = 1; i < (int)tour.size() - 3 && !improved; i++) {
                for (int j = i + 1; j < (int)tour.size() - 2 && !improved; j++) {
                    for (int k = j + 1; k < (int)tour.size() - 1 && !improved; k++) {
                        double current_cost = total_distance(tour);
                        iter++;
                        
                        std::vector<int> P1(tour.begin(), tour.begin() + i);
                        std::vector<int> P2(tour.begin() + i, tour.begin() + j);
                        std::vector<int> P3(tour.begin() + j, tour.begin() + k);
                        std::vector<int> P4(tour.begin() + k, tour.end());
                        
                        std::vector<int> P2_rev = P2;
                        std::reverse(P2_rev.begin(), P2_rev.end());
                        std::vector<int> P3_rev = P3;
                        std::reverse(P3_rev.begin(), P3_rev.end());
                        
                        std::vector<std::vector<int>> patterns = {
                            P1, P3, P2, P4,
                            P1, P2_rev, P3_rev, P4,
                            P1, P3, P2_rev, P4,
                            P1, P3_rev, P2, P4,
                            P1, P3_rev, P2_rev, P4
                        };
                        
                        for (int p = 0; p < 5; p++) {
                            std::vector<int> pattern;
                            pattern.insert(pattern.end(), patterns[p*4].begin(), patterns[p*4].end());
                            pattern.insert(pattern.end(), patterns[p*4+1].begin(), patterns[p*4+1].end());
                            pattern.insert(pattern.end(), patterns[p*4+2].begin(), patterns[p*4+2].end());
                            pattern.insert(pattern.end(), patterns[p*4+3].begin(), patterns[p*4+3].end());
                            
                            double new_cost = total_distance(pattern);
                            if (new_cost < current_cost) {
                                tour = pattern;
                                improved = true;
                                break;
                            }
                        }
                    }
                }
            }
        }
        return tour;
    }
    
    std::vector<int> or_opt(const std::vector<int>& tour) {
        int n = tour.size();
        std::uniform_int_distribution<int> segment_dist(1, std::min(3, n - 1));
        int segment_length = segment_dist(rng);
        
        std::uniform_int_distribution<int> pos_dist(0, n - segment_length);
        int i = pos_dist(rng);
        int j = i + segment_length;
        
        std::vector<int> segment(tour.begin() + i, tour.begin() + j);
        std::vector<int> rest;
        rest.insert(rest.end(), tour.begin(), tour.begin() + i);
        rest.insert(rest.end(), tour.begin() + j, tour.end());
        
        std::uniform_int_distribution<int> insert_dist(0, rest.size());
        int insert_pos = insert_dist(rng);
        
        std::vector<int> new_tour;
        new_tour.insert(new_tour.end(), rest.begin(), rest.begin() + insert_pos);
        new_tour.insert(new_tour.end(), segment.begin(), segment.end());
        new_tour.insert(new_tour.end(), rest.begin() + insert_pos, rest.end());
        
        return new_tour;
    }
    
    std::vector<int> two_opt(const std::vector<int>& tour) {
        int n = tour.size();
        int i, j;
        
        do {
            std::uniform_int_distribution<int> dist(0, n - 1);
            i = dist(rng);
            j = dist(rng);
            if (i > j) std::swap(i, j);
        } while (j - i <= 1);
        
        std::vector<int> new_tour = tour;
        std::reverse(new_tour.begin() + i, new_tour.begin() + j + 1);
        return new_tour;
    }
    
    std::vector<int> three_opt(const std::vector<int>& tour) {
        int n = tour.size();
        int a, b, c;
        
        do {
            std::uniform_int_distribution<int> dist(0, n - 1);
            a = dist(rng);
            b = dist(rng);
            c = dist(rng);
            
            if (a > b) std::swap(a, b);
            if (b > c) std::swap(b, c);
            if (a > b) std::swap(a, b);
        } while (b - a <= 1 || c - b <= 1);
        
        std::vector<int> P1(tour.begin(), tour.begin() + a);
        std::vector<int> P2(tour.begin() + a, tour.begin() + b);
        std::vector<int> P3(tour.begin() + b, tour.begin() + c);
        std::vector<int> P4(tour.begin() + c, tour.end());
        
        std::vector<int> P2_rev = P2;
        std::reverse(P2_rev.begin(), P2_rev.end());
        std::vector<int> P3_rev = P3;
        std::reverse(P3_rev.begin(), P3_rev.end());
        
        std::vector<std::vector<int>> patterns = {
            P1, P3, P2, P4,
            P1, P2_rev, P3_rev, P4,
            P1, P3, P2_rev, P4,
            P1, P3_rev, P2, P4,
            P1, P3_rev, P2_rev, P4
        };
        
        std::uniform_int_distribution<int> pattern_dist(0, 4);
        int pattern_index = pattern_dist(rng);
        
        std::vector<int> new_tour;
        new_tour.insert(new_tour.end(), patterns[pattern_index*4].begin(), patterns[pattern_index*4].end());
        new_tour.insert(new_tour.end(), patterns[pattern_index*4+1].begin(), patterns[pattern_index*4+1].end());
        new_tour.insert(new_tour.end(), patterns[pattern_index*4+2].begin(), patterns[pattern_index*4+2].end());
        new_tour.insert(new_tour.end(), patterns[pattern_index*4+3].begin(), patterns[pattern_index*4+3].end());
        
        return new_tour;
    }
    
    std::vector<int> neighbor(const std::vector<int>& tour) {
        std::uniform_real_distribution<double> prob_dist(0.0, 1.0);
        double p = prob_dist(rng);
        
        if (p < 0.3) {
            return two_opt(tour);
        } else if (p < 0.65) {
            return three_opt(tour);
        } else {
            return or_opt(tour);
        }
    }
    
    std::vector<int> solve_annealing(std::vector<int> tour, 
                                   double initial_temp = -1, 
                                   double final_temp = 1e-8,
                                   double alpha = 0.9999999,
                                   long long max_iter = 1e9) {
        std::vector<int> current_tour = tour;
        std::vector<int> best_tour = tour;
        double current_cost = total_distance(current_tour);
        double before_cost = current_cost;
        double best_cost = current_cost;
        
        if (initial_temp < 0) {
            initial_temp = current_cost * 0.1;
        }
        
        double temp = initial_temp;
        long long iter = 0;
        long long stagnation = 0;
        
        std::uniform_real_distribution<double> rand_dist(0.0, 1.0);
        
        while (final_temp < temp && iter < max_iter) {
            std::vector<int> new_tour = neighbor(current_tour);
            double new_cost = total_distance(new_tour);
            
            double delta = new_cost - current_cost;
            
            if (delta < 0 || std::exp(-delta / temp) > rand_dist(rng)) {
                current_tour = new_tour;
                current_cost = new_cost;
            }
            
            temp *= alpha;
            
            if (iter % 10000000 == 0) {
                std::cout << "iter = " << iter << std::endl;
                std::cout << "temp = " << temp << std::endl;
                std::cout << "score = " << current_cost << std::endl;
            }
            
            if (std::abs(before_cost - current_cost) < 0.01) {
                stagnation++;
                if (stagnation > 5000000) {
                    temp = initial_temp * 0.1;
                    std::cout << "Reset temp! temp=" << temp << std::endl;
                    std::cout << "stagnated score=" << current_cost << std::endl;
                    stagnation = 0;
                    if (current_cost < best_cost) {
                        best_cost = current_cost;
                        best_tour = current_tour;
                    }
                }
                before_cost = current_cost;
            } else {
                stagnation = 0;
                before_cost = current_cost;
            }
            
            iter++;
        }
        
        return best_tour;
    }
    
public:
    TSPSolver() : rng(std::chrono::steady_clock::now().time_since_epoch().count()) {}
    
    bool read_input(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            std::cerr << "Error: Cannot open file " << filename << std::endl;
            return false;
        }
        
        std::string line;
        // Skip header if exists
        if (std::getline(file, line)) {
            // Check if first line looks like header
            if (line.find("x") != std::string::npos || line.find("X") != std::string::npos) {
                // Skip header line
            } else {
                // First line is data, parse it
                std::stringstream ss(line);
                std::string token;
                std::vector<std::string> tokens;
                while (std::getline(ss, token, ',')) {
                    tokens.push_back(token);
                }
                if (tokens.size() >= 2) {
                    cities.emplace_back(std::stod(tokens[0]), std::stod(tokens[1]));
                }
            }
        }
        
        while (std::getline(file, line)) {
            std::stringstream ss(line);
            std::string token;
            std::vector<std::string> tokens;
            while (std::getline(ss, token, ',')) {
                tokens.push_back(token);
            }
            if (tokens.size() >= 2) {
                cities.emplace_back(std::stod(tokens[0]), std::stod(tokens[1]));
            }
        }
        
        file.close();
        build_distance_matrix();
        return true;
    }


    void write_tour(const std::vector<int>& tour, const std::string& filename) {
    std::ofstream ofs(filename);
    if (!ofs) {
        std::cerr << "Error: Cannot open file " << filename << " for writing." << std::endl;
        return;
    }

    // 1行目にインデックス（0始まりにするなら tour[0]、1始まりにするなら tour[0] + 1）
    ofs << "index\n";

    // 2行目以降に都市番号を1行ずつ出力
    for (int city : tour) {
        ofs << city << "\n";  // 必要なら "+ 1" して1始まりに調整
    }

    ofs.close();
    }
    
    void solve(const std::string& out_filename) {
        std::vector<int> tour = solve_greedy_multi_start(2000);
        std::cout << "greedy = " << total_distance(tour) << std::endl;
        
        double cost = total_distance(tour);
        
        // N = 128, input_4.csv parameters
        //tour = solve_annealing(tour, cost * 0.5, 1e-9, 0.999997);

        // N = 512, input_5.csv, N = 2048, input_6.csv parameters
        tour = solve_annealing(tour, cost * 0.1, 1e-9, 0.9999999,1e10);
        std::cout << "annealing = " << total_distance(tour) << std::endl;
        
        tour = solve_opt2(tour);
        std::cout << "opt2 = " << total_distance(tour) << std::endl;
        
        //tour = solve_opt3(tour, 100000);
        //std::cout << "opt3 = " << total_distance(tour) << std::endl;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <input_file.csv>" << std::endl;
        return 1;
    }
    
    TSPSolver solver;
    if (!solver.read_input(argv[1])) {
        return 1;
    }
    
    solver.solve(argv[2]);
    
    return 0;
}