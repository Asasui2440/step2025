#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <cmath>
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

double total_distance(const vector<int>& tour, const vector<vector<double>>& dist_matrix) {
    double total = 0.0;
    int N = tour.size();
    for (int i = 0; i < N - 1; ++i)
        total += dist_matrix[tour[i]][tour[i + 1]];
    total += dist_matrix[tour[N - 1]][tour[0]];
    return total;
}

void write_tour(const vector<int>& tour, const string& filename) {
    ofstream ofs(filename);
    ofs << "index\n";
    for (int city : tour)
        ofs << city << "\n";
    ofs.close();
}

vector<int> ant_colony_optimization(
    const vector<vector<double>>& dist_matrix,
    int num_ants = 200,
    int generations = 2000,
    double alpha = 1.0,      // フェロモンの重み
    double beta = 8.0,       // ヒューリスティック情報の重み
    double rho = 0.8,        // フェロモン蒸発率
    double Q = 100.0         // フェロモン増加量
) {

    int N = dist_matrix.size();
    mt19937 rng(chrono::steady_clock::now().time_since_epoch().count()); //乱数生成
    uniform_real_distribution<double> real_dist(0.0, 1.0);

    // フェロモン初期化
    vector<vector<double>> pheromone(N, vector<double>(N, 1.0));
    vector<int> best_tour;
    double best_length = numeric_limits<double>::max();

    for (int gen = 0; gen < generations; ++gen) {
        vector<vector<int>> all_tours(num_ants, vector<int>(N));
        vector<double> lengths(num_ants);

        for (int k = 0; k < num_ants; ++k) {
            vector<int> tour;
            vector<bool> visited(N, false);
            int current = k % N;
            tour.push_back(current);
            visited[current] = true;

            for (int step = 1; step < N; ++step) {
                vector<double> prob(N, 0.0);
                double sum = 0.0;
                for (int j = 0; j < N; ++j) {
                    if (!visited[j]) {
                        // -------------------------------
                        // アリが次に都市jへ進む確率の「重み」を計算
                        // ・pheromone[current][j] ... 現在地currentから都市jへのフェロモン量（多いほど選ばれやすい）
                        // ・alpha ... フェロモンの影響度（大きいほどフェロモン重視）
                        // ・dist_matrix[current][j] ... 現在地currentから都市jへの距離（短いほど選ばれやすい）
                        // ・beta ... 距離の影響度（大きいほど距離重視）
                        // pow(pheromone, alpha) * pow(1/distance, beta) で重みを計算
                        // 1e-9を足しているのはゼロ除算防止
            
                        prob[j] = pow(pheromone[current][j], alpha) * pow(1.0 / (dist_matrix[current][j] + 1e-9), beta);
                        sum += prob[j];
                    }
                }

                // ランダムな値を生成
                double r = real_dist(rng) * sum;
                int next = -1;
                for (int j = 0; j < N; ++j) {
                    if (!visited[j]) {
                        r -= prob[j]; // 重みの分だけrを減らす
                        if (r <= 0) { 
                            next = j;
                            break;
                        }
                    }
                }
                // もしnextが決まらなかった場合、適当に未訪問の都市選ぶ
                if (next == -1) { // fallback
                    for (int j = 0; j < N; ++j) {
                        if (!visited[j]) {
                            next = j;
                            break;
                        }
                    }
                }
                tour.push_back(next);
                visited[next] = true;
                current = next;
            }

            // 1匹の蟻のツアー構築終わり
            all_tours[k] = tour;
            lengths[k] = total_distance(tour, dist_matrix);
            if (lengths[k] < best_length) {
                best_length = lengths[k];
                best_tour = tour;
            }
        }

        // フェロモン蒸発
        for (int i = 0; i < N; ++i)
            for (int j = 0; j < N; ++j)
                pheromone[i][j] *= (1.0 - rho); // rhoが高いほどすぐに蒸発する

        // フェロモン更新
        for (int k = 0; k < num_ants; ++k) {
            double delta = Q / lengths[k];  // 短いツアーほど多くのフェロモンを残す
            for (int i = 0; i < N; ++i) {
                int from = all_tours[k][i];
                int to = all_tours[k][(i + 1) % N];
                pheromone[from][to] += delta;
                pheromone[to][from] += delta;
            }
        }
    if ((gen + 1) % 100 == 0 || gen == generations - 1) {
        cout << "[Gen " << (gen + 1) << "] best_length = " << best_length << endl;
    }

    }
    return best_tour;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " input.csv output.csv" << endl;
        return 1;
    }
    vector<City> cities = read_input(argv[1]);
    auto dist_matrix = distance_matrix(cities);
    auto tour = ant_colony_optimization(dist_matrix);
    cout << "length: " << total_distance(tour, dist_matrix) << endl;
    write_tour(tour, argv[2]);
    return 0;
}