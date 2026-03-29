#!/bin/bash --login
# CSF3 (UoM) — GPU 训练 BERT 拒识 + 意图
# 用法（在含本项目的目录下）:  sbatch csf3/train_bert.slurm
# 文档: https://ri.itservices.manchester.ac.uk/csf3/batch-slurm/gpu-jobs-slurm/

#SBATCH -p gpuA
#SBATCH -G 1
#SBATCH -n 4
#SBATCH -t 8:00:00
#SBATCH -J robot-bert-train
#SBATCH -o slurm-train-%j.out
#SBATCH -e slurm-train-%j.err

set -euo pipefail

# 任务从提交目录启动；请在本仓库根目录执行 sbatch
cd "${SLURM_SUBMIT_DIR}"
export PYTHONPATH="${SLURM_SUBMIT_DIR}"

# 按集群实际模块名修改（登录节点执行: module avail cuda  /  module spider pytorch）
module purge
module load cuda/12.6.2

# 使用你在登录节点创建的 conda 环境（名称与 conda create 时一致）
eval "$(conda shell.bash hook)"
conda activate robot

# 依赖需已安装: torch(含CUDA)、transformers、sklearn、tqdm、boto3 等
python - <<'PY'
import torch
print("torch", torch.__version__, "cuda", torch.cuda.is_available())
if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))
PY

echo "=== train reject ==="
python train/run.py --model bert --data reject --device cuda --gpu 0 --batch-size 64

echo "=== train intent ==="
python train/run.py --model bert --data intent --device cuda --gpu 0 --batch-size 64

echo "=== done ==="
ls -la train/saved/reject/ train/saved/intent/ 2>/dev/null || true
