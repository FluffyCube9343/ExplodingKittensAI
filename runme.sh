clear && echo "Start" && g++ -std=c++17 main.cpp -o binaries/mainout \
-O3 -march=native -flto -ffast-math && ./binaries/mainout