# Deployment Guide - Text2Trait Frontend

This guide explains how to deploy the Text2Trait frontend application using Gunicorn and the provided WSGI entry point.

## Prerequisites

1. Python 3.12 or higher
2. Install dependencies from `text2trait_forntend_app/src/pyproject.toml`:
   (Note: The directory name contains a typo 'forntend' - this is the actual name in the repository)
   ```bash
   cd text2trait_forntend_app/src
   pip install -r pyproject.toml
   # or with poetry:
   poetry install
   ```

3. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```

## WSGI Entry Point

The `wsgi_t2tfe.py` file at the root of the repository provides a Gunicorn-compatible WSGI entry point for the Text2Trait frontend Dash application.

## Usage

### Local Development

For local development and testing:

```bash
python wsgi_t2tfe.py
```

The application will be available at `http://localhost:8050/`

### Production Deployment with Gunicorn

For production deployment, use Gunicorn:

```bash
gunicorn wsgi_t2tfe:server --bind 0.0.0.0:8050 --workers 4
```

#### Recommended Gunicorn Configuration

```bash
gunicorn wsgi_t2tfe:server \
    --bind 0.0.0.0:8050 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/text2trait/access.log \
    --error-logfile /var/log/text2trait/error.log \
    --log-level info
```

#### Configuration Options Explained

- `--bind 0.0.0.0:8050` - Bind to all interfaces on port 8050
- `--workers 4` - Use 4 worker processes (adjust based on CPU cores: 2-4 × CPU cores)
- `--timeout 120` - Worker timeout in seconds (adjust based on your needs)
- `--access-logfile` - Path for access logs
- `--error-logfile` - Path for error logs
- `--log-level` - Logging level (debug, info, warning, error, critical)

### Running as a Systemd Service

Create a systemd service file `/etc/systemd/system/text2trait-frontend.service`:

```ini
[Unit]
Description=Text2Trait Frontend Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/Text2Trait_devel
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn wsgi_t2tfe:server \
    --bind 0.0.0.0:8050 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/text2trait/access.log \
    --error-logfile /var/log/text2trait/error.log
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable text2trait-frontend
sudo systemctl start text2trait-frontend
sudo systemctl status text2trait-frontend
```

### Using with Nginx (Reverse Proxy)

Create an Nginx configuration `/etc/nginx/sites-available/text2trait`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed by Dash)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Increase timeouts for long-running requests
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/text2trait /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Variables

If your application requires environment variables, set them before running:

```bash
export DATA_PATH=/path/to/data
export LOG_LEVEL=INFO
gunicorn wsgi_t2tfe:server --bind 0.0.0.0:8050 --workers 4
```

## Monitoring and Logs

Monitor the application:

```bash
# View logs
tail -f /var/log/text2trait/access.log
tail -f /var/log/text2trait/error.log

# Check service status
sudo systemctl status text2trait-frontend

# View systemd logs
sudo journalctl -u text2trait-frontend -f
```

## Performance Tuning

### Worker Count

The optimal number of workers depends on your server:

- CPU-bound applications: `(2 × CPU cores) + 1`
- I/O-bound applications: `(4 × CPU cores) + 1`

For the Dash application (mostly I/O-bound):

```bash
# For a 4-core server:
gunicorn wsgi_t2tfe:server --bind 0.0.0.0:8050 --workers 17
```

### Worker Class

For better async support, use the gevent worker class:

```bash
pip install gevent
gunicorn wsgi_t2tfe:server \
    --bind 0.0.0.0:8050 \
    --workers 4 \
    --worker-class gevent \
    --worker-connections 1000
```

## Troubleshooting

### Application won't start

1. Check Python path and dependencies:
   ```bash
   python -c "from wsgi_t2tfe import server; print('OK')"
   ```

2. Check Gunicorn syntax:
   ```bash
   gunicorn --check-config wsgi_t2tfe:server
   ```

3. Check logs for errors:
   ```bash
   tail -f /var/log/text2trait/error.log
   ```

### High memory usage

Reduce the number of workers:

```bash
gunicorn wsgi_t2tfe:server --bind 0.0.0.0:8050 --workers 2
```

### Timeout errors

Increase the timeout:

```bash
gunicorn wsgi_t2tfe:server --bind 0.0.0.0:8050 --timeout 300
```

## Security Considerations

1. **Never expose Gunicorn directly to the internet** - Always use a reverse proxy like Nginx
2. **Use HTTPS** - Configure SSL/TLS in Nginx
3. **Firewall rules** - Restrict access to port 8050 to localhost only
4. **Keep dependencies updated** - Regularly update Python packages
5. **Use a dedicated user** - Don't run as root

## Additional Resources

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Dash Deployment Guide](https://dash.plotly.com/deployment)
- [Nginx Documentation](https://nginx.org/en/docs/)
