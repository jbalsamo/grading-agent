"""
Utility functions for the Master Agent System.
"""
import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitor system performance and health."""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.agent_usage = {}
        self.response_times = []
    
    def log_request(self, agent_type: str, response_time: float, success: bool = True):
        """Log a request for monitoring."""
        self.request_count += 1
        if not success:
            self.error_count += 1
        
        if agent_type not in self.agent_usage:
            self.agent_usage[agent_type] = {"requests": 0, "errors": 0, "avg_time": 0}
        
        self.agent_usage[agent_type]["requests"] += 1
        if not success:
            self.agent_usage[agent_type]["errors"] += 1
        
        # Update average response time
        current_avg = self.agent_usage[agent_type]["avg_time"]
        current_count = self.agent_usage[agent_type]["requests"]
        new_avg = ((current_avg * (current_count - 1)) + response_time) / current_count
        self.agent_usage[agent_type]["avg_time"] = new_avg
        
        self.response_times.append(response_time)
        
        # Keep only last 100 response times for memory efficiency
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        uptime = time.time() - self.start_time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            "average_response_time": avg_response_time,
            "agent_usage": self.agent_usage,
            "requests_per_minute": (self.request_count / (uptime / 60)) if uptime > 0 else 0
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

class ConfigValidator:
    """Validate system configuration."""
    
    @staticmethod
    def validate_azure_config() -> Dict[str, Any]:
        """Validate Azure OpenAI configuration."""
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_CHAT_DEPLOYMENT"
        ]
        
        validation_result = {
            "valid": True,
            "missing_vars": [],
            "warnings": [],
            "config_values": {}
        }
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                validation_result["valid"] = False
                validation_result["missing_vars"].append(var)
            else:
                # Mask sensitive values
                if "KEY" in var:
                    validation_result["config_values"][var] = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                else:
                    validation_result["config_values"][var] = value
        
        # Check optional variables
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        if not api_version:
            validation_result["warnings"].append("AZURE_OPENAI_API_VERSION not set, using default")
        else:
            validation_result["config_values"]["AZURE_OPENAI_API_VERSION"] = api_version
        
        return validation_result
    
    @staticmethod
    def validate_data_directory(data_dir: str = "data") -> Dict[str, Any]:
        """Validate data directory setup."""
        validation_result = {
            "valid": True,
            "exists": os.path.exists(data_dir),
            "writable": False,
            "files": {},
            "issues": []
        }
        
        if validation_result["exists"]:
            try:
                # Test write permissions
                test_file = os.path.join(data_dir, ".write_test")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                validation_result["writable"] = True
            except Exception as e:
                validation_result["valid"] = False
                validation_result["issues"].append(f"Directory not writable: {e}")
            
            # Check for existing files
            interactions_file = os.path.join(data_dir, "interactions.jsonl")
            context_file = os.path.join(data_dir, "context.json")
            
            if os.path.exists(interactions_file):
                try:
                    with open(interactions_file, "r") as f:
                        lines = f.readlines()
                    validation_result["files"]["interactions"] = {
                        "exists": True,
                        "line_count": len(lines),
                        "size_bytes": os.path.getsize(interactions_file)
                    }
                except Exception as e:
                    validation_result["files"]["interactions"] = {
                        "exists": True,
                        "error": str(e)
                    }
            
            if os.path.exists(context_file):
                try:
                    with open(context_file, "r") as f:
                        context_data = json.load(f)
                    validation_result["files"]["context"] = {
                        "exists": True,
                        "keys": list(context_data.keys()),
                        "size_bytes": os.path.getsize(context_file)
                    }
                except Exception as e:
                    validation_result["files"]["context"] = {
                        "exists": True,
                        "error": str(e)
                    }
        else:
            validation_result["valid"] = False
            validation_result["issues"].append("Data directory does not exist")
        
        return validation_result

class SystemHealthChecker:
    """Check system health and connectivity."""
    
    def __init__(self, master_agent=None):
        self.master_agent = master_agent
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive system health check."""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        # Check configuration
        config_check = ConfigValidator.validate_azure_config()
        health_report["checks"]["configuration"] = {
            "status": "pass" if config_check["valid"] else "fail",
            "details": config_check
        }
        
        # Check data directory
        data_check = ConfigValidator.validate_data_directory()
        health_report["checks"]["data_directory"] = {
            "status": "pass" if data_check["valid"] else "fail",
            "details": data_check
        }
        
        # Check agent connectivity
        if self.master_agent:
            agent_check = self._check_agent_connectivity()
            health_report["checks"]["agent_connectivity"] = agent_check
        
        # Check system resources
        resource_check = self._check_system_resources()
        health_report["checks"]["system_resources"] = resource_check
        
        # Determine overall status
        failed_checks = [check for check in health_report["checks"].values() if check["status"] == "fail"]
        if failed_checks:
            health_report["overall_status"] = "unhealthy"
        elif any(check["status"] == "warning" for check in health_report["checks"].values()):
            health_report["overall_status"] = "degraded"
        
        return health_report
    
    def _check_agent_connectivity(self) -> Dict[str, Any]:
        """Check if agents can connect to Azure OpenAI."""
        try:
            # Simple test message
            test_response = self.master_agent.chat("test")
            return {
                "status": "pass" if test_response and "error" not in test_response.lower() else "fail",
                "details": {
                    "test_successful": True,
                    "response_length": len(test_response) if test_response else 0
                }
            }
        except Exception as e:
            return {
                "status": "fail",
                "details": {
                    "test_successful": False,
                    "error": str(e)
                }
            }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = "pass"
            warnings = []
            
            if cpu_percent > 80:
                status = "warning"
                warnings.append(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > 85:
                status = "warning"
                warnings.append(f"High memory usage: {memory.percent}%")
            
            if disk.percent > 90:
                status = "warning"
                warnings.append(f"High disk usage: {disk.percent}%")
            
            return {
                "status": status,
                "details": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "warnings": warnings
                }
            }
        except ImportError:
            return {
                "status": "warning",
                "details": {
                    "message": "psutil not available for resource monitoring"
                }
            }
        except Exception as e:
            return {
                "status": "fail",
                "details": {
                    "error": str(e)
                }
            }

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_system_info() -> Dict[str, Any]:
    """Get basic system information."""
    import platform
    import sys
    
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "architecture": platform.architecture(),
        "hostname": platform.node(),
        "current_directory": os.getcwd(),
        "environment_variables": {
            key: value for key, value in os.environ.items() 
            if not any(sensitive in key.upper() for sensitive in ["KEY", "SECRET", "PASSWORD", "TOKEN"])
        }
    }

def cleanup_logs(log_dir: str = "logs", days_to_keep: int = 7) -> Dict[str, Any]:
    """Clean up old log files."""
    if not os.path.exists(log_dir):
        return {"status": "no_logs_directory", "cleaned_files": 0}
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    cleaned_files = 0
    total_size_cleaned = 0
    
    try:
        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            if os.path.isfile(file_path):
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_modified < cutoff_date:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    cleaned_files += 1
                    total_size_cleaned += file_size
        
        return {
            "status": "success",
            "cleaned_files": cleaned_files,
            "size_cleaned": format_file_size(total_size_cleaned)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "cleaned_files": cleaned_files
        }
