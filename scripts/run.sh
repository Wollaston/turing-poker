#!/bin/bash
#SBATCH --job-name=GEPA
#SBATCH --output=logs/run_%j.out
#SBATCH --error=logs/run_%j.err
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=12
#SBATCH --mem=24G
#SBATCH --nodelist=student-gpu-001

export HF_HOME=/data/matthewflynn/.cache/huggingface
export UV_CACHE_DIR=/data/matthewflynn/.cache/uv

uv sync

uv run scripts/dspy_optimize.py $1
