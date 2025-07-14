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
#include <iterator>
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

    
    
    std::pair<std::vector<int>, double> two_opt(const std::vector<int>& tour, double cost) {
        int n = tour.size();
        
        // 境界チェックを厳密に
        std::uniform_int_distribution<int> i_dist(1, n - 3);
        std::uniform_int_distribution<int> j_dist(2, n - 2);
        
        int i = i_dist(rng);
        int j = j_dist(rng);
        
        if (i >= j) {
            std::swap(i, j);
        }
        
        if (j - i <= 1) {
            return std::make_pair(tour, cost);
        }
        
        // 差分コスト計算
        int a = tour[i - 1];
        int b = tour[i];
        int c = tour[j];
        int d = tour[j + 1];
        
        double cost_gap = dist_matrix[a][c] + dist_matrix[b][d] 
                        - dist_matrix[a][b] - dist_matrix[c][d];
        
        std::vector<int> new_tour = tour;
        std::reverse(new_tour.begin() + i, new_tour.begin() + j + 1);
        
        return std::make_pair(new_tour, cost + cost_gap);
    }

    // or_1_opt
    std::pair<std::vector<int>, double> or_opt(const std::vector<int>& tour, double cost) {
        int n = tour.size();


    std::uniform_int_distribution<int> pos_dist(0, n - 1);
    int i = pos_dist(rng);

   // 挿入位置（i自身は不可）
    std::vector<int> valid_positions;
    for (int pos = 0; pos <= n; ++pos) {
        if (pos != i && pos!=i+1) valid_positions.push_back(pos);
    }
    if (valid_positions.empty()) return std::make_pair(tour, cost);
    std::uniform_int_distribution<int> insert_dist(0, valid_positions.size() - 1);
    int insert_pos = valid_positions[insert_dist(rng)];

    // 差分コスト計算
    int seg = tour[i];
    int before_seg = tour[(i - 1 + n) % n];
    int after_seg = tour[(i + 1) % n];
   
    int insert_before = tour[(insert_pos - 1 + n) % n];
    int insert_after = tour[insert_pos % n];


     double cost_gap = dist_matrix[before_seg][after_seg]
                    + dist_matrix[insert_before][seg]
                    + dist_matrix[seg][insert_after]
                    - dist_matrix[before_seg][seg]
                    - dist_matrix[seg][after_seg]
                    - dist_matrix[insert_before][insert_after];

    // 新しいツアーを構築する
    std::vector<int> new_tour = tour;
    new_tour.erase(new_tour.begin() + i);
    int insert_idx = (insert_pos < i) ? insert_pos : insert_pos - 1;
    new_tour.insert(new_tour.begin() + insert_idx, seg);

    return std::make_pair(new_tour, cost + cost_gap);
    }

    // 半々の確率でor_optかtwo_optか選択
    std::pair<std::vector<int>, double> neighbor(const std::vector<int>& tour, double cost) {
        std::uniform_real_distribution<double> prob_dist(0.0, 1.0);
        double p = prob_dist(rng);
        if(p < 0.5){
            return or_opt(tour,cost);
        }
      else{
        return two_opt(tour,cost);
      }
    }


    // 焼きなまし
    std::vector<int> solve_annealing(std::vector<int> tour, 
                                   double initial_temp = -1, 
                                   double final_temp = 0.1,
                                   double beta = 1e-6,
                                   double epsilon = 0.01,
                                   long long max_iter = 1e9,
                                const std::string& realtime_filename="realtime_tour.csv") {
        std::vector<int> current_tour = tour;
        double current_cost = total_distance(current_tour);
        std::vector<int> best_tour_so_far = current_tour; // これまでの最良ツアーを保持
        double best_cost_so_far = current_cost;         // これまでの最良スコアを保持
        
        if (initial_temp < 0) {
            initial_temp = current_cost * 0.1;
        }
        
        double temp = initial_temp;
        long long iter = 0;
        
        std::uniform_real_distribution<double> rand_dist(0.0, 1.0);
        
        while (final_temp < temp && iter < max_iter) {
            auto [new_tour, new_cost] = neighbor(current_tour, current_cost);
            
            double delta = new_cost - current_cost;
            
            if (delta < 0 || std::exp(-delta / temp) > rand_dist(rng)) {
                current_tour = new_tour;
                current_cost = new_cost;

                if (current_cost < best_cost_so_far) {
                    best_cost_so_far = current_cost;
                    best_tour_so_far = current_tour;
                    //write_tour(best_tour_so_far, realtime_filename); 
                }
            }
            
            temp = initial_temp / (1 + beta * iter) - epsilon;

            if (iter % 10000000 == 0) {
                double actual_cost = total_distance(current_tour);
                std::cout << "iter = " << iter << std::endl;
                std::cout << "temp = " << temp << std::endl;
                std::cout << "score = " << current_cost << std::endl;
                std::cout << "real_score = " << actual_cost << std::endl;

            }

            iter++;
        }
        
        return best_tour_so_far;
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

// サンプルコードにあったwrite_tourのc++翻訳版
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
    
    void solve(const std::string& out_filename, const std::string& realtime_filename) {
        std::vector<int> tour = solve_greedy_multi_start(100);
        std::cout << "greedy = " << total_distance(tour) << std::endl;
        
        double cost = total_distance(tour);
        
        // N = 128, input_4.csv parameters
        //tour = solve_annealing(tour, cost * 0.5, 1e-9, 0.999997);

        // N = 512, input_5.csv, N = 2048, input_6.csv parameters
        tour = solve_annealing(tour, -1, 0.1, 1e-6,1,1e9, realtime_filename);
        std::cout << "annealing = " << total_distance(tour) << std::endl;

        write_tour(tour,out_filename);
        
    }
};



int main(int argc, char* argv[]) {
     if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <input_file.csv> <output_file.csv> <realtime_tour.csv>" << std::endl;
        return 1;
    }
    
    TSPSolver solver;
    if (!solver.read_input(argv[1])) {
        return 1;
    }
    
    solver.solve(argv[2],argv[3]);
    
    return 0;
}