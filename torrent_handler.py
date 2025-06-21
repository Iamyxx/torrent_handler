#!/usr/bin/env python3
"""
Torrent Handler - Automatically process torrent files and add them to Transmission
"""

import os
import time
import logging
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
    # Configuration
    config = {
        'download_folder': os.getenv('DOWNLOAD_FOLDER', '/Users/xiangyao/Downloads'),
        'processed_folder': os.getenv('PROCESSED_FOLDER', '/Users/xiangyao/Downloads/processed_torrents'),
        'transmission': {
            'host': os.getenv('TRANSMISSION_HOST', 'localhost'),
            'port': int(os.getenv('TRANSMISSION_PORT', 9091)),
            'username': os.getenv('TRANSMISSION_USERNAME'),
            'password': os.getenv('TRANSMISSION_PASSWORD'),
            'download_dir': os.getenv('TRANSMISSION_DOWNLOAD_DIR', '/Users/xiangyao/Downloads')
        }
    }
    
    # Create and start the file watcher
    event_handler = TorrentHandler(
        config['download_folder'],
        config['processed_folder'],
        config['transmission']
    )
    
    observer = Observer()
    observer.schedule(event_handler, config['download_folder'], recursive=False)
    observer.start()
    
    logger.info(f"Starting torrent handler. Monitoring: {config['download_folder']}")
    
    try:
        while True:
            time.sleep(60)  # Sleep for 60 seconds
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Torrent handler stopped")
    
    observer.join()

if __name__ == "__main__":
    main() 