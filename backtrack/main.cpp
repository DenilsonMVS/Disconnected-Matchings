
#include <bits/stdc++.h>
#include <sys/wait.h>
#define show(v) cout << #v ": " << (v) << endl;

using namespace std;

#define INFEASIBLE 0
#define OPTIMAL 1
#define FEASIBLE 2
#define UNKNOWN 3


int main(int argc, const char * const argv[]) {

    if(argc != 2) {
        cout << "Usage: main <input_file>\n";
        return 0;
    }

    const auto input_file = argv[1];
    auto file = ifstream(input_file);



    int ttt;
    file >> ttt;
    while (ttt--) {
        int n, m, c;
        file >> n >> m >> c;

        auto edges = vector<pair<int, int>>(m);
        for (auto &[f, s] : edges) {
            file >> f >> s;
        }

        // Create pipes for communication
        int pipe_stdin[2], pipe_stdout[2];
        if (pipe(pipe_stdin) == -1 || pipe(pipe_stdout) == -1) {
            perror("pipe");
            return 1;
        }

        pid_t pid = fork();
        if (pid == -1) {
            perror("fork");
            return 1;
        }

        if (pid == 0) { // Child process
            // Redirect stdin and stdout
            dup2(pipe_stdin[0], STDIN_FILENO);
            dup2(pipe_stdout[1], STDOUT_FILENO);

            // Close unused pipe ends
            close(pipe_stdin[0]);
            close(pipe_stdin[1]);
            close(pipe_stdout[0]);
            close(pipe_stdout[1]);

            // Replace child process with "backtrack"
            execlp("./backtrack", "backtrack", (char *)NULL);
            perror("execlp");
            exit(1);
        } else { // Parent process
            // Close unused pipe ends
            close(pipe_stdin[0]);
            close(pipe_stdout[1]);

            // Write data to the child's stdin
            dprintf(pipe_stdin[1], "%d %d %d\n", n, m, c);
            for (const auto &[f, s] : edges) {
                dprintf(pipe_stdin[1], "%d %d\n", f, s);
            }
            close(pipe_stdin[1]); // Signal EOF to the child process
            

            // Read child's stdout and print to parent's stdout
            char buffer[1024];
            ssize_t bytes_read;
            while ((bytes_read = read(pipe_stdout[0], buffer, sizeof(buffer) - 1)) > 0) {
                buffer[bytes_read] = '\0'; // Null-terminate the string
                cout << buffer;
            }
            close(pipe_stdout[0]);

            // Wait for the child process to finish
            int status;
            waitpid(pid, &status, 0);
            if (WIFEXITED(status)) {
                // cout << "Child process exited with status: " << WEXITSTATUS(status) << endl;
            } else {
                cerr << "Child process terminated abnormally" << endl;
            }
        }
    }

    return 0;
}
