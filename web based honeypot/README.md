# Web-Based Honeypot

A containerized web honeypot designed to attract and log malicious activities. This honeypot simulates various common web services and captures detailed information about attack attempts.

## Features

- **Multiple Attack Vectors**: Simulates admin panels, phpMyAdmin, WordPress, and API endpoints
- **Comprehensive Logging**: Logs all interactions to both files and SQLite database
- **Real-time Monitoring**: Live attack monitoring and statistics
- **Docker Containerized**: Easy deployment and isolation
- **Automated Management**: Scripts for deployment, monitoring, and maintenance

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Linux/Unix environment (tested on Ubuntu/Debian)
- Port 8080 available (and optionally port 80)

### Deployment

1. **Clone or create the project directory:**
   ```bash
   mkdir web-honeypot && cd web-honeypot
   ```

2. **Create the required files:**
   - Copy all the provided files (honeypot.py, Dockerfile, docker-compose.yml, requirements.txt, deploy.sh)

3. **Make the deployment script executable:**
   ```bash
   chmod +x deploy.sh
   ```

4. **Deploy the honeypot:**
   ```bash
   ./deploy.sh deploy
   ```

The honeypot will be available at:
- Main interface: http://localhost:8080
- Admin panel: http://localhost:8080/admin
- Logs viewer: http://localhost:8080/honeypot/admin/logs

## Management Commands

The `deploy.sh` script provides several management commands:

```bash
# Deploy the honeypot
./deploy.sh deploy

# Check status
./deploy.sh status

# View recent logs
./deploy.sh logs

# View live logs
./deploy.sh live-logs

# Monitor attacks in real-time
./deploy.sh monitor

# View statistics
./deploy.sh stats

# Stop the honeypot
./deploy.sh stop

# Restart the honeypot
./deploy.sh restart

```

## Honeypot Endpoints

The honeypot simulates several common attack targets:

### Web Interfaces
- `/` - Main page with links to admin areas
- `/admin` - Fake admin login panel
- `/phpmyadmin`, `/pma` - phpMyAdmin simulation
- `/wp-admin` - WordPress admin simulation

### API Endpoints
- `/api/login` - API login endpoint
- `/api/users` - User information endpoint

### Sensitive Files
- `/.env` - Environment configuration file
- `/config.php` - Configuration file
- `/wp-config.php` - WordPress configuration
- `/.git/config` - Git configuration

### Other Services
- `/ssh` - SSH service simulation

## Data Storage

The honeypot stores data in two formats:

1. **Log Files** (`logs/honeypot.log`): Human-readable log entries
2. **SQLite Database** (`data/honeypot.db`): Structured data for analysis

### Database Schema
```sql
interactions (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    ip_address TEXT,
    user_agent TEXT,
    method TEXT,
    path TEXT,
    headers TEXT,
    data TEXT,
    interaction_type TEXT
)
```

## Security Considerations

### For Production Deployment:

1. **Network Isolation**: Deploy in an isolated network segment
2. **Monitoring**: Set up external monitoring for the honeypot itself
3. **Log Management**: Regularly backup and analyze logs
4. **Resource Limits**: Monitor resource usage to prevent DoS
5. **Legal Compliance**: Ensure compliance with local laws regarding honeypots

### Security Features:
- Runs as non-root user inside container
- Resource limits configured
- No sensitive data exposure
- Comprehensive logging for forensic analysis

## Monitoring and Analysis

### Real-time Monitoring
```bash
# Monitor live attacks
./deploy.sh monitor

# View live logs
./deploy.sh live-logs
```

### Statistical Analysis
```bash
# View interaction statistics
./deploy.sh stats
```

This shows:
- Total interactions
- Top attacking IP addresses
- Most targeted paths
- Login attempt counts
- Recent activity

### Log Analysis

You can analyze the SQLite database directly:
```bash
sqlite3 data/honeypot.db "SELECT * FROM interactions WHERE interaction_type='admin_login_attempt';"
```

Or examine raw logs:
```bash
grep "login_attempt" logs/honeypot.log
```

## Customization

### Adding New Endpoints

Edit `honeypot.py` to add new routes:
```python
@app.route('/your-endpoint')
def your_endpoint():
    log_request("your_endpoint_access")
    return "Your response"
```

### Modifying Logging

Adjust logging levels and formats in the logging configuration section of `honeypot.py`.

### Changing Ports

Modify the `docker-compose.yml` file to change port mappings:
```yaml
ports:
  - "your-port:8080"
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   sudo netstat -tulpn | grep :8080
   ```

2. **Permission Denied**
   ```bash
   # Fix permissions
   chmod +x deploy.sh
   sudo chown -R $USER:$USER logs data
   ```

3. **Container Won't Start**
   ```bash
   # Check container logs
   docker-compose logs honeypot
   ```

4. **Database Access Issues**
   ```bash
   # Check database file permissions
   ls -la data/honeypot.db
   ```

### Health Checks

The container includes health checks. Monitor with:
```bash
docker-compose ps
```

### Log Rotation

Logs are automatically rotated by the logrotate service in the compose file.

## Legal and Ethical Considerations

- **Purpose**: Use only for legitimate security research, education, or network defense
- **Privacy**: Be aware of data collection laws in your jurisdiction
- **Notification**: Consider notification requirements for monitoring
- **Responsible Use**: Do not use to attack or harm others

## Contributing

To contribute improvements:
1. Test changes in an isolated environment
2. Ensure logging captures new attack vectors
3. Update documentation
4. Consider security implications

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Docker and container logs
3. Verify network connectivity and permissions

## License

This honeypot