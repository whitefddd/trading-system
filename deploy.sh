#!/bin/bash

# 安装系统依赖
sudo apt update
sudo apt install -y python3-pip postgresql nginx

# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# 配置 PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE trading_db;"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '123456';"

# 安装项目依赖
cd backend
pip3 install -r requirements.txt

cd ../frontend
npm install
npm run build

# 配置 Nginx
sudo bash -c 'cat > /etc/nginx/sites-available/trading_system << EOL
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    location / {
        root /path/to/your/frontend/dist;  # 替换为你的前端构建目录的实际路径
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
}
EOL'

# 启用站点配置
sudo ln -s /etc/nginx/sites-available/trading_system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 创建服务文件
sudo bash -c 'cat > /etc/systemd/system/trading_system.service << EOL
[Unit]
Description=Trading System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/your/backend  # 替换为你的后端目录的实际路径
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOL'

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable trading_system
sudo systemctl start trading_system 