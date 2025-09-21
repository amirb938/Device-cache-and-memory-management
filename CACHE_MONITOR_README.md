# Live Cache Monitor Feature

## Overview
A new live monitoring feature has been added to track the cache size of a specific Android application in real-time.

## Features
- **Real-time Cache Monitoring**: Monitor cache size of any installed app by package name
- **Live Updates**: Cache size updates every 2 seconds
- **WebSocket Integration**: Uses Socket.IO for real-time communication
- **Persian UI**: Fully localized interface in Persian/Farsi

## How to Use

### 1. Start the Application
```bash
python app.py
```
The application will be available at `http://localhost:5000`

### 2. Connect Your Android Device
- Enable USB Debugging on your Android device
- Connect via USB or ADB over WiFi
- Verify connection with `adb devices`

### 3. Use the Cache Monitor
1. **Select Device**: Choose your connected device from the dropdown
2. **Enter Package Name**: Input the full package name of the app you want to monitor
   - Example: `com.android.chrome` for Chrome browser
   - Example: `com.whatsapp` for WhatsApp
3. **Start Monitoring**: Click "شروع مانیتورینگ کش" (Start Cache Monitoring)
4. **View Live Data**: The cache size will update every 2 seconds showing:
   - Package name
   - Cache size in KB and MB
   - Device name
   - Last update timestamp
5. **Stop Monitoring**: Click "توقف مانیتورینگ کش" (Stop Cache Monitoring) when done

## Technical Details

### Backend Implementation
- **WebSocket Handlers**: 
  - `start_cache_monitoring`: Initiates monitoring for a specific package
  - `stop_cache_monitoring`: Stops the monitoring
  - `cache_update`: Sends real-time cache size data
- **Cache Size Calculation**: Uses `du -s` command on Android device cache directories
- **Root Access**: Automatically enables ADB root for cache access

### Frontend Implementation
- **Real-time Updates**: Socket.IO client receives live cache data
- **Persian Interface**: Full RTL support with Persian text
- **Responsive Design**: Works on desktop and mobile browsers
- **Error Handling**: Comprehensive error messages and validation

### Cache Directories Monitored
The system monitors cache in these Android directories:
- `/data/data/{package_name}/cache`
- `/data/user/0/{package_name}/cache`

## Example Package Names
- Chrome: `com.android.chrome`
- WhatsApp: `com.whatsapp`
- Instagram: `com.instagram.android`
- Telegram: `org.telegram.messenger`
- YouTube: `com.google.android.youtube`
- Facebook: `com.facebook.katana`

## Requirements
- Python 3.6+
- Flask
- Flask-SocketIO
- ADB (Android Debug Bridge)
- Root access on Android device (for cache monitoring)

## Troubleshooting
1. **No devices found**: Ensure USB debugging is enabled and device is connected
2. **Cache size shows 0**: Verify the package name is correct and app is installed
3. **Permission denied**: Ensure ADB root access is available
4. **Connection lost**: Check device connection and restart monitoring

## Security Note
This feature requires root access to read cache directories. Use only on trusted devices and networks.
