#include <bits/stdc++.h>
#define show(v) cout << #v ": " << (v) << endl;

using namespace std;

#define INFEASIBLE 0
#define OPTIMAL 1
#define FEASIBLE 2
#define UNKNOWN 3

vector<pair<int, vector<vector<int>>>> load_graphs(const char filename[]) {
    auto file = ifstream(filename);
    
    int num_cases;
    file >> num_cases;

    auto graphs = vector<pair<int, vector<vector<int>>>>();
    graphs.reserve(num_cases);

    while(num_cases--) {
        int n, m, components;
        file >> n >> m >> components;

        auto graph = vector<vector<int>>(n, vector<int>());

        while(m--) {
            int f, t;
            file >> f >> t;

            graph[f].push_back(t);
            graph[t].push_back(f);
        }

        graphs.push_back({components, move(graph)});
    }

    return graphs;
}


void remove_from_vec(vector<int> &v, int value) {
    for(int i = 0; i < v.size(); i++) {
        if(v[i] == value) {
            swap(v[i], v.back());
            v.pop_back();
            return;
        }
    }
}

#define MAX 10000

int n, m, c;
int stk[MAX];
int match[MAX];
vector<int> g[MAX];
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
		for (int i : g[u]) {
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
            for (int j : g[i]) {
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

std::pair<vector<int>, int> remove_node(int node_idx) {
    for(auto to : g[node_idx]) {
        // Poderia ser O(1) ou O(log(n))
        // Mas comos os valores são baixos,
        // Acredito que assim seja mais eficiente
        remove_from_vec(g[to], node_idx);
    }
    auto tmp = vector<int>();
    swap(tmp, g[node_idx]);
    
    visited = 0;
    int s_size = 0;
    int amount_dfs = 0;
    for(auto to : tmp) {
        if(visited[to]) {
            continue;
        }
        
        int size = 0;
        stk[s_size++] = to;
        while(s_size) {
            auto cur = stk[--s_size];
            if(visited[cur]) {
                continue;
            }
            visited[cur] = true;
            size++;

            for(auto to : g[cur]) {
                if(visited[to]) {
                    continue;
                }

                stk[s_size++] = to;
            }
        }

        amount_dfs += (size >= 2);
    }

    return {tmp, amount_dfs};
}

void readd_node(int node_idx, vector<int> &tmp) {
    swap(tmp, g[node_idx]);
    for(auto to : g[node_idx]) {
        g[to].push_back(node_idx);
    }
}

vector<pair<int, int>> rec(int node_idx, int num_components) {
    if(node_idx == n || num_components == 0) {
        return vector<pair<int, int>>();
    }

    if(num_components >= c) {
        return blossom();
    }

    auto [tmp, amount_dfs] = remove_node(node_idx);
    

    auto res1 = vector<pair<int, int>>();

    int new_num_components = num_components + amount_dfs - 1;
    if(new_num_components >= c) {
        res1 = blossom();
    } else {
        res1 = rec(node_idx + 1, new_num_components);
    }


    readd_node(node_idx, tmp);


    auto res2 = rec(node_idx + 1, num_components);

    if(res1.size() > res2.size()) {
        return res1;
    } else {
        return res2;
    }
}


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

            for(auto to : g[cur]) {
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
    int start_comps = calculate_num_components();
    const auto sol = rec(0, start_comps);

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

// python3 ../statatistics.py ../test_instances/16_2.txt ../solutions/backtrack/test1/16_2.txt ../images/backtrack/test1/16_2.png
// python3 ../statatistics.py ../test_instances/16_3.txt ../solutions/backtrack/test1/16_3.txt ../images/backtrack/test1/16_3.png
// python3 ../statatistics.py ../test_instances/16_4.txt ../solutions/backtrack/test1/16_4.txt ../images/backtrack/test1/16_4.png
// python3 ../statatistics.py ../test_instances/32_2.txt ../solutions/backtrack/test1/32_2.txt ../images/backtrack/test1/32_2.png
// python3 ../statatistics.py ../test_instances/32_3.txt ../solutions/backtrack/test1/32_3.txt ../images/backtrack/test1/32_3.png
// python3 ../statatistics.py ../test_instances/32_4.txt ../solutions/backtrack/test1/32_4.txt ../images/backtrack/test1/32_4.png
// python3 ../statatistics.py ../test_instances/32_8.txt ../solutions/backtrack/test1/32_8.txt ../images/backtrack/test1/32_8.png