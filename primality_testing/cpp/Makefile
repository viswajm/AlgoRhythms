# C++ Makefile for Linux
# Primality Testing Core Implementation

CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O3 -march=native -fPIC
LDFLAGS = -lm

SRCS = utils.cpp fermat.cpp miller_rabin.cpp main.cpp
OBJS = $(SRCS:.cpp=.o)
TARGET = primality_test

.PHONY: all clean run test

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)
	@echo "Build successful: $@"

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
	@echo "Clean complete"

run: $(TARGET)
	./$(TARGET)

test: $(TARGET)
	@echo "Testing n=17 with k=10"
	./$(TARGET) 17 10
	@echo ""
	@echo "Testing Carmichael number 561"
	./$(TARGET) 561 10 0
