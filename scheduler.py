"""
Windows Task Scheduler integration for EDCopilot Chit Chat Updater
Handles automated scheduling and execution
"""

import os
import sys
import subprocess
import logging
from datetime import datetime, timezone
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/scheduler_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Windows Task Scheduler integration for EDCopilot Updater"""
    
    def __init__(self):
        self.task_name = "EDCopilot_ChitChat_Updater"
        self.task_description = "Automated EDCopilot Chit Chat Content Generation"
        self.script_path = Path(__file__).parent / "src" / "main.py"
        self.python_path = sys.executable
        
    def create_task(self, frequency: str = "weekly", time: str = "09:00") -> bool:
        """
        Create a scheduled task for automated execution
        
        Args:
            frequency: Task frequency ('daily', 'weekly', 'biweekly')
            time: Time to run the task (HH:MM format)
            
        Returns:
            True if task created successfully
        """
        try:
            # Build the schtasks command
            cmd = [
                "schtasks", "/create", "/tn", self.task_name,
                "/tr", f'"{self.python_path}" "{self.script_path}"',
                "/sc", self._get_schedule(frequency),
                "/st", time,
                "/f"  # Force creation (overwrite if exists)
            ]
            
            # Add description
            cmd.extend(["/d", self.task_description])
            
            logger.info(f"Creating scheduled task: {' '.join(cmd)}")
            
            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Scheduled task '{self.task_name}' created successfully")
                print(f"✅ Scheduled task '{self.task_name}' created successfully")
                print(f"   Frequency: {frequency}")
                print(f"   Time: {time}")
                return True
            else:
                logger.error(f"❌ Failed to create scheduled task: {result.stderr}")
                print(f"❌ Failed to create scheduled task: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating scheduled task: {str(e)}")
            print(f"❌ Error creating scheduled task: {str(e)}")
            return False
    
    def delete_task(self) -> bool:
        """Delete the scheduled task"""
        try:
            cmd = ["schtasks", "/delete", "/tn", self.task_name, "/f"]
            
            logger.info(f"Deleting scheduled task: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Scheduled task '{self.task_name}' deleted successfully")
                print(f"✅ Scheduled task '{self.task_name}' deleted successfully")
                return True
            else:
                logger.error(f"❌ Failed to delete scheduled task: {result.stderr}")
                print(f"❌ Failed to delete scheduled task: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting scheduled task: {str(e)}")
            print(f"❌ Error deleting scheduled task: {str(e)}")
            return False
    
    def list_tasks(self) -> bool:
        """List all scheduled tasks"""
        try:
            cmd = ["schtasks", "/query", "/fo", "table"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print("📋 Scheduled Tasks:")
                print(result.stdout)
                return True
            else:
                logger.error(f"❌ Failed to list scheduled tasks: {result.stderr}")
                print(f"❌ Failed to list scheduled tasks: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error listing scheduled tasks: {str(e)}")
            print(f"❌ Error listing scheduled tasks: {str(e)}")
            return False
    
    def run_task_now(self) -> bool:
        """Run the scheduled task immediately"""
        try:
            cmd = ["schtasks", "/run", "/tn", self.task_name]
            
            logger.info(f"Running scheduled task: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Scheduled task '{self.task_name}' started successfully")
                print(f"✅ Scheduled task '{self.task_name}' started successfully")
                return True
            else:
                logger.error(f"❌ Failed to run scheduled task: {result.stderr}")
                print(f"❌ Failed to run scheduled task: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running scheduled task: {str(e)}")
            print(f"❌ Error running scheduled task: {str(e)}")
            return False
    
    def get_task_status(self) -> bool:
        """Get the status of the scheduled task"""
        try:
            cmd = ["schtasks", "/query", "/tn", self.task_name, "/fo", "table"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"📋 Task Status for '{self.task_name}':")
                print(result.stdout)
                return True
            else:
                logger.error(f"❌ Failed to get task status: {result.stderr}")
                print(f"❌ Failed to get task status: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error getting task status: {str(e)}")
            print(f"❌ Error getting task status: {str(e)}")
            return False
    
    def _get_schedule(self, frequency: str) -> str:
        """Convert frequency to schtasks schedule format"""
        frequency_map = {
            'daily': 'DAILY',
            'weekly': 'WEEKLY',
            'biweekly': 'WEEKLY /mo 2'  # Every 2 weeks
        }
        
        return frequency_map.get(frequency.lower(), 'WEEKLY')

def main():
    """Main entry point for scheduler management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='EDCopilot Task Scheduler Management')
    parser.add_argument('action', choices=['create', 'delete', 'list', 'run', 'status'],
                       help='Action to perform')
    parser.add_argument('--frequency', choices=['daily', 'weekly', 'biweekly'],
                       default='weekly', help='Task frequency (for create action)')
    parser.add_argument('--time', default='09:00',
                       help='Time to run task (HH:MM format, for create action)')
    
    args = parser.parse_args()
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    scheduler = TaskScheduler()
    
    if args.action == 'create':
        success = scheduler.create_task(args.frequency, args.time)
    elif args.action == 'delete':
        success = scheduler.delete_task()
    elif args.action == 'list':
        success = scheduler.list_tasks()
    elif args.action == 'run':
        success = scheduler.run_task_now()
    elif args.action == 'status':
        success = scheduler.get_task_status()
    else:
        print(f"❌ Unknown action: {args.action}")
        return False
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
