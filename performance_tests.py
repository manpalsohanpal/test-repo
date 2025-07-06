#!/usr/bin/env python3
"""
Comprehensive performance testing suite for hello world optimizations.

This module provides:
- Benchmark tests for different implementations
- Memory usage analysis
- Execution time comparisons
- Scalability testing
- Regression detection
"""

import time
import gc
import subprocess
import sys
from typing import Dict, List, Callable, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Results from a performance benchmark."""
    name: str
    execution_time: float
    memory_usage: float
    operations_per_second: float
    success_rate: float
    error_count: int


class PerformanceTester:
    """Main performance testing class."""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.baseline_results: Dict[str, BenchmarkResult] = {}
    
    def measure_execution_time(self, func: Callable, *args, **kwargs) -> Tuple[Any, float]:
        """Measure execution time of a function."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time
    
    def measure_memory_usage(self, func: Callable, *args, **kwargs) -> Tuple[Any, float]:
        """Measure memory usage of a function."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # Force garbage collection before measurement
            gc.collect()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            result = func(*args, **kwargs)
            
            gc.collect()
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            
            return result, memory_after - memory_before
        except ImportError:
            logger.warning("psutil not available, memory measurement disabled")
            return func(*args, **kwargs), 0.0
    
    def run_script_benchmark(self, script_path: str, args: List[str] = None) -> BenchmarkResult:
        """Benchmark a Python script execution."""
        if args is None:
            args = []
        
        cmd = [sys.executable, script_path] + args
        
        try:
            start_time = time.perf_counter()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            success = result.returncode == 0
            
            return BenchmarkResult(
                name=f"Script: {Path(script_path).name}",
                execution_time=execution_time,
                memory_usage=0.0,  # Not measured for subprocess
                operations_per_second=1.0 / execution_time if execution_time > 0 else 0,
                success_rate=1.0 if success else 0.0,
                error_count=0 if success else 1
            )
        except subprocess.TimeoutExpired:
            return BenchmarkResult(
                name=f"Script: {Path(script_path).name} (TIMEOUT)",
                execution_time=30.0,
                memory_usage=0.0,
                operations_per_second=0.0,
                success_rate=0.0,
                error_count=1
            )
        except Exception as e:
            logger.error(f"Error running script {script_path}: {e}")
            return BenchmarkResult(
                name=f"Script: {Path(script_path).name} (ERROR)",
                execution_time=0.0,
                memory_usage=0.0,
                operations_per_second=0.0,
                success_rate=0.0,
                error_count=1
            )
    
    def benchmark_function(self, func: Callable, name: str, iterations: int = 1000, 
                          *args, **kwargs) -> BenchmarkResult:
        """Benchmark a function over multiple iterations."""
        logger.info(f"Benchmarking {name} with {iterations} iterations...")
        
        execution_times = []
        memory_usages = []
        errors = 0
        
        for i in range(iterations):
            try:
                # Measure execution time
                _, exec_time = self.measure_execution_time(func, *args, **kwargs)
                execution_times.append(exec_time)
                
                # Measure memory every 100 iterations to avoid overhead
                if i % 100 == 0:
                    _, memory_delta = self.measure_memory_usage(func, *args, **kwargs)
                    memory_usages.append(memory_delta)
                
            except Exception as e:
                errors += 1
                logger.debug(f"Error in iteration {i}: {e}")
        
        if not execution_times:
            logger.error(f"No successful executions for {name}")
            return BenchmarkResult(name, 0.0, 0.0, 0.0, 0.0, errors)
        
        avg_execution_time = sum(execution_times) / len(execution_times)
        avg_memory_usage = sum(memory_usages) / len(memory_usages) if memory_usages else 0.0
        success_rate = (iterations - errors) / iterations
        ops_per_second = 1.0 / avg_execution_time if avg_execution_time > 0 else 0.0
        
        result = BenchmarkResult(
            name=name,
            execution_time=avg_execution_time,
            memory_usage=avg_memory_usage,
            operations_per_second=ops_per_second,
            success_rate=success_rate,
            error_count=errors
        )
        
        self.results.append(result)
        return result
    
    def run_scalability_test(self, func: Callable, name: str, sizes: List[int]) -> List[BenchmarkResult]:
        """Test function scalability with different input sizes."""
        results = []
        
        for size in sizes:
            logger.info(f"Testing {name} with size {size}")
            
            # Create test data of appropriate size
            test_data = [f"Hello World {i}" for i in range(size)]
            
            result = self.benchmark_function(
                func, f"{name} (size={size})", 10, test_data
            )
            results.append(result)
        
        return results
    
    def compare_implementations(self) -> None:
        """Compare different implementation performances."""
        logger.info("Comparing implementation performances...")
        
        # Test original script
        if Path("hello_world.py").exists():
            original_result = self.run_script_benchmark("hello_world.py")
            self.results.append(original_result)
            self.baseline_results["original"] = original_result
        
        # Test optimized script
        if Path("hello_world_optimized.py").exists():
            optimized_result = self.run_script_benchmark("hello_world_optimized.py")
            self.results.append(optimized_result)
        
        # Test async version
        if Path("hello_world_async.py").exists():
            async_result = self.run_script_benchmark("hello_world_async.py", ["--count", "10"])
            self.results.append(async_result)
    
    def generate_report(self) -> str:
        """Generate a comprehensive performance report."""
        report_lines = [
            "# Performance Test Report",
            "",
            f"Total tests run: {len(self.results)}",
            f"Report generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Test Results",
            "",
        ]
        
        # Sort results by execution time
        sorted_results = sorted(self.results, key=lambda x: x.execution_time)
        
        for result in sorted_results:
            report_lines.extend([
                f"### {result.name}",
                f"- Execution time: {result.execution_time:.6f} seconds",
                f"- Memory usage: {result.memory_usage:.2f} MB",
                f"- Operations per second: {result.operations_per_second:.2f}",
                f"- Success rate: {result.success_rate:.2%}",
                f"- Error count: {result.error_count}",
                "",
            ])
        
        # Performance comparison
        if "original" in self.baseline_results and len(self.results) > 1:
            baseline = self.baseline_results["original"]
            report_lines.extend([
                "## Performance Improvements",
                "",
            ])
            
            for result in self.results:
                if result.name != baseline.name:
                    speedup = baseline.execution_time / result.execution_time if result.execution_time > 0 else 0
                    memory_change = result.memory_usage - baseline.memory_usage
                    
                    report_lines.extend([
                        f"### {result.name} vs Original",
                        f"- Speedup: {speedup:.2f}x",
                        f"- Memory change: {memory_change:+.2f} MB",
                        "",
                    ])
        
        # Recommendations
        report_lines.extend([
            "## Recommendations",
            "",
            "1. **Fastest implementation**: " + sorted_results[0].name,
            "2. **Most memory efficient**: " + min(self.results, key=lambda x: x.memory_usage).name,
            "3. **Most reliable**: " + max(self.results, key=lambda x: x.success_rate).name,
            "",
        ])
        
        return "\n".join(report_lines)
    
    def save_report(self, filename: str = "performance_report.md") -> None:
        """Save the performance report to a file."""
        report = self.generate_report()
        
        with open(filename, "w") as f:
            f.write(report)
        
        logger.info(f"Performance report saved to {filename}")


def main():
    """Main function to run performance tests."""
    tester = PerformanceTester()
    
    # Run comparison tests
    tester.compare_implementations()
    
    # Test simple function implementations
    def simple_hello():
        print("Hello World")
    
    def complex_hello():
        message = "Hello World"
        for i in range(100):
            if i % 10 == 0:
                temp = message + f" {i}"
        print(message)
    
    tester.benchmark_function(simple_hello, "Simple Hello Function", 1000)
    tester.benchmark_function(complex_hello, "Complex Hello Function", 1000)
    
    # Generate and save report
    tester.save_report()
    
    # Print summary
    print("\n" + "="*50)
    print("PERFORMANCE TEST SUMMARY")
    print("="*50)
    
    for result in sorted(tester.results, key=lambda x: x.execution_time):
        print(f"{result.name:30} | {result.execution_time:.6f}s | {result.success_rate:.1%}")
    
    print("="*50)
    print(f"Detailed report saved to performance_report.md")


if __name__ == "__main__":
    main()