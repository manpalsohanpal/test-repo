#!/usr/bin/env python3
"""
Optimized Hello World script with performance monitoring and error handling.

This enhanced version includes:
- Execution time measurement
- Memory usage tracking
- Error handling
- Logging infrastructure
- Command-line argument support
- Performance profiling capabilities
"""

import sys
import time
import logging
import argparse
from typing import Optional
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('performance.log')
    ]
)
logger = logging.getLogger(__name__)


@contextmanager
def performance_monitor(operation_name: str):
    """Context manager for monitoring performance of operations."""
    start_time = time.perf_counter()
    start_memory = get_memory_usage()
    
    logger.info(f"Starting {operation_name}")
    
    try:
        yield
    except Exception as e:
        logger.error(f"Error in {operation_name}: {e}")
        raise
    finally:
        end_time = time.perf_counter()
        end_memory = get_memory_usage()
        
        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory if end_memory and start_memory else 0
        
        logger.info(f"Completed {operation_name}:")
        logger.info(f"  Execution time: {execution_time:.6f} seconds")
        logger.info(f"  Memory delta: {memory_delta:.2f} MB")


def get_memory_usage() -> Optional[float]:
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        # psutil not available, return None
        return None


def hello_world(message: str = "Hello World", repeat: int = 1) -> None:
    """
    Print hello world message with optional customization.
    
    Args:
        message: Custom message to print (default: "Hello World")
        repeat: Number of times to repeat the message (default: 1)
    """
    if repeat < 1:
        raise ValueError("Repeat count must be at least 1")
    
    if repeat > 1000:
        logger.warning(f"Large repeat count: {repeat}. This may impact performance.")
    
    with performance_monitor(f"printing message {repeat} times"):
        for i in range(repeat):
            print(f"{message}" + (f" #{i+1}" if repeat > 1 else ""))


def main() -> int:
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Optimized Hello World script with performance monitoring"
    )
    parser.add_argument(
        "--message", 
        default="Hello World",
        help="Custom message to print (default: Hello World)"
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times to repeat the message (default: 1)"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run benchmark tests"
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Enable detailed profiling"
    )
    
    try:
        args = parser.parse_args()
        
        if args.profile:
            import cProfile
            import pstats
            from io import StringIO
            
            profiler = cProfile.Profile()
            profiler.enable()
        
        if args.benchmark:
            run_benchmark()
        else:
            hello_world(args.message, args.repeat)
        
        if args.profile:
            profiler.disable()
            s = StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats()
            logger.info(f"Profiling results:\n{s.getvalue()}")
        
        return 0
        
    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def run_benchmark() -> None:
    """Run performance benchmarks."""
    logger.info("Running performance benchmarks...")
    
    test_cases = [
        ("Single message", "Hello World", 1),
        ("10 messages", "Hello World", 10),
        ("100 messages", "Hello World", 100),
        ("Custom message", "Performance Test", 50),
    ]
    
    for test_name, message, repeat in test_cases:
        with performance_monitor(f"benchmark: {test_name}"):
            hello_world(message, repeat)


if __name__ == "__main__":
    sys.exit(main())