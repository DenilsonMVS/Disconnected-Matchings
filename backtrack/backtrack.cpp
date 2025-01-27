#include <bits/stdc++.h>
#define show(v) cout << #v ": " << (v) << endl;

using namespace std;

#define INFEASIBLE 0
#define OPTIMAL 1
#define FEASIBLE 2
#define UNKNOWN 3
#define MAX 10000

int n, m, c;
int stk[MAX];
int match[MAX];
vector<int> g[MAX];
vector<int> bg[MAX];
int pai[MAX], base[MAX], vis[MAX];
queue<int> q;

// Os grafos testados não possuem mais de 32 vértices
bitset<64> bloss;
bitset<64> teve;
bitset<64> visited;
int l;


void contract(int u, int v, bool first = 1) {
	if (first) {
		bloss = 0;
        teve = 0;

		int k = u; l = v;
		while (1) {
			teve[k = base[k]] = 1;
			if (match[k] == -1) break;
			k = pai[match[k]];
		}
		while (!teve[l = base[l]]) l = pai[match[l]];
	}
	while (base[u] != l) {
		bloss[base[u]] = bloss[base[match[u]]] = 1;
		pai[u] = v;
		v = match[u];
		u = pai[match[u]];
	}
	if (!first) return;
	contract(v, u, 0);
	for (int i = 0; i < n; i++) if (bloss[base[i]]) {
		base[i] = l;
		if (!vis[i]) q.push(i);
		vis[i] = 1;
	}
}

int getpath(int s) {
	for (int i = 0; i < n; i++) base[i] = i, pai[i] = -1, vis[i] = 0;

    while(q.size()) {
        q.pop();
    }

	vis[s] = 1; q.push(s);

	while (q.size()) {
		int u = q.front(); q.pop();
		for (int i : bg[u]) {
			if (base[i] == base[u] or match[u] == i) continue;
			if (i == s or (match[i] != -1 and pai[match[i]] != -1))
				contract(u, i);
			else if (pai[i] == -1) {
				pai[i] = u;
				if (match[i] == -1) return i;
				i = match[i];
				vis[i] = 1; q.push(i);
			}
		}
	}

	return -1;
}

vector<pair<int, int>> blossom() {
    
    auto ans = vector<pair<int, int>>();
    for(int i = 0; i < n; i++) {
        match[i] = -1;
    }

	for (int i = 0; i < n; i++) {
        if (match[i] == -1) {
            for (int j : bg[i]) {
                if (match[j] == -1) {
                    match[i] = j;
                    match[j] = i;
                    break;
                }
            }
        }
    }

	for (int i = 0; i < n; i++) {
        if (match[i] == -1) {
            int j = getpath(i);
            if (j == -1) continue;
            while (j != -1) {
                int p = pai[j], pp = match[p];
                match[p] = j;
                match[j] = p;
                j = pp;
            }
    	}
    }

    for(int i = 0; i < n; i++) {
        if(match[i] != -1 && i < match[i]) {
            ans.push_back({i, match[i]});
        }
    }

	return ans;
}


struct Configuration {
    int value;
    mutable int nxt_idx_to_change;
    bitset<64> config;

    Configuration(bitset<64> config, int nxt_idx_to_change) {
        for(int i = 0; i < n; i++) {
            bg[i].clear();
        }

        for(int i = 0; i < n; i++) {
            if(!config[i]) {
                continue;
            }

            for(auto to : g[i]) {
                if(!config[to]) {
                    continue;
                }

                bg[i].push_back(to);
                bg[to].push_back(i);
            }
        }

        this->value = blossom().size();
        this->nxt_idx_to_change = nxt_idx_to_change;
        this->config = config;
    }

    void advance() const {
        this->nxt_idx_to_change++;
    }

    bool operator<(const Configuration &other) const {
        return this->value < other.value;
    }
};

