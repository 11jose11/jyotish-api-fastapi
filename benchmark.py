#!/usr/bin/env python3
"""Benchmark script for API performance testing."""

import asyncio
import time
import statistics
from datetime import datetime, timedelta
from typing import List, Dict

from app.services.swe import swe_service
from app.services.swe_optimized import swe_optimized_service
from app.services.cache import cache_service


class BenchmarkRunner:
    """Benchmark runner for performance testing."""
    
    def __init__(self):
        self.results = {}
    
    async def benchmark_ephemeris_calculation(self, iterations: int = 100):
        """Benchmark ephemeris calculations."""
        print(f"\n🔄 Benchmarking Ephemeris Calculations ({iterations} iterations)")
        
        # Test data
        dt = datetime(2025, 8, 17, 12, 0, 0)
        planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        
        # Clear caches
        swe_optimized_service.clear_caches()
        
        # Test original service
        print("📊 Testing Original Service...")
        original_times = []
        for i in range(iterations):
            start_time = time.time()
            result = swe_service.calculate_planets(dt, planets)
            duration = time.time() - start_time
            original_times.append(duration)
        
        # Test optimized service (first run - cache miss)
        print("📊 Testing Optimized Service (Cache Miss)...")
        optimized_times_miss = []
        for i in range(iterations):
            start_time = time.time()
            result = swe_optimized_service.calculate_planets(dt, planets)
            duration = time.time() - start_time
            optimized_times_miss.append(duration)
        
        # Test optimized service (second run - cache hit)
        print("📊 Testing Optimized Service (Cache Hit)...")
        optimized_times_hit = []
        for i in range(iterations):
            start_time = time.time()
            result = swe_optimized_service.calculate_planets(dt, planets)
            duration = time.time() - start_time
            optimized_times_hit.append(duration)
        
        # Test async optimized service
        print("📊 Testing Async Optimized Service...")
        async_times = []
        for i in range(iterations):
            start_time = time.time()
            result = await swe_optimized_service.calculate_planets_async(dt, planets)
            duration = time.time() - start_time
            async_times.append(duration)
        
        # Calculate statistics
        stats = {
            "original": {
                "mean": statistics.mean(original_times),
                "median": statistics.median(original_times),
                "min": min(original_times),
                "max": max(original_times),
                "std": statistics.stdev(original_times) if len(original_times) > 1 else 0
            },
            "optimized_miss": {
                "mean": statistics.mean(optimized_times_miss),
                "median": statistics.median(optimized_times_miss),
                "min": min(optimized_times_miss),
                "max": max(optimized_times_miss),
                "std": statistics.stdev(optimized_times_miss) if len(optimized_times_miss) > 1 else 0
            },
            "optimized_hit": {
                "mean": statistics.mean(optimized_times_hit),
                "median": statistics.median(optimized_times_hit),
                "min": min(optimized_times_hit),
                "max": max(optimized_times_hit),
                "std": statistics.stdev(optimized_times_hit) if len(optimized_times_hit) > 1 else 0
            },
            "async": {
                "mean": statistics.mean(async_times),
                "median": statistics.median(async_times),
                "min": min(async_times),
                "max": max(async_times),
                "std": statistics.stdev(async_times) if len(async_times) > 1 else 0
            }
        }
        
        # Calculate improvements
        original_mean = stats["original"]["mean"]
        improvements = {
            "optimized_miss": (original_mean - stats["optimized_miss"]["mean"]) / original_mean * 100,
            "optimized_hit": (original_mean - stats["optimized_hit"]["mean"]) / original_mean * 100,
            "async": (original_mean - stats["async"]["mean"]) / original_mean * 100
        }
        
        # Print results
        print("\n📈 Results:")
        print(f"{'Service':<20} {'Mean (ms)':<12} {'Median (ms)':<12} {'Improvement':<12}")
        print("-" * 60)
        print(f"{'Original':<20} {stats['original']['mean']*1000:<12.2f} {stats['original']['median']*1000:<12.2f} {'-':<12}")
        print(f"{'Optimized (Miss)':<20} {stats['optimized_miss']['mean']*1000:<12.2f} {stats['optimized_miss']['median']*1000:<12.2f} {improvements['optimized_miss']:<12.1f}%")
        print(f"{'Optimized (Hit)':<20} {stats['optimized_hit']['mean']*1000:<12.2f} {stats['optimized_hit']['median']*1000:<12.2f} {improvements['optimized_hit']:<12.1f}%")
        print(f"{'Async':<20} {stats['async']['mean']*1000:<12.2f} {stats['async']['median']*1000:<12.2f} {improvements['async']:<12.1f}%")
        
        self.results["ephemeris"] = {
            "stats": stats,
            "improvements": improvements
        }
    
    async def benchmark_batch_processing(self, batch_sizes: List[int] = [5, 10, 20, 50]):
        """Benchmark batch processing."""
        print(f"\n🔄 Benchmarking Batch Processing")
        
        # Test data
        base_dt = datetime(2025, 8, 17, 12, 0, 0)
        planets = ["Sun", "Moon"]
        
        batch_results = {}
        
        for batch_size in batch_sizes:
            print(f"📊 Testing batch size: {batch_size}")
            
            # Create batch of dates
            dates = [base_dt + timedelta(hours=i) for i in range(batch_size)]
            
            # Test individual processing
            individual_times = []
            for i in range(3):  # 3 iterations for averaging
                start_time = time.time()
                results = []
                for dt in dates:
                    result = await swe_optimized_service.calculate_planets_async(dt, planets)
                    results.append(result)
                duration = time.time() - start_time
                individual_times.append(duration)
            
            # Test batch processing
            batch_times = []
            for i in range(3):  # 3 iterations for averaging
                start_time = time.time()
                results = await swe_optimized_service.calculate_planets_async(dates[0], planets)
                duration = time.time() - start_time
                batch_times.append(duration)
            
            individual_mean = statistics.mean(individual_times)
            batch_mean = statistics.mean(batch_times)
            improvement = (individual_mean - batch_mean) / individual_mean * 100
            
            batch_results[batch_size] = {
                "individual_mean": individual_mean,
                "batch_mean": batch_mean,
                "improvement": improvement
            }
        
        # Print results
        print("\n📈 Batch Processing Results:")
        print(f"{'Batch Size':<12} {'Individual (s)':<15} {'Batch (s)':<12} {'Improvement':<12}")
        print("-" * 55)
        for batch_size, result in batch_results.items():
            print(f"{batch_size:<12} {result['individual_mean']:<15.3f} {result['batch_mean']:<12.3f} {result['improvement']:<12.1f}%")
        
        self.results["batch"] = batch_results
    
    async def benchmark_cache_performance(self, iterations: int = 1000):
        """Benchmark cache performance."""
        print(f"\n🔄 Benchmarking Cache Performance ({iterations} iterations)")
        
        # Test data
        test_key = "benchmark_test_key"
        test_value = {
            "planets": {"Sun": {"lon": 120.5}, "Moon": {"lon": 45.2}},
            "timestamp": time.time()
        }
        
        # Test cache operations
        set_times = []
        get_times = []
        
        for i in range(iterations):
            # Test set
            start_time = time.time()
            success = await cache_service.set(f"{test_key}_{i}", test_value, 60)
            set_duration = time.time() - start_time
            set_times.append(set_duration)
            
            # Test get
            start_time = time.time()
            retrieved = await cache_service.get(f"{test_key}_{i}")
            get_duration = time.time() - start_time
            get_times.append(get_duration)
        
        # Calculate statistics
        set_stats = {
            "mean": statistics.mean(set_times),
            "median": statistics.median(set_times),
            "min": min(set_times),
            "max": max(set_times)
        }
        
        get_stats = {
            "mean": statistics.mean(get_times),
            "median": statistics.median(get_times),
            "min": min(get_times),
            "max": max(get_times)
        }
        
        # Print results
        print("\n📈 Cache Performance Results:")
        print(f"{'Operation':<12} {'Mean (ms)':<12} {'Median (ms)':<12} {'Min (ms)':<12} {'Max (ms)':<12}")
        print("-" * 65)
        print(f"{'Set':<12} {set_stats['mean']*1000:<12.3f} {set_stats['median']*1000:<12.3f} {set_stats['min']*1000:<12.3f} {set_stats['max']*1000:<12.3f}")
        print(f"{'Get':<12} {get_stats['mean']*1000:<12.3f} {get_stats['median']*1000:<12.3f} {get_stats['min']*1000:<12.3f} {get_stats['max']*1000:<12.3f}")
        
        self.results["cache"] = {
            "set": set_stats,
            "get": get_stats
        }
    
    def print_summary(self):
        """Print benchmark summary."""
        print("\n" + "="*60)
        print("🎯 BENCHMARK SUMMARY")
        print("="*60)
        
        if "ephemeris" in self.results:
            improvements = self.results["ephemeris"]["improvements"]
            print(f"\n🚀 Ephemeris Calculation Improvements:")
            print(f"   • Optimized (Cache Miss): {improvements['optimized_miss']:.1f}% faster")
            print(f"   • Optimized (Cache Hit):  {improvements['optimized_hit']:.1f}% faster")
            print(f"   • Async:                  {improvements['async']:.1f}% faster")
        
        if "batch" in self.results:
            print(f"\n📦 Batch Processing:")
            for batch_size, result in self.results["batch"].items():
                print(f"   • Batch size {batch_size}: {result['improvement']:.1f}% improvement")
        
        if "cache" in self.results:
            cache_stats = self.results["cache"]
            print(f"\n💾 Cache Performance:")
            print(f"   • Set operations: {cache_stats['set']['mean']*1000:.3f}ms average")
            print(f"   • Get operations: {cache_stats['get']['mean']*1000:.3f}ms average")
        
        print("\n✅ Benchmark completed successfully!")


async def main():
    """Main benchmark function."""
    print("🚀 Starting API Performance Benchmark")
    print("="*50)
    
    runner = BenchmarkRunner()
    
    # Run benchmarks
    await runner.benchmark_ephemeris_calculation(iterations=50)
    await runner.benchmark_batch_processing(batch_sizes=[5, 10, 20])
    await runner.benchmark_cache_performance(iterations=100)
    
    # Print summary
    runner.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
