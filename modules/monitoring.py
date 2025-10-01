"""
Monitoring and metrics export utilities.
"""
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
import logging
from .config import config

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and export metrics for monitoring."""
    
    def __init__(self):
        self.enabled = config.enable_metrics
        self.metrics: Dict[str, Any] = defaultdict(lambda: {
            "count": 0,
            "total_duration": 0,
            "errors": 0,
            "last_called": None
        })
        self.request_history: List[Dict[str, Any]] = []
        self.start_time = time.time()
    
    def record_request(self, agent_type: str, duration: float, success: bool = True, error: Optional[str] = None):
        """Record a request metric.
        
        Args:
            agent_type: Type of agent that handled the request
            duration: Request duration in seconds
            success: Whether the request succeeded
            error: Error message if failed
        """
        if not self.enabled:
            return
        
        metric = self.metrics[agent_type]
        metric["count"] += 1
        metric["total_duration"] += duration
        metric["last_called"] = datetime.now().isoformat()
        
        if not success:
            metric["errors"] += 1
        
        # Record in history (keep last 1000)
        self.request_history.append({
            "agent_type": agent_type,
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "success": success,
            "error": error
        })
        
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
        
        logger.debug(f"Recorded metric: {agent_type}, duration={duration:.2f}s, success={success}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics.
        
        Returns:
            Dictionary of metrics
        """
        uptime = time.time() - self.start_time
        total_requests = sum(m["count"] for m in self.metrics.values())
        total_errors = sum(m["errors"] for m in self.metrics.values())
        
        agent_metrics = {}
        for agent_type, metric in self.metrics.items():
            avg_duration = metric["total_duration"] / metric["count"] if metric["count"] > 0 else 0
            error_rate = (metric["errors"] / metric["count"] * 100) if metric["count"] > 0 else 0
            
            agent_metrics[agent_type] = {
                "request_count": metric["count"],
                "average_duration": round(avg_duration, 3),
                "error_count": metric["errors"],
                "error_rate": round(error_rate, 2),
                "last_called": metric["last_called"]
            }
        
        return {
            "uptime_seconds": round(uptime, 2),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "overall_error_rate": round((total_errors / total_requests * 100) if total_requests > 0 else 0, 2),
            "agents": agent_metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_prometheus_format(self) -> str:
        """Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        metrics = self.get_metrics()
        lines = []
        
        # Overall metrics
        lines.append("# HELP agent_uptime_seconds System uptime in seconds")
        lines.append("# TYPE agent_uptime_seconds gauge")
        lines.append(f"agent_uptime_seconds {metrics['uptime_seconds']}")
        
        lines.append("# HELP agent_requests_total Total number of requests")
        lines.append("# TYPE agent_requests_total counter")
        lines.append(f"agent_requests_total {metrics['total_requests']}")
        
        lines.append("# HELP agent_errors_total Total number of errors")
        lines.append("# TYPE agent_errors_total counter")
        lines.append(f"agent_errors_total {metrics['total_errors']}")
        
        # Per-agent metrics
        lines.append("# HELP agent_duration_seconds Average request duration by agent")
        lines.append("# TYPE agent_duration_seconds gauge")
        for agent_type, agent_metrics in metrics["agents"].items():
            lines.append(f'agent_duration_seconds{{agent="{agent_type}"}} {agent_metrics["average_duration"]}')
        
        lines.append("# HELP agent_requests_by_type Request count by agent type")
        lines.append("# TYPE agent_requests_by_type counter")
        for agent_type, agent_metrics in metrics["agents"].items():
            lines.append(f'agent_requests_by_type{{agent="{agent_type}"}} {agent_metrics["request_count"]}')
        
        return "\n".join(lines)
    
    def export_to_file(self, filepath: str = "metrics.json"):
        """Export metrics to a JSON file.
        
        Args:
            filepath: Path to export file
        """
        try:
            metrics = self.get_metrics()
            with open(filepath, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.info(f"Metrics exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
    
    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.request_history.clear()
        self.start_time = time.time()
        logger.info("Metrics reset")


class AlertManager:
    """Simple alert manager for monitoring thresholds."""
    
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.thresholds = {
            "error_rate": 10.0,  # Alert if error rate > 10%
            "avg_duration": 5.0,  # Alert if avg duration > 5 seconds
            "memory_percent": 85.0  # Alert if memory usage > 85%
        }
    
    def check_metrics(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check metrics against thresholds and generate alerts.
        
        Args:
            metrics: Metrics dictionary
            
        Returns:
            List of active alerts
        """
        alerts = []
        
        # Check overall error rate
        if metrics.get("overall_error_rate", 0) > self.thresholds["error_rate"]:
            alerts.append({
                "severity": "warning",
                "metric": "error_rate",
                "value": metrics["overall_error_rate"],
                "threshold": self.thresholds["error_rate"],
                "message": f"High error rate: {metrics['overall_error_rate']}%"
            })
        
        # Check per-agent metrics
        for agent_type, agent_metrics in metrics.get("agents", {}).items():
            if agent_metrics["average_duration"] > self.thresholds["avg_duration"]:
                alerts.append({
                    "severity": "warning",
                    "metric": "avg_duration",
                    "agent": agent_type,
                    "value": agent_metrics["average_duration"],
                    "threshold": self.thresholds["avg_duration"],
                    "message": f"Slow response for {agent_type}: {agent_metrics['average_duration']}s"
                })
        
        if alerts:
            self.alerts.extend(alerts)
            logger.warning(f"Generated {len(alerts)} alerts")
        
        return alerts
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        return self.alerts
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts.clear()
        logger.info("Alerts cleared")


# Global instances
metrics_collector = MetricsCollector()
alert_manager = AlertManager()