int calculate_num_components() {
    visited = 0;

    int amount = 0;
    for(int i = 0; i < n; i++) {
        if(visited[i]) {
            continue;
        }

        int comp_size = 0;
        int s_size = 0;
        stk[s_size++] = i;
        while(s_size) {
            int cur = stk[--s_size];
            if(visited[cur]) {
                continue;
            }
            visited[cur] = true;
            comp_size++;

            for(auto to : bg[cur]) {
                if(visited[to]) {
                    continue;
                }

                stk[s_size++] = to;
            }
        }

        amount += (comp_size >= 2);
    }

    return amount;
}

int calculate_num_components(bitset<64> config) {
    visited = 0;

    int amount = 0;
    for(int i = 0; i < n; i++) {
        if(visited[i] || !config[i]) {
            continue;
        }

        int comp_size = 0;
        int s_size = 0;
        stk[s_size++] = i;
        while(s_size) {
            int cur = stk[--s_size];
            if(visited[cur]) {
                continue;
            }
            visited[cur] = true;
            comp_size++;

            for(auto to : bg[cur]) {
                if(visited[to] || !config[to]) {
                    continue;
                }

                stk[s_size++] = to;
            }
        }

        amount += (comp_size >= 2);
    }

    return amount;
}

vector<pair<int, int>> extract_best_solution(bitset<64> config) {
    for(int i = 0; i < n; i++) {
        bg[i].clear();
    }

    for(int i = 0; i < n; i++) {
        if(!config[i]) {
            continue;
        }

        for(auto to : g[i]) {
            if(!config[to]) {
                continue;
            }

            bg[i].push_back(to);
            bg[to].push_back(i);
        }
    }

    int num_comps = calculate_num_components();
    if(num_comps >= c) {
        return blossom();
    } else {
        return {};
    }
}


bool can_have_one_extra_component(bitset<64> config, int num_comps_before) {

    for(int i = 0; i < n; i++) {
        for(auto to : bg[i]) {

            auto new_config = config;

            for(auto neigh : bg[i]) {
                new_config[neigh] = false;
            }

            for(auto neigh : bg[to]) {
                new_config[neigh] = false;
            }
            new_config[i] = true;
            new_config[to] = true;

            int num_comps_after = calculate_num_components(new_config);
            if(num_comps_after > num_comps_before) {
                return true;
            }
        }
    }

    return false;
}

vector<pair<int, int>> run() {
    
    auto firstSol = blossom();

    priority_queue<Configuration> candidates;
    auto allNodes = bitset<64>();
    allNodes.set();
    auto base_config = Configuration(allNodes, 0);
    int num_comps = calculate_num_components();
    candidates.push(base_config);

    auto best_solution = base_config;
    if(num_comps < c) {
        best_solution.value = 0;
    }    

    while(candidates.size()) {
        auto &v = candidates.top();
        int node_idx = v.nxt_idx_to_change;

        if(v.value <= best_solution.value) {
            break;
        }
        

        v.advance();
        if(v.nxt_idx_to_change == n) {
            candidates.pop();
        }


        auto config = v.config;
        config[node_idx] = false;

        auto removed_node_solution = Configuration(config, node_idx + 1);
        int num_components = calculate_num_components();
        if(num_components >= c) {
            if(removed_node_solution.value > best_solution.value) {
                best_solution = removed_node_solution;
            }
        } else if(
            num_components != 0 &&
            removed_node_solution.nxt_idx_to_change != n &&
            can_have_one_extra_component(config, num_components)
        ) {
            candidates.push(removed_node_solution);
        }
    }

    return extract_best_solution(best_solution.config);
}


atomic<bool> finished;

void handle_timeout(int) {
    if(finished) {
        return;
    } else {
        cout << "3 4\n";
        cout.flush();
        _exit(0);
    }
}


