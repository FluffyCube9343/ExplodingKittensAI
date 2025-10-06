clear && echo "Start" && \
g++ -std=c++17 main.cpp -o main.out \
-O3 -march=native -flto -ffast-math -funroll-loops && \
./main.out