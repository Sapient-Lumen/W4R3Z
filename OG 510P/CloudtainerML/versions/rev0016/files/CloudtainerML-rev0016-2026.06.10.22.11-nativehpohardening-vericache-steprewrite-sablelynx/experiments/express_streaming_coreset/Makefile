CXX ?= g++
CXXFLAGS ?= -O3 -std=c++17 -Wall -Wextra -pedantic
OUT ?= express_coreset
JSON ?= ../../artifacts/probe-results/REV0014_EXPRESS_STREAMING_CORESET_SMOKE.json

all: $(OUT)

$(OUT): express_coreset.cpp
	$(CXX) $(CXXFLAGS) $< -o $@

run: $(OUT)
	./$(OUT) $(JSON)

clean:
	rm -f $(OUT)
