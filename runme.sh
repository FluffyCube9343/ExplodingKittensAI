clear && echo "Start" && \
g++ -std=c++17 main.cpp -o main.out \
-O2 -march=native -flto -ffast-math -funroll-loops && \
echo "compiled"
./main.out