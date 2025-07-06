"""
Configuration management for performance optimization.

This module provides centralized configuration for:
- Performance monitoring settings
- Environment-specific optimizations
- Resource limits and thresholds
- Logging configuration
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class PerformanceConfig:
    """Configuration for performance monitoring and optimization."""
    
    # Monitoring settings
    enable_profiling: bool = False
    enable_memory_tracking: bool = True
    log_performance_metrics: bool = True
    performance_log_file: str = "performance.log"
    
    # Resource limits
    max_concurrent_operations: int = 50
    memory_warning_threshold_mb: float = 100.0
    execution_time_warning_threshold_s: float = 1.0
    
    # Optimization settings
    batch_size: int = 100
    async_timeout_s: float = 30.0
    cache_enabled: bool = True
    lazy_loading: bool = True
    
    # Environment-specific settings
    environment: str = "development"  # development, staging, production
    debug_mode: bool = True
    verbose_logging: bool = True
    
    @classmethod
    def from_environment(cls) -> "PerformanceConfig":
        """Create configuration from environment variables."""
        return cls(
            enable_profiling=_get_bool_env("PERF_ENABLE_PROFILING", False),
            enable_memory_tracking=_get_bool_env("PERF_ENABLE_MEMORY", True),
            log_performance_metrics=_get_bool_env("PERF_LOG_METRICS", True),
            performance_log_file=os.getenv("PERF_LOG_FILE", "performance.log"),
            
            max_concurrent_operations=_get_int_env("PERF_MAX_CONCURRENT", 50),
            memory_warning_threshold_mb=_get_float_env("PERF_MEMORY_THRESHOLD", 100.0),
            execution_time_warning_threshold_s=_get_float_env("PERF_TIME_THRESHOLD", 1.0),
            
            batch_size=_get_int_env("PERF_BATCH_SIZE", 100),
            async_timeout_s=_get_float_env("PERF_ASYNC_TIMEOUT", 30.0),
            cache_enabled=_get_bool_env("PERF_CACHE_ENABLED", True),
            lazy_loading=_get_bool_env("PERF_LAZY_LOADING", True),
            
            environment=os.getenv("ENVIRONMENT", "development"),
            debug_mode=_get_bool_env("DEBUG", True),
            verbose_logging=_get_bool_env("VERBOSE_LOGGING", True),
        )
    
    def get_optimized_settings(self) -> Dict[str, Any]:
        """Get environment-optimized settings."""
        if self.environment == "production":
            return {
                "debug_mode": False,
                "verbose_logging": False,
                "enable_profiling": False,
                "max_concurrent_operations": 100,
                "batch_size": 500,
            }
        elif self.environment == "staging":
            return {
                "debug_mode": False,
                "verbose_logging": True,
                "enable_profiling": True,
                "max_concurrent_operations": 75,
                "batch_size": 250,
            }
        else:  # development
            return {
                "debug_mode": True,
                "verbose_logging": True,
                "enable_profiling": True,
                "max_concurrent_operations": 25,
                "batch_size": 50,
            }
    
    def apply_optimizations(self) -> None:
        """Apply environment-specific optimizations."""
        optimized = self.get_optimized_settings()
        
        for key, value in optimized.items():
            if hasattr(self, key):
                setattr(self, key, value)


def _get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean value from environment variable."""
    value = os.getenv(key, "").lower()
    return value in ("true", "1", "yes", "on") if value else default


def _get_int_env(key: str, default: int = 0) -> int:
    """Get integer value from environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def _get_float_env(key: str, default: float = 0.0) -> float:
    """Get float value from environment variable."""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default


class CacheConfig:
    """Configuration for caching mechanisms."""
    
    def __init__(self, config: PerformanceConfig):
        self.enabled = config.cache_enabled
        self.cache_dir = Path("cache")
        self.max_cache_size_mb = 50.0
        self.cache_ttl_hours = 24
        self.auto_cleanup = True
        
        # Create cache directory if needed
        if self.enabled:
            self.cache_dir.mkdir(exist_ok=True)


class LoggingConfig:
    """Configuration for logging optimization."""
    
    def __init__(self, config: PerformanceConfig):
        self.performance_logging = config.log_performance_metrics
        self.log_file = config.performance_log_file
        self.verbose = config.verbose_logging
        self.debug = config.debug_mode
        
        # Set appropriate log levels based on environment
        if config.environment == "production":
            self.level = "WARNING"
        elif config.environment == "staging":
            self.level = "INFO"
        else:
            self.level = "DEBUG" if config.debug_mode else "INFO"


# Global configuration instance
CONFIG = PerformanceConfig.from_environment()
CONFIG.apply_optimizations()

# Specialized configurations
CACHE_CONFIG = CacheConfig(CONFIG)
LOGGING_CONFIG = LoggingConfig(CONFIG)