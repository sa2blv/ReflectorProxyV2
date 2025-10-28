# ReflectorProxyV2

ReflectorProxyV2 is a PHP-based proxy/reflector designed to forward and handle traffic between services — supporting standard HTTP and Server-Sent Events (SSE).  
It is optimized to run with **PHP-FPM**, **Nginx**, and **Redis** for performance and reliability.

## 🚀 Features

- Lightweight proxy/reflector written in PHP  
- Supports HTTP and SSE (Server-Sent Events)  
- Redis support for caching or session handling  
- Simple configuration using `.env` or config files  
- Fully compatible with Nginx + PHP-FPM  
- Built-in logging and error handling  

## 🧩 Requirements

| Component | Recommended Version |
|------------|--------------------|
| OS | Debian 12 / Ubuntu 22.04 |
| PHP | 8.1 or later |
| Nginx | Latest stable version |
| PHP-FPM | Enabled and running |
| Redis | Latest stable version |
| Git | Installed |
| (Optional) SSL | For HTTPS via Certbot |

## ⚙️ Installation

### 1. Install dependencies

```bash
sudo apt update
sudo apt install -y git nginx php php-fpm php-cli php-json php-curl php-mbstring php-xml php-sqlite3 php-redis unzip
```

### 2. Install and configure Redis

Install Redis:

```bash
sudo apt install redis-server -y
```

Edit the Redis configuration file:

```bash
sudo nano /etc/redis/redis.conf
```

Add or modify the following lines:

```
bind 127.0.0.1 ::1
requirepass MyStrongPassword123!
```

Restart Redis to apply the changes:

```bash
sudo systemctl restart redis-server
```

> ⚠️ **Important:**  
> The Redis password `MyStrongPassword123!` must also be configured in both:  
> - `config.php` (inside the ReflectorProxyV2 project)  
> - `/etc/reflectorproxy` (system-level configuration if used)

Example (`config.php`):

```php
$redis = [
    'host' => '127.0.0.1',
    'port' => 6379,
    'password' => 'MyStrongPassword123!'
];
```

### 3. Clone the repository

```bash
cd /var/www
sudo git clone https://github.com/sa2blv/ReflectorProxyV2.git
cd ReflectorProxyV2
```

### 4. Set permissions

```bash
sudo chown -R www-data:www-data /var/www/ReflectorProxyV2
sudo chmod -R 755 /var/www/ReflectorProxyV2
```

### 5. Verify PHP-FPM

```bash
sudo systemctl status php8.1-fpm
sudo systemctl enable --now php8.1-fpm
```

Default socket:
```
/run/php/php8.1-fpm.sock
```

## 🌐 Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/reflectorproxy
```

Add the following:

```nginx
server {
    listen 80;
    server_name reflectorproxy.local;

    root /var/www/ReflectorProxyV2/public;
    index index.php index.html;

    access_log /var/log/nginx/reflectorproxy.access.log;
    error_log /var/log/nginx/reflectorproxy.error.log;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

Enable and reload Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/reflectorproxy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Application Configuration

```bash
cp .env.example .env
nano .env
```

Example:

```env
APP_ENV=production
APP_PORT=8080
LOG_PATH=/var/www/ReflectorProxyV2/logs/
TARGET_URL=http://127.0.0.1:6200
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=MyStrongPassword123!
```

## 🧪 Testing the Installation

```bash
sudo systemctl restart php8.1-fpm
sudo systemctl restart redis-server
sudo systemctl reload nginx
```

Check Redis:

```bash
redis-cli -a MyStrongPassword123! ping
```

Output:

```
PONG
```

Test in browser:
```
http://your-server-ip/
```

## 🔒 Enable HTTPS (Optional)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 🧭 Logs & Troubleshooting

| Component | Path |
|------------|------|
| Nginx Access Log | `/var/log/nginx/reflectorproxy.access.log` |
| Nginx Error Log | `/var/log/nginx/reflectorproxy.error.log` |
| PHP-FPM Logs | `/var/log/php8.1-fpm.log` |
| Redis Logs | `/var/log/redis/redis-server.log` |

## 🔄 Updating

```bash
cd /var/www/ReflectorProxyV2
sudo git pull
sudo systemctl reload nginx
```

## 🧱 License

Released under the [MIT License](LICENSE).

**Maintainer:** [sa2blv](https://github.com/sa2blv)  
**Contributions:** Pull requests and improvements are welcome!
