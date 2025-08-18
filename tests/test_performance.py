"""Performance tests for API optimizations."""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from app.services.swe_optimized import swe_optimized_service
from app.services.cache import cache_service
from app.middleware.performance import batch_processor, get_performance_stats


class TestPerformance:
    """Test performance optimizations."""
    
    def test_swiss_ephemeris_caching(self):
        """Test SWE service caching performance."""
        # Clear caches first
        swe_optimized_service.clear_caches()
        
        # Test data
        dt = datetime(2025, 8, 17, 12, 0, 0)
        planets = ["Sun", "Moon", "Mars"]
        
        # First calculation (cache miss)
        start_time = time.time()
        result1 = swe_optimized_service.calculate_planets(dt, planets)
        first_duration = time.time() - start_time
        
        # Second calculation (cache hit)
        start_time = time.time()
        result2 = swe_optimized_service.calculate_planets(dt, planets)
        second_duration = time.time() - start_time
        
        # Verify results are identical
        assert result1 == result2
        
        # Verify cache hit is faster
        assert second_duration < first_duration * 0.5  # At least 50% faster
        
        # Check cache statistics
        cache_info = swe_optimized_service._get_rasi_cached.cache_info()
        assert cache_info.hits > 0
    
    @pytest.mark.asyncio
    async def test_async_ephemeris_calculation(self):
        """Test async ephemeris calculation performance."""
        dt = datetime(2025, 8, 17, 12, 0, 0)
        planets = ["Sun", "Moon", "Mercury", "Venus", "Mars"]
        
        # Test async calculation
        start_time = time.time()
        result = await swe_optimized_service.calculate_planets_async(dt, planets)
        async_duration = time.time() - start_time
        
        # Test sync calculation for comparison
        start_time = time.time()
        sync_result = swe_optimized_service.calculate_planets(dt, planets)
        sync_duration = time.time() - start_time
        
        # Verify results are identical
        assert result == sync_result
        
        # Async should be similar or faster
        assert async_duration <= sync_duration * 1.2  # Allow 20% overhead
    
    @pytest.mark.asyncio
    async def test_batch_processing(self):
        """Test batch processing performance."""
        # Create test data
        dates = [
            datetime(2025, 8, 17, 12, 0, 0),
            datetime(2025, 8, 18, 12, 0, 0),
            datetime(2025, 8, 19, 12, 0, 0),
        ]
        
        async def calculate_for_date(dt):
            return await swe_optimized_service.calculate_planets_async(dt, ["Sun", "Moon"])
        
        # Process in batch
        start_time = time.time()
        batch_results = await batch_processor.process_batch(dates, calculate_for_date)
        batch_duration = time.time() - start_time
        
        # Process individually for comparison
        start_time = time.time()
        individual_results = []
        for dt in dates:
            result = await calculate_for_date(dt)
            individual_results.append(result)
        individual_duration = time.time() - start_time
        
        # Verify results are identical
        assert len(batch_results) == len(individual_results)
        for i in range(len(batch_results)):
            assert batch_results[i] == individual_results[i]
        
        # Batch should be faster due to concurrency
        assert batch_duration < individual_duration * 0.8  # At least 20% faster
    
    def test_cache_service_performance(self):
        """Test cache service performance."""
        # Test cache operations
        test_key = "test_performance_key"
        test_value = {"data": "test", "timestamp": time.time()}
        
        # Test set operation
        start_time = time.time()
        success = asyncio.run(cache_service.set(test_key, test_value, 60))
        set_duration = time.time() - start_time
        
        assert success or not cache_service.enabled
        assert set_duration < 0.1  # Should be fast
        
        # Test get operation
        start_time = time.time()
        retrieved_value = asyncio.run(cache_service.get(test_key))
        get_duration = time.time() - start_time
        
        if cache_service.enabled:
            assert retrieved_value == test_value
        assert get_duration < 0.1  # Should be fast
    
    def test_performance_stats(self):
        """Test performance statistics."""
        stats = get_performance_stats()
        
        # Verify required fields
        required_fields = [
            "concurrent_requests",
            "max_concurrent_requests", 
            "batch_size_limit",
            "slow_request_threshold"
        ]
        
        for field in required_fields:
            assert field in stats
            assert stats[field] is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        dt = datetime(2025, 8, 17, 12, 0, 0)
        planets = ["Sun", "Moon"]
        
        # Create multiple concurrent requests
        async def single_request():
            return await swe_optimized_service.calculate_planets_async(dt, planets)
        
        # Test with 5 concurrent requests
        start_time = time.time()
        tasks = [single_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        concurrent_duration = time.time() - start_time
        
        # Verify all requests completed successfully
        assert len(results) == 5
        for result in results:
            assert "Sun" in result
            assert "Moon" in result
        
        # Verify reasonable performance
        assert concurrent_duration < 2.0  # Should complete within 2 seconds
    
    def test_memory_usage(self):
        """Test memory usage with caching."""
        # Clear caches first
        swe_optimized_service.clear_caches()
        
        # Perform multiple calculations to fill cache
        dt = datetime(2025, 8, 17, 12, 0, 0)
        
        for i in range(100):
            # Use different longitudes to fill cache
            test_lon = i * 3.6  # 360 degrees / 100
            swe_optimized_service._get_rasi(test_lon)
            swe_optimized_service._get_nakshatra(test_lon)
            swe_optimized_service._get_pada(test_lon)
        
        # Check cache statistics
        rasi_cache_info = swe_optimized_service._get_rasi_cached.cache_info()
        nakshatra_cache_info = swe_optimized_service._get_nakshatra_cached.cache_info()
        pada_cache_info = swe_optimized_service._get_pada_cached.cache_info()
        
        # Verify caches are being used
        assert rasi_cache_info.hits > 0
        assert nakshatra_cache_info.hits > 0
        assert pada_cache_info.hits > 0
        
        # Verify cache sizes are reasonable
        assert rasi_cache_info.currsize <= 1000
        assert nakshatra_cache_info.currsize <= 1000
        assert pada_cache_info.currsize <= 1000
