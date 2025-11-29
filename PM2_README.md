# PM2 Configuration Guide

This project is configured to run with PM2, a process manager for Node.js and Python applications.

## Prerequisites

1. **Install PM2 globally:**
   ```bash
   npm install -g pm2
   ```

2. **Ensure your virtual environment is set up:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## PM2 Commands

### Start the application
```bash
pm2 start ecosystem.config.js
```

### Stop the application
```bash
pm2 stop device-cache-manager
```

### Restart the application
```bash
pm2 restart device-cache-manager
```

### View application status
```bash
pm2 status
```

### View logs
```bash
# View all logs
pm2 logs device-cache-manager

# View only error logs
pm2 logs device-cache-manager --err

# View only output logs
pm2 logs device-cache-manager --out
```

### Monitor application
```bash
pm2 monit
```

### Stop and delete the application
```bash
pm2 delete device-cache-manager
```

### Save PM2 process list (for auto-start on reboot)
```bash
pm2 save
pm2 startup
```

## Configuration Details

The `ecosystem.config.js` file contains the following configuration:

- **Name**: `device-cache-manager`
- **Script**: `run.py`
- **Interpreter**: Python 3 from virtual environment (`./venv/bin/python3`)
- **Instances**: 1 (single instance)
- **Auto-restart**: Enabled
- **Memory limit**: 500MB (auto-restart if exceeded)
- **Port**: 5000 (configurable via PORT environment variable)
- **Logs**: Stored in `./logs/` directory
  - Error logs: `pm2-error.log`
  - Output logs: `pm2-out.log`
  - Combined logs: `pm2-combined.log`

## Environment Variables

You can modify environment variables in `ecosystem.config.js`:

- `FLASK_ENV`: Set to `production` for production mode (disables debug)
- `PORT`: Server port (default: 5000)

## Production Mode

When `FLASK_ENV=production`, the application runs with:
- Debug mode disabled
- Production-optimized settings

## Troubleshooting

1. **Application won't start:**
   - Check if virtual environment exists: `ls -la venv/`
   - Verify Python interpreter path in `ecosystem.config.js`
   - Check logs: `pm2 logs device-cache-manager --err`

2. **Port already in use:**
   - Change the PORT in `ecosystem.config.js` or stop the conflicting service

3. **Permission issues:**
   - Ensure the logs directory is writable: `chmod 755 logs/`

## Auto-start on System Reboot

To make PM2 start your application automatically on system reboot:

```bash
pm2 save
pm2 startup
# Follow the instructions provided by the startup command
```

