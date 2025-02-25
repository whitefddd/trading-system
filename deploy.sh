#!/bin/bash

# 安装系统依赖
sudo apt update
sudo apt install -y python3-pip postgresql nginx

# 安装 Python 虚拟环境
sudo apt install -y python3-venv

# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# 配置 PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE trading_db;"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '123456';"

# 克隆代码
cd /root
git clone https://github.com/whitefddd/trading-system.git
cd trading-system

# 安装项目依赖
cd backend
# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
pip install uvicorn

cd ../frontend
# 安装全局 vite
sudo npm install -g vite
npm install
sudo npm run build

# 配置 Nginx
sudo bash -c 'cat > /etc/nginx/sites-available/trading_system << EOL
server {
    listen 80;
    server_name www.100xlabs.top;

    location / {
        root /root/trading-system/frontend/dist;
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
User=root
WorkingDirectory=/root/trading-system/backend
Environment="PATH=/root/trading-system/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/root/trading-system/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOL'

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable trading_system
sudo systemctl start trading_system

# 添加 SSL 证书（使用 Let's Encrypt）
sudo apt install -y certbot python3-certbot-nginx
<<<<<<< HEAD
sudo certbot --nginx -d www.100xlabs.top --non-interactive --agree-tos --email 100xlabs168@gmail.com 
=======
sudo certbot --nginx -d www.100xlabs.top --non-interactive --agree-tos --email 100xlabs168@gmail.com 
>>>>>>> 6c62b5ee81ff738c98fddea8fe241e4557313d94
