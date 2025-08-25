# 1. 选择一个官方的、轻量的Python作为基础镜像
FROM python:3.11-slim

# 2. 在镜像内创建一个工作目录
WORKDIR /app

# 3. 复制依赖文件到工作目录
COPY requirements.txt .

# 4. 安装所有依赖
RUN pip install --no-cache-dir -r requirements.txt

# 5. 复制你项目的所有文件到工作目录
COPY . .

# 6. 定义容器启动时要执行的命令
CMD ["python", "main.py"]