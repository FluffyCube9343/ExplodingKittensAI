g++ -std=c++17 main.cpp -o binaries/app
valgrind --tool=callgrind ./binaries/app
kcachegrind callgrind.out.*
