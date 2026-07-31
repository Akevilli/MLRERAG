#!/bin/bash

/bin/ollama serve &
pid=$!

sleep 5

ollama pull qwen3-embedding:0.6b

wait $pid
