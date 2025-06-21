# torrent_handler

Auto handle the torrent file in the download folder to keep the download folder clean. And achieve auto load .torrent file to transmission.

## Features

- 🔍 **File Monitoring**: Automatically detects new `.torrent` files in your download folder
- 📤 **Transmission Integration**: Seamlessly adds torrent files to Transmission via RPC
- 🧹 **Auto Cleanup**: Moves processed torrent files to a designated folder
- 📝 **Logging**: Comprehensive logging for monitoring and debugging
- ⚙️ **Configurable**: Easy configuration via environment variables

## Requirements

- Python 3.7+
- Transmission with RPC enabled
- macOS, Linux, or Windows

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Iamyxx/torrent_handler.git
   cd torrent_handler
   ```

2. **Quick Setup** (Recommended):
   ```bash
   # Run the automated setup script
   ./setup.sh
   ```
   
   This script will:
   - Create a virtual environment
   - Install all dependencies
   - Create a .env file from template
   - Provide next steps

3. **Manual Setup** (Alternative):
   ```bash
   # Create a virtual environment
   python3 -m venv venv
   
   # Activate the virtual environment
   source venv/bin/activate
   
   # Your prompt should now show (venv) indicating the virtual environment is active
   ```

4. **Install dependencies**:
   ```bash
   # Make sure your virtual environment is activated, then:
   pip install -r requirements.txt
   ```

   **Note**: If you encounter "externally-managed-environment" error on macOS, you must use a virtual environment as shown above. This is a security feature in newer Python installations.

5. **Configure Transmission RPC**:
   - Open Transmission preferences
   - Go to "Remote" tab
   - Enable "Allow remote access"
   - Set username and password
   - Note the port (default: 9091)

6. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

## Configuration

**Important**: All environment variables are now required except for `TRANSMISSION_USERNAME` and `TRANSMISSION_PASSWORD`, which can be left empty if your Transmission instance does not require authentication.

Create a `.env` file with the following variables:

```bash
# Folder to monitor for new torrent files (REQUIRED)
DOWNLOAD_FOLDER=/path/to/download/folder

# Folder to move processed torrent files (REQUIRED)
PROCESSED_FOLDER=/path/to/processed/folder

# Transmission RPC Configuration (REQUIRED)
TRANSMISSION_HOST=localhost
TRANSMISSION_PORT=9091
TRANSMISSION_USERNAME=your_username   # Leave empty if not required
TRANSMISSION_PASSWORD=your_password   # Leave empty if not required

# Transmission download directory (REQUIRED)
TRANSMISSION_DOWNLOAD_DIR=/path/to/download/directory
```

**Note**: If your Transmission server does not require a username or password, you can leave `TRANSMISSION_USERNAME` and `TRANSMISSION_PASSWORD` blank in your `.env` file:

```bash
TRANSMISSION_USERNAME=
TRANSMISSION_PASSWORD=
```

The application will validate that the download folder exists and is accessible before starting.

## Usage

### Run the torrent handler:
```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Run the torrent handler
python torrent_handler.py
```

The script will:
1. Start monitoring your download folder for new `.torrent` files
2. Automatically add new torrent files to Transmission
3. Move processed torrent files to the `PROCESSED_FOLDER`
4. Log all activities to both console and `torrent_handler.log`

### Stop the handler:
Press `Ctrl+C` to stop the torrent handler gracefully.

### Deactivate virtual environment:
```bash
deactivate
```

## Troubleshooting

### Common Issues

1. **"externally-managed-environment" error**:
   - This is expected on newer macOS Python installations
   - Always use a virtual environment: `python3 -m venv venv && source venv/bin/activate`
   - Never use `--break-system-packages` flag as it can break your system

2. **Connection to Transmission failed**:
   - Ensure Transmission is running
   - Check RPC settings in Transmission preferences
   - Verify username/password in `.env` file

3. **Permission errors**:
   - Ensure the script has read/write permissions to the folders
   - Check Transmission download directory permissions

4. **File not being processed**:
   - Check the log file for error messages
   - Ensure the torrent file has `.torrent` extension
   - Verify the download folder path is correct

### Virtual Environment Management

```bash
# Create virtual environment (one-time setup)
python3 -m venv venv

# Activate virtual environment (every time you work on the project)
source venv/bin/activate

# Install dependencies (after activation)
pip install -r requirements.txt

# Run the application (after activation)
python torrent_handler.py

# Deactivate when done
deactivate
```

### Logs

Check `torrent_handler.log` for detailed information about:
- File detection events
- Transmission connection status
- Processing errors
- File movement operations

## Development

### Project Structure
```
torrent_handler/
├── torrent_handler.py    # Main application
├── requirements.txt      # Python dependencies
├── env.example          # Example configuration
├── README.md           # This file
├── venv/               # Virtual environment (created during setup)
└── torrent_handler.log # Application logs
```

### Adding Features

The modular design makes it easy to extend:
- Add new file type handlers in the `TorrentHandler` class
- Implement additional Transmission operations
- Add notification systems (email, push notifications)
- Create a GUI interface

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
