"""
Unit tests for utility modules.
"""
import pytest
import time
from modules.utils import SystemMonitor, SystemHealthChecker


@pytest.mark.unit
class TestSystemMonitor:
    """Test SystemMonitor functionality."""
    
    def test_initialization(self):
        """Test SystemMonitor initialization."""
        monitor = SystemMonitor()
        assert monitor is not None
        assert hasattr(monitor, 'start_time')
        assert hasattr(monitor, 'request_count')
        assert hasattr(monitor, 'error_count')
    
    def test_log_request_success(self):
        """Test logging a successful request."""
        monitor = SystemMonitor()
        initial_count = monitor.request_count
        
        monitor.log_request("chat", 0.5, success=True)
        assert monitor.request_count == initial_count + 1
        assert monitor.error_count == 0
    
    def test_log_request_error(self):
        """Test logging a failed request."""
        monitor = SystemMonitor()
        initial_errors = monitor.error_count
        
        monitor.log_request("chat", 0.5, success=False)
        assert monitor.error_count == initial_errors + 1
    
    def test_get_stats(self):
        """Test getting system statistics."""
        monitor = SystemMonitor()
        
        # Record some activity
        monitor.log_request("chat", 0.5, success=True)
        monitor.log_request("analysis", 1.0, success=True)
        monitor.log_request("chat", 0.3, success=False)
        
        stats = monitor.get_stats()
        
        assert 'total_requests' in stats
        assert 'total_errors' in stats
        assert 'error_rate' in stats
        assert 'uptime_formatted' in stats
        assert stats['total_requests'] == 3
        assert stats['total_errors'] == 1
        assert abs(stats['error_rate'] - 33.33) < 1  # ~33.33%
    
    def test_uptime_calculation(self):
        """Test uptime calculation."""
        monitor = SystemMonitor()
        time.sleep(0.1)  # Wait a bit
        
        stats = monitor.get_stats()
        assert 'uptime_seconds' in stats
        assert stats['uptime_seconds'] > 0
    
    def test_response_time_tracking(self):
        """Test response time tracking."""
        monitor = SystemMonitor()
        
        monitor.log_request("chat", 0.5, success=True)
        monitor.log_request("chat", 1.0, success=True)
        monitor.log_request("chat", 0.75, success=True)
        
        stats = monitor.get_stats()
        assert 'average_response_time' in stats
        # Average of 0.5, 1.0, 0.75 = 0.75
        assert abs(stats['average_response_time'] - 0.75) < 0.01
    
    def test_agent_usage_tracking(self):
        """Test that agent usage is tracked correctly."""
        monitor = SystemMonitor()
        
        monitor.log_request("chat", 0.5, success=True)
        monitor.log_request("chat", 0.6, success=True)
        monitor.log_request("analysis", 1.0, success=True)
        
        stats = monitor.get_stats()
        assert 'agent_usage' in stats
        assert 'chat' in stats['agent_usage']
        assert 'analysis' in stats['agent_usage']
        assert stats['agent_usage']['chat']['requests'] == 2
        assert stats['agent_usage']['analysis']['requests'] == 1


@pytest.mark.unit
@pytest.mark.requires_api
class TestSystemHealthChecker:
    """Test SystemHealthChecker functionality."""
    
    def test_health_check_structure(self, master_agent):
        """Test that health check returns proper structure."""
        health_checker = SystemHealthChecker(master_agent)
        result = health_checker.run_health_check()
        
        assert 'overall_status' in result
        assert 'checks' in result
        assert 'timestamp' in result
        assert result['overall_status'] in ['healthy', 'degraded', 'unhealthy']
        assert isinstance(result['checks'], dict)
    
    def test_health_check_includes_all_checks(self, master_agent):
        """Test that health check includes expected checks."""
        health_checker = SystemHealthChecker(master_agent)
        result = health_checker.run_health_check()
        
        checks = result['checks']
        
        # Should have checks for core components
        assert 'configuration' in checks
        assert 'data_directory' in checks
        assert 'agent_connectivity' in checks  # Present when master_agent provided
        assert 'system_resources' in checks
    
    def test_health_check_status_values(self, master_agent):
        """Test that health check statuses are valid."""
        health_checker = SystemHealthChecker(master_agent)
        result = health_checker.run_health_check()
        
        valid_statuses = ['pass', 'warning', 'fail']
        
        for check_name, check_result in result['checks'].items():
            assert 'status' in check_result
            assert check_result['status'] in valid_statuses
    
    def test_health_check_without_agent(self):
        """Test health check without master agent."""
        health_checker = SystemHealthChecker()
        result = health_checker.run_health_check()
        
        # Should still have configuration and data checks
        assert 'configuration' in result['checks']
        assert 'data_directory' in result['checks']
        assert 'system_resources' in result['checks']
        # Should not have agent connectivity check
        assert 'agent_connectivity' not in result['checks'] or result['checks']['agent_connectivity']['status'] == 'fail'
