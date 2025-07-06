#!/usr/bin/env python3
"""
Async Hello World script optimized for concurrency and scalability.

This version includes:
- Async/await support for I/O operations
- Concurrent execution capabilities
- Non-blocking operations
- Batch processing optimization
- Connection pooling ready
"""

import asyncio
import time
import logging
import argparse
from typing import List, Optional
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def async_performance_monitor(operation_name: str):
    """Async context manager for monitoring performance."""
    start_time = time.perf_counter()
    logger.info(f"Starting async {operation_name}")
    
    try:
        yield
    except Exception as e:
        logger.error(f"Error in async {operation_name}: {e}")
        raise
    finally:
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logger.info(f"Completed async {operation_name} in {execution_time:.6f} seconds")


async def async_hello_world(message: str = "Hello World", delay: float = 0.0) -> str:
    """
    Async version of hello world with optional delay simulation.
    
    Args:
        message: Message to return
        delay: Simulated I/O delay in seconds
        
    Returns:
        The formatted message
    """
    if delay > 0:
        await asyncio.sleep(delay)  # Simulate I/O operation
    
    return message


async def batch_hello_world(messages: List[str], concurrent_limit: int = 10) -> List[str]:
    """
    Process multiple hello world messages concurrently with rate limiting.
    
    Args:
        messages: List of messages to process
        concurrent_limit: Maximum concurrent operations
        
    Returns:
        List of processed messages
    """
    semaphore = asyncio.Semaphore(concurrent_limit)
    
    async def process_with_semaphore(msg: str) -> str:
        async with semaphore:
            return await async_hello_world(msg, delay=0.001)  # Simulate small I/O delay
    
    async with async_performance_monitor(f"batch processing {len(messages)} messages"):
        tasks = [process_with_semaphore(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process message {i}: {result}")
            else:
                successful_results.append(result)
        
        return successful_results


async def performance_benchmark() -> None:
    """Run async performance benchmarks."""
    logger.info("Running async performance benchmarks...")
    
    # Test different concurrent loads
    test_sizes = [1, 10, 50, 100, 500]
    
    for size in test_sizes:
        messages = [f"Hello World #{i+1}" for i in range(size)]
        
        # Test with different concurrency limits
        for limit in [5, 10, 20]:
            if limit <= size:  # Only test if limit makes sense
                async with async_performance_monitor(f"{size} messages, limit {limit}"):
                    results = await batch_hello_world(messages, limit)
                    logger.info(f"Processed {len(results)}/{size} messages successfully")


async def simulate_web_load() -> None:
    """Simulate concurrent web requests for load testing."""
    logger.info("Simulating concurrent web load...")
    
    async def simulate_request(request_id: int) -> str:
        """Simulate a web request with variable processing time."""
        processing_time = 0.001 + (request_id % 10) * 0.0001  # Variable delay
        await asyncio.sleep(processing_time)
        return await async_hello_world(f"Response {request_id}")
    
    # Simulate 1000 concurrent requests
    request_count = 1000
    
    async with async_performance_monitor(f"simulating {request_count} concurrent requests"):
        tasks = [simulate_request(i) for i in range(request_count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"Handled {successful}/{request_count} requests successfully")


async def main() -> int:
    """Main async function."""
    parser = argparse.ArgumentParser(
        description="Async Hello World script with performance monitoring"
    )
    parser.add_argument(
        "--message",
        default="Hello World",
        help="Base message for processing"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of messages to process concurrently"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run async benchmark tests"
    )
    parser.add_argument(
        "--web-simulation",
        action="store_true",
        help="Run web load simulation"
    )
    parser.add_argument(
        "--concurrent-limit",
        type=int,
        default=10,
        help="Maximum concurrent operations"
    )
    
    try:
        args = parser.parse_args()
        
        if args.benchmark:
            await performance_benchmark()
        elif args.web_simulation:
            await simulate_web_load()
        else:
            # Process messages concurrently
            messages = [f"{args.message} #{i+1}" for i in range(args.count)]
            results = await batch_hello_world(messages, args.concurrent_limit)
            
            for result in results:
                print(result)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Async script interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error in async script: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))