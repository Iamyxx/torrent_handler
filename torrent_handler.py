#!/usr/bin/env python3
"""
Torrent Handler - Automatically process torrent files and add them to Transmission
"""

import os
import time
import logging
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from transmission_rpc import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('torrent_handler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TorrentHandler(FileSystemEventHandler):
    def __init__(self, download_folder, processed_folder, transmission_config):
        self.download_folder = Path(download_folder)
        self.processed_folder = Path(processed_folder)
        self.transmission_config = transmission_config
        
        # Create processed folder if it doesn't exist
        self.processed_folder.mkdir(exist_ok=True)
        
        # Initialize Transmission client
        try:
            self.transmission_client = Client(
                host=transmission_config['host'],
                port=transmission_config['port'],
                username=transmission_config.get('username'),
                password=transmission_config.get('password')
            )
            logger.info("Successfully connected to Transmission")
        except Exception as e:
            logger.error(f"Failed to connect to Transmission: {e}")
            self.transmission_client = None
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        # Convert to string if it's bytes
        src_path = event.src_path.decode('utf-8') if isinstance(event.src_path, bytes) else event.src_path
        file_path = Path(src_path)
        if file_path.suffix.lower() == '.torrent':
            logger.info(f"New torrent file detected: {file_path}")
            self.process_torrent_file(file_path)
    
    def process_torrent_file(self, torrent_path):
        """Process a torrent file by adding it to Transmission and moving it"""
        try:
            # Add torrent to Transmission
            if self.transmission_client:
                with open(torrent_path, 'rb') as f:
                    torrent_data = f.read()
                
                self.transmission_client.add_torrent(
                    torrent=torrent_data,
                    download_dir=self.transmission_config.get('download_dir', '/downloads')
                )
                logger.info(f"Successfully added torrent to Transmission: {torrent_path.name}")
            
            # Move torrent file to processed folder
            new_path = self.processed_folder / torrent_path.name
            torrent_path.rename(new_path)
            logger.info(f"Moved torrent file to: {new_path}")
            
        except Exception as e:
            logger.error(f"Error processing torrent file {torrent_path}: {e}")

def main():
    # Configuration validation
    required_env_vars = {
        'DOWNLOAD_FOLDER': os.getenv('DOWNLOAD_FOLDER'),
        'PROCESSED_FOLDER': os.getenv('PROCESSED_FOLDER'),
        'TRANSMISSION_HOST': os.getenv('TRANSMISSION_HOST'),
        'TRANSMISSION_PORT': os.getenv('TRANSMISSION_PORT'),
        'TRANSMISSION_DOWNLOAD_DIR': os.getenv('TRANSMISSION_DOWNLOAD_DIR')
    }
    optional_env_vars = {
        'TRANSMISSION_USERNAME': os.getenv('TRANSMISSION_USERNAME'),
        'TRANSMISSION_PASSWORD': os.getenv('TRANSMISSION_PASSWORD')
    }
    
    # Check for missing required environment variables
    missing_vars = [var for var, value in required_env_vars.items() if not value]
    
    if missing_vars:
        logger.error("❌ Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        logger.error("")
        logger.error("Please create a .env file with the following variables:")
        logger.error("   DOWNLOAD_FOLDER=/path/to/download/folder")
        logger.error("   PROCESSED_FOLDER=/path/to/processed/folder")
        logger.error("   TRANSMISSION_HOST=localhost")
        logger.error("   TRANSMISSION_PORT=9091")
        logger.error("   TRANSMISSION_DOWNLOAD_DIR=/path/to/download/directory")
        logger.error("")
        logger.error("You can copy env.example to .env and edit it with your settings.")
        sys.exit(1)
    
    # Configuration
    config = {
        'download_folder': required_env_vars['DOWNLOAD_FOLDER'],
        'processed_folder': required_env_vars['PROCESSED_FOLDER'],
        'transmission': {
            'host': required_env_vars['TRANSMISSION_HOST'],
            'port': required_env_vars['TRANSMISSION_PORT'],  # Will convert to int after validation
            'username': optional_env_vars['TRANSMISSION_USERNAME'],
            'password': optional_env_vars['TRANSMISSION_PASSWORD'],
            'download_dir': required_env_vars['TRANSMISSION_DOWNLOAD_DIR']
        }
    }
    
    # Type assertions for the type checker
    assert config['download_folder'] is not None
    assert config['processed_folder'] is not None
    assert config['transmission']['host'] is not None
    assert config['transmission']['port'] is not None
    assert config['transmission']['username'] is not None
    assert config['transmission']['password'] is not None
    assert config['transmission']['download_dir'] is not None
    
    # Convert port to int after validation
    config['transmission']['port'] = int(config['transmission']['port'])
    
    # Validate that folders exist
    download_path = Path(config['download_folder'])
    if not download_path.exists():
        logger.error(f"❌ Download folder does not exist: {config['download_folder']}")
        sys.exit(1)
    
    if not download_path.is_dir():
        logger.error(f"❌ Download folder is not a directory: {config['download_folder']}")
        sys.exit(1)
    
    logger.info(f"✅ Configuration validated successfully")
    logger.info(f"📁 Monitoring folder: {config['download_folder']}")
    logger.info(f"📁 Processed folder: {config['processed_folder']}")
    logger.info(f"🔗 Transmission: {config['transmission']['host']}:{config['transmission']['port']}")
    
    # Create and start the file watcher
    event_handler = TorrentHandler(
        config['download_folder'],
        config['processed_folder'],
        config['transmission']
    )
    
    observer = Observer()
    observer.schedule(event_handler, config['download_folder'], recursive=False)
    observer.start()
    
    logger.info(f"🚀 Starting torrent handler. Monitoring: {config['download_folder']}")
    
    try:
        while True:
            time.sleep(60)  # Sleep for 60 seconds
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Torrent handler stopped")
    
    observer.join()

if __name__ == "__main__":
    main() 