#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <limits>
#include <chrono>

using namespace std;

struct City {
    double x, y;
};

double calc_distance(const City& a, const City& b) {
    double dx = a.x - b.x, dy = a.y - b.y;
    return sqrt(dx * dx + dy * dy);
}

vector<vector<double>> distance_matrix(const vector<City>& cities) {
    int N = cities.size();
    vector<vector<double>> dist(N, vector<double>(N));
    for (int i = 0; i < N; ++i)
        for (int j = 0; j < N; ++j)
            dist[i][j] = calc_distance(cities[i], cities[j]);
    return dist;
}

double total_distance(const vector<int>& tour, const vector<vector<double>>& dist_matrix) {
    double total = 0.0;
    int N = tour.size();
    for (int i = 0; i < N - 1; ++i)
        total += dist_matrix[tour[i]][tour[i + 1]];
    total += dist_matrix[tour[N - 1]][tour[0]];
    return total;
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
  
    
vector<City> read_input(const string& filename) {
    vector<City> cities;
    ifstream ifs(filename);
    string line;
    while (getline(ifs, line)) {
        if (line.empty() || line[0] == 'x' || line[0] == 'X') continue;
        stringstream ss(line);
        string xstr, ystr;
        getline(ss, xstr, ',');
        getline(ss, ystr, ',');
        cities.push_back({stod(xstr), stod(ystr)});
    }
    return cities;
}


vector<int> solve_genetic_algorithm(
    const vector<vector<double>>& dist_matrix,
    int population_size = 2000,
    int generations = 10000, 
    double mutation_rate = 0.3,
    int elite_size = 150
) {

    int N = dist_matrix.size();
    mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());
    uniform_real_distribution<double> real_dist(0.0, 1.0);

    // ランダムな都市の順列を生成
    auto create_individual = [&]() {
        vector<int> tour(N);
        iota(tour.begin(), tour.end(), 0);
        shuffle(tour.begin(), tour.end(), rng);
        return tour;
    };

    // 適応度
    // 距離が短いほど良い個体
    auto fitness = [&](const vector<int>& individual) {
        return 1.0 / total_distance(individual, dist_matrix);
    };

    // ランダムに選んだ中で、最良の個体を親にする
    auto tournament_selection = [&](const vector<vector<int>>& population, int tournament_size = 3) {
        vector<int> idxs(population.size());
        iota(idxs.begin(), idxs.end(), 0);
        shuffle(idxs.begin(), idxs.end(), rng);
        int best = idxs[0];
        double best_fit = fitness(population[best]);
        for (int i = 1; i < tournament_size; ++i) {
            int idx = idxs[i];
            double fit = fitness(population[idx]);
            if (fit > best_fit) {
                best = idx;
                best_fit = fit;
            }
        }
        return population[best];
    };

    // 順序交叉
    // 2つの親個体（parent1, parent2）から2つの子個体（child1, child2）を生成する。
    // 1. ランダムな区間[start, end)を選び、その区間は親1/親2から子1/子2へコピー。
    // 2. 残りの部分は、もう一方の親の順序を保ちつつ、まだ入っていない都市を前から埋める。
    // これにより、両親の部分的な順序情報を保った子個体ができる。
    auto order_crossover = [&](const vector<int>& parent1, const vector<int>& parent2) {
        int n = parent1.size();
        uniform_int_distribution<int> dist(0, n - 1);
        int start = dist(rng), end = dist(rng);
        if (start > end) swap(start, end);

        // 1. 区間[start, end)を親1/親2から子1/子2へコピー
        vector<int> child1(n, -1), child2(n, -1);
        for (int i = start; i < end; ++i) {
            child1[i] = parent1[i];
            child2[i] = parent2[i];
        }
        // child1 parent2の順序で残りを埋める
        int j = 0;
        for (int i = 0; i < n; ++i) {
            int val = parent2[i];
            if (find(child1.begin() + start, child1.begin() + end, val) == child1.begin() + end) {
                while (child1[j] != -1) ++j;
                child1[j] = val;
            }
        }
        // child2 parent1の順序で残りを埋める
        j = 0;
        for (int i = 0; i < n; ++i) {
            int val = parent1[i];
            if (find(child2.begin() + start, child2.begin() + end, val) == child2.begin() + end) {
                while (child2[j] != -1) ++j;
                child2[j] = val;
            }
        }
        return make_pair(child1, child2);
    };

    // スワップ突然変異 (2点の入れ替え)
    auto swap_mutation = [&](vector<int> individual) {
        if (real_dist(rng) < mutation_rate) {
            uniform_int_distribution<int> dist(0, N - 1);
            int i = dist(rng), j = dist(rng);
            swap(individual[i], individual[j]);
        }
        return individual;
    };

    // 2-opt突然変異（区間を反転）
    auto two_opt_mutation = [&](vector<int> individual) {
        if (real_dist(rng) < mutation_rate) {
            uniform_int_distribution<int> dist(0, N - 1);
            int i = dist(rng), j = dist(rng);
            if (i > j) swap(i, j);
            reverse(individual.begin() + i, individual.begin() + j + 1);
        }
        return individual;
    };

    // 初期集団 (tourのリスト)
    vector<vector<int>> population(population_size);
    for (auto& ind : population) ind = create_individual();

    vector<int> best_individual;
    double best_fitness = 0.0;

    // 世代ごとの進化ループ
    for (int gen = 0; gen < generations; ++gen) {
        // 各個体の適応度を計算して降順にソート
        vector<pair<vector<int>, double>> population_fitness;
        for (const auto& ind : population)
            population_fitness.emplace_back(ind, fitness(ind));
        sort(population_fitness.begin(), population_fitness.end(),
             [](const auto& a, const auto& b) { return a.second > b.second; });

        // 最良個体を記録
        if (population_fitness[0].second > best_fitness) {
            best_fitness = population_fitness[0].second;
            best_individual = population_fitness[0].first;
        }
        
        // ★ 500世代ごとにデバッグ出力
        if ((gen + 1) % 500 == 0 || gen == generations - 1) {
            double best_length = 1.0 / population_fitness[0].second;
            cout << "[Generation " << (gen + 1) << "] Best length: " << best_length << endl;
        }

        // エリート選択
        vector<vector<int>> new_population;
        for (int i = 0; i < elite_size; ++i)
            new_population.push_back(population_fitness[i].first);

        // 交叉と突然変異(エリートのtourは除く)
        while ((int)new_population.size() < population_size) {
            auto parent1 = tournament_selection(population);
            auto parent2 = tournament_selection(population);
            auto [child1, child2] = order_crossover(parent1, parent2);
            child1 = swap_mutation(child1);
            child2 = two_opt_mutation(child2);
            new_population.push_back(child1);
            if ((int)new_population.size() < population_size)
                new_population.push_back(child2);
        }
        population = new_population;


    }
    return best_individual.empty() ? population[0] : best_individual;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " input.csv output.csv" << endl;
        return 1;
    }
    vector<City> cities = read_input(argv[1]);
    auto dist_matrix = distance_matrix(cities);
    auto tour = solve_genetic_algorithm(dist_matrix);
    cout << "length: " << total_distance(tour, dist_matrix) << endl;
    write_tour(tour, argv[2]);
    return 0;
}