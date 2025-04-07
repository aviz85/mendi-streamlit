"""
Usage Logger for Streamlit Application

This module provides a logger implementation for tracking and displaying
user interactions and process events within the Streamlit application.
"""

import logging
import os
import datetime
from typing import Optional, List, Dict, Any
import json

class StreamlitLogger:
    """
    Logger for Streamlit interface that stores logs and can display them in the UI
    
    This logger collects logs with timestamps and categories, and provides methods
    to display them, retrieve them, or save them to a file.
    """
    
    def __init__(self):
        """Initialize a new Streamlit logger"""
        self.logs = []
        self.logger = logging.getLogger(__name__)
    
    def log(self, message: str, icon: str = "ℹ️"):
        """
        Add a log entry with timestamp and icon
        
        Parameters:
            message: The message to log
            icon: Icon to display with the message (emoji)
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "message": message,
            "icon": icon
        }
        self.logs.append(entry)
        
        # Also log to standard logger
        self.logger.info(f"{icon} {message}")
    
    def get_logs(self) -> List[Dict[str, str]]:
        """
        Get all log entries
        
        Returns:
            List of log entries
        """
        return self.logs
    
    def clear_logs(self):
        """Clear all log entries"""
        self.logs = []
        self.log("יומן הפעולות נוקה", "🧹")
    
    def save_logs(self, filename: str) -> bool:
        """
        Save logs to a file
        
        Parameters:
            filename: The name of the file to save logs to
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, ensure_ascii=False, indent=2)
            self.log(f"יומן הפעולות נשמר לקובץ: {filename}", "💾")
            return True
        except Exception as e:
            self.log(f"שגיאה בשמירת יומן הפעולות: {str(e)}", "❌")
            return False
    
    def display_logs(self, streamlit_container) -> None:
        """
        Display logs in a Streamlit container
        
        Parameters:
            streamlit_container: Streamlit container to display logs in
        """
        if not self.logs:
            streamlit_container.info("אין פעולות מתועדות")
            return
            
        for entry in self.logs:
            streamlit_container.write(
                f"**{entry['timestamp']}** {entry['icon']} {entry['message']}"
            )

# Singleton instance
streamlit_logger = StreamlitLogger()
