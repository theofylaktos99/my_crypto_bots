# main.py - Main Application Entry Point
import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

import logging
from src.utils.logger import setup_logging
from src.utils.config_manager import SecurityConfig as ConfigManager
from src.dashboard.main_dashboard import MainDashboard

def main():
    """Main application entry point"""
    
    # Setup logging
    setup_logging(
        level="INFO",
        log_file="logs/main_app.log",
        console=True
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Crypto Trading Bot System")
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager()
        
        # Validate configuration
        if not config_manager.validate_config():
            logger.error("❌ Configuration validation failed")
            return False
        
        # Initialize and start main dashboard
        dashboard = MainDashboard(config_manager)
        dashboard.run()
        
    except KeyboardInterrupt:
        logger.info("👋 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
