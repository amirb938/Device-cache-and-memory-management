from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import subprocess
import threading
import time
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cache_manage_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Import our existing modules
from cache_fill import list_devices, fill_cache
from calculate_cache import get_packages, get_cache_size, enable_root
from storage_fill_clean import fill_storage, clean_storage, show_free_storage

# Global variable to control monitoring
monitoring_active = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/devices')
def get_devices():
    """Get list of connected devices"""
    try:
        devices = list_devices()
        return jsonify({'success': True, 'devices': devices})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cache/fill', methods=['POST'])
def api_fill_cache():
    """Fill cache for selected packages"""
    try:
        data = request.get_json()
        device = data.get('device')
        package_count = int(data.get('package_count', 10))
        file_size_mb = int(data.get('file_size_mb', 5))
        keyword = data.get('keyword', '')
        
        if not device:
            return jsonify({'success': False, 'error': 'Device not specified'})
        
        # Get packages with keyword filter
        from calculate_cache import get_packages
        all_packages = get_packages(keyword) if keyword else get_packages('.')
        
        if not all_packages:
            return jsonify({'success': False, 'error': f'No packages found matching keyword "{keyword}"'})
        
        # Select random packages from filtered list
        import random
        selected_packages = random.sample(all_packages, min(package_count, len(all_packages)))
        
        # Fill cache for selected packages
        from cache_fill import create_file_in_cache
        filled_count = 0
        
        for package in selected_packages:
            try:
                create_file_in_cache(device, package, file_size_mb)
                filled_count += 1
            except Exception as e:
                print(f"Failed to fill cache for {package}: {e}")
        
        message = f'Cache filled for {filled_count} packages'
        if keyword:
            message += f' (filtered by keyword: "{keyword}")'
        
        return jsonify({
            'success': True, 
            'message': message,
            'filled_count': filled_count,
            'total_filtered_packages': len(all_packages),
            'keyword_used': keyword
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cache/calculate', methods=['POST'])
def api_calculate_cache():
    """Calculate cache sizes for packages"""
    try:
        data = request.get_json()
        package_filter = data.get('package_filter', '.')
        
        enable_root()
        packages = get_packages(package_filter)
        
        if not packages:
            return jsonify({'success': False, 'error': f'No packages found containing "{package_filter}"'})
        
        package_sizes = []
        total_size = 0
        
        for pkg in packages:
            size_kb = get_cache_size(pkg)
            total_size += size_kb
            package_sizes.append({
                'package': pkg,
                'size_kb': size_kb,
                'size_mb': round(size_kb / 1024, 2)
            })
        
        # Sort by size (descending)
        package_sizes.sort(key=lambda x: x['size_kb'], reverse=True)
        
        return jsonify({
            'success': True,
            'packages': package_sizes,
            'total_size_kb': total_size,
            'total_size_mb': round(total_size / 1024, 2),
            'package_count': len(packages)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/storage/fill', methods=['POST'])
def api_fill_storage():
    """Fill device storage"""
    try:
        data = request.get_json()
        device = data.get('device')
        size_mb = int(data.get('size_mb', 100))
        count = int(data.get('count', 1))
        
        if not device:
            return jsonify({'success': False, 'error': 'Device not specified'})
        
        count = max(1, min(count, 100))
        for _ in range(count):
            fill_storage(device, size_mb)
        total_mb = size_mb * count
        return jsonify({'success': True, 'message': f'Storage filled with {count} file(s) x {size_mb}MB = {total_mb}MB'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/storage/clean', methods=['POST'])
def api_clean_storage():
    """Clean fill files from storage"""
    try:
        data = request.get_json()
        device = data.get('device')
        
        if not device:
            return jsonify({'success': False, 'error': 'Device not specified'})
        
        clean_storage(device)
        return jsonify({'success': True, 'message': 'Storage cleaned successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/storage/free', methods=['POST'])
def api_get_free_storage():
    """Get free storage information"""
    try:
        data = request.get_json()
        device = data.get('device')
        
        if not device:
            return jsonify({'success': False, 'error': 'Device not specified'})
        
        # Get storage info using our existing function
        from storage_fill_clean import run_adb
        out, err = run_adb(device, ["shell", "df", "/sdcard"])
        
        if err:
            return jsonify({'success': False, 'error': err})
        
        # Parse the output
        lines = out.strip().split('\n')
        if len(lines) >= 2:
            # Second line contains the actual data
            data_line = lines[1].split()
            if len(data_line) >= 4:
                total_kb = int(data_line[1])
                used_kb = int(data_line[2])
                free_kb = int(data_line[3])
                
                return jsonify({
                    'success': True,
                    'storage': {
                        'total_kb': total_kb,
                        'used_kb': used_kb,
                        'free_kb': free_kb,
                        'total_mb': round(total_kb / 1024, 2),
                        'used_mb': round(used_kb / 1024, 2),
                        'free_mb': round(free_kb / 1024, 2),
                        'usage_percent': round((used_kb / total_kb) * 100, 2)
                    },
                    'raw_output': out
                })
        
        return jsonify({'success': False, 'error': 'Could not parse storage information'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cache/clear_all', methods=['POST'])
def api_clear_all_cache():
    """Clear cache for all applications"""
    try:
        data = request.get_json()
        device = data.get('device')
        include_filter = (data.get('include_filter') or '').strip()
        exclude_filter = (data.get('exclude_filter') or '').strip()
        min_cache_mb = data.get('min_cache_mb')
        max_cache_mb = data.get('max_cache_mb')
        
        if not device:
            return jsonify({'success': False, 'error': 'Device not specified'})
        
        # Enable root access
        enable_root()
        
        # Get all packages
        packages = get_packages('.')

        # Apply include/exclude name filters
        if include_filter:
            packages = [p for p in packages if include_filter in p]
        if exclude_filter:
            packages = [p for p in packages if exclude_filter not in p]
        
        if not packages:
            return jsonify({'success': False, 'error': 'No packages found after applying filters'})
        
        cleared_count = 0
        failed_packages = []
        skipped_packages = []
        
        # Clear cache for each package
        from storage_fill_clean import run_adb
        
        for package in packages:
            try:
                # Size-based filtering if requested
                if min_cache_mb is not None or max_cache_mb is not None:
                    size_kb = get_cache_size(package)
                    size_mb = size_kb / 1024.0
                    if min_cache_mb is not None and size_mb < float(min_cache_mb):
                        skipped_packages.append(f"{package} (size {round(size_mb,2)} MB < min {min_cache_mb} MB)")
                        continue
                    if max_cache_mb is not None and size_mb > float(max_cache_mb):
                        skipped_packages.append(f"{package} (size {round(size_mb,2)} MB > max {max_cache_mb} MB)")
                        continue

                # Clear cache from both directories
                cache_paths = [
                    f"/data/data/{package}/cache",
                    f"/data/user/0/{package}/cache"
                ]
                
                for cache_path in cache_paths:
                    # Remove all files in cache directory
                    cmd = f"rm -rf {cache_path}/*"
                    out, err = run_adb(device, ["shell", cmd])
                    
                    if err and "No such file or directory" not in err:
                        print(f"Warning clearing {cache_path}: {err}")
                
                cleared_count += 1
                
            except Exception as e:
                failed_packages.append(f"{package}: {str(e)}")
                print(f"Failed to clear cache for {package}: {e}")
        
        result_message = f"Cache cleared for {cleared_count} applications"
        if failed_packages:
            result_message += f". Failed for {len(failed_packages)} applications"
        if skipped_packages:
            result_message += f". Skipped {len(skipped_packages)} applications by filters"
        
        return jsonify({
            'success': True,
            'message': result_message,
            'cleared_count': cleared_count,
            'total_packages': len(packages),
            'failed_packages': failed_packages[:10],  # Limit to first 10 failures
            'skipped_packages': skipped_packages[:10],
            'filters': {
                'include_filter': include_filter,
                'exclude_filter': exclude_filter,
                'min_cache_mb': min_cache_mb,
                'max_cache_mb': max_cache_mb
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    global monitoring_active
    monitoring_active = False
    print('Client disconnected')

@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    global monitoring_active
    device = data.get('device')
    if not device:
        emit('monitoring_error', {'error': 'Device not specified'})
        return
    
    monitoring_active = True
    
    def monitor_storage():
        while monitoring_active:
            try:
                from storage_fill_clean import run_adb
                out, err = run_adb(device, ["shell", "df", "/sdcard"])
                
                if not err and out:
                    lines = out.strip().split('\n')
                    if len(lines) >= 2:
                        data_line = lines[1].split()
                        if len(data_line) >= 4:
                            total_kb = int(data_line[1])
                            used_kb = int(data_line[2])
                            free_kb = int(data_line[3])
                            
                            storage_data = {
                                'timestamp': datetime.now().isoformat(),
                                'total_kb': total_kb,
                                'used_kb': used_kb,
                                'free_kb': free_kb,
                                'total_mb': round(total_kb / 1024, 2),
                                'used_mb': round(used_kb / 1024, 2),
                                'free_mb': round(free_kb / 1024, 2),
                                'usage_percent': round((used_kb / total_kb) * 100, 2)
                            }
                            
                            socketio.emit('storage_update', storage_data)
            except Exception as e:
                socketio.emit('monitoring_error', {'error': str(e)})
                break
            
            time.sleep(2)  # Update every 2 seconds
    
    # Start monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_storage)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    emit('monitoring_started', {'message': 'Storage monitoring started'})

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    global monitoring_active
    monitoring_active = False
    emit('monitoring_stopped', {'message': 'Storage monitoring stopped'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
