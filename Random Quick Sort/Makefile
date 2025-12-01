CXX = g++
CXXFLAGS = -O3 -std=c++17 -march=native
TARGET = rqs

all: $(TARGET)

$(TARGET): rqs.cpp
	$(CXX) $(CXXFLAGS) rqs.cpp -o $(TARGET)

clean:
	rm -f $(TARGET) *.csv

.PHONY: all clean