int main() {

    cin >> n >> m >> c;

    for(int i = 0; i < m; i++) {
        int f, t;
        cin >> f >> t;
        g[f].push_back(t);
        g[t].push_back(f);
    }


    signal(SIGALRM, handle_timeout); // Set the signal handler
    alarm(4);

    auto start_time = chrono::high_resolution_clock::now();
    const auto sol = run();

    finished = true;
    auto end_time = chrono::high_resolution_clock::now();
    chrono::duration<double> elapsed_time = end_time - start_time;

    cout << fixed << setprecision(6);

    if(sol.size()) {
        cout << "1 " << sol.size() << ' ' << elapsed_time.count() << '\n';
        for(auto &[f, t] : sol) {
            cout << f << ' ' << t << '\n';
        }
    } else {
        cout << "0 " << elapsed_time.count() << '\n';
    }

    return 0;
}

// ./main ../test_instances/16_2.txt > ../solutions/backtrack/test1/16_2.txt && ./main ../test_instances/16_3.txt > ../solutions/backtrack/test1/16_3.txt && ./main ../test_instances/16_4.txt > ../solutions/backtrack/test1/16_4.txt && ./main ../test_instances/32_2.txt > ../solutions/backtrack/test1/32_2.txt && ./main ../test_instances/32_3.txt > ../solutions/backtrack/test1/32_3.txt && ./main ../test_instances/32_4.txt > ../solutions/backtrack/test1/32_4.txt && ./main ../test_instances/32_8.txt > ../solutions/backtrack/test1/32_8.txt
// ./main ../test_instances/16_2.txt > ../solutions/backtrack/test2/16_2.txt && ./main ../test_instances/16_3.txt > ../solutions/backtrack/test2/16_3.txt && ./main ../test_instances/16_4.txt > ../solutions/backtrack/test2/16_4.txt && ./main ../test_instances/32_2.txt > ../solutions/backtrack/test2/32_2.txt && ./main ../test_instances/32_3.txt > ../solutions/backtrack/test2/32_3.txt && ./main ../test_instances/32_4.txt > ../solutions/backtrack/test2/32_4.txt && ./main ../test_instances/32_8.txt > ../solutions/backtrack/test2/32_8.txt

// python3 ../statatistics.py ../test_instances/16_2.txt ../solutions/backtrack/test1/16_2.txt ../images/backtrack/test1/16_2.png
// python3 ../statatistics.py ../test_instances/16_3.txt ../solutions/backtrack/test1/16_3.txt ../images/backtrack/test1/16_3.png
// python3 ../statatistics.py ../test_instances/16_4.txt ../solutions/backtrack/test1/16_4.txt ../images/backtrack/test1/16_4.png
// python3 ../statatistics.py ../test_instances/32_2.txt ../solutions/backtrack/test1/32_2.txt ../images/backtrack/test1/32_2.png
// python3 ../statatistics.py ../test_instances/32_3.txt ../solutions/backtrack/test1/32_3.txt ../images/backtrack/test1/32_3.png
// python3 ../statatistics.py ../test_instances/32_4.txt ../solutions/backtrack/test1/32_4.txt ../images/backtrack/test1/32_4.png
// python3 ../statatistics.py ../test_instances/32_8.txt ../solutions/backtrack/test1/32_8.txt ../images/backtrack/test1/32_8.png

// python3 ../statatistics.py ../test_instances/16_2.txt ../solutions/backtrack/test2/16_2.txt ../images/backtrack/test2/16_2.png
// python3 ../statatistics.py ../test_instances/16_3.txt ../solutions/backtrack/test2/16_3.txt ../images/backtrack/test2/16_3.png
// python3 ../statatistics.py ../test_instances/16_4.txt ../solutions/backtrack/test2/16_4.txt ../images/backtrack/test2/16_4.png
// python3 ../statatistics.py ../test_instances/32_2.txt ../solutions/backtrack/test2/32_2.txt ../images/backtrack/test2/32_2.png
// python3 ../statatistics.py ../test_instances/32_3.txt ../solutions/backtrack/test2/32_3.txt ../images/backtrack/test2/32_3.png
// python3 ../statatistics.py ../test_instances/32_4.txt ../solutions/backtrack/test2/32_4.txt ../images/backtrack/test2/32_4.png
// python3 ../statatistics.py ../test_instances/32_8.txt ../solutions/backtrack/test2/32_8.txt ../images/backtrack/test2/32_8.png