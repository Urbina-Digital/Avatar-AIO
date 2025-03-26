"""
Hardware Capability Detection Module for AI Avatar Platform

This module detects and analyzes the hardware capabilities of the system
to determine if it can run the AI Avatar Platform locally.
"""

import os
import logging
import platform
import psutil
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
import shutil
import GPUtil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('hardware_detector')

class HardwareDetector:
    """Detects and analyzes hardware capabilities."""
    
    def __init__(self):
        """Initialize the HardwareDetector."""
        # Define minimum requirements
        self.min_requirements = {
            "cpu_cores": 4,
            "ram_gb": 8,
            "disk_space_gb": 10,
            "gpu_vram_gb": 4
        }
        
        # Define recommended requirements
        self.recommended_requirements = {
            "cpu_cores": 8,
            "ram_gb": 16,
            "disk_space_gb": 20,
            "gpu_vram_gb": 8
        }
        
        logger.info("HardwareDetector initialized")
    
    def detect_hardware(self) -> Dict:
        """
        Detect hardware capabilities of the system.
        
        Returns:
            Dictionary with hardware specifications
        """
        logger.info("Detecting hardware capabilities")
        
        # Get CPU information
        cpu_info = self._get_cpu_info()
        
        # Get RAM information
        ram_info = self._get_ram_info()
        
        # Get disk information
        disk_info = self._get_disk_info()
        
        # Get GPU information
        gpu_info = self._get_gpu_info()
        
        # Combine all information
        hardware_info = {
            "cpu": cpu_info,
            "ram": ram_info,
            "disk": disk_info,
            "gpu": gpu_info,
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
        }
        
        return hardware_info
    
    def _get_cpu_info(self) -> Dict:
        """
        Get CPU information.
        
        Returns:
            Dictionary with CPU specifications
        """
        try:
            # Get physical and logical CPU cores
            physical_cores = psutil.cpu_count(logical=False)
            logical_cores = psutil.cpu_count(logical=True)
            
            # Get CPU frequency
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                current_freq = cpu_freq.current
                max_freq = cpu_freq.max
            else:
                current_freq = None
                max_freq = None
            
            # Get CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            return {
                "physical_cores": physical_cores,
                "logical_cores": logical_cores,
                "current_frequency_mhz": current_freq,
                "max_frequency_mhz": max_freq,
                "usage_percent": cpu_usage
            }
        
        except Exception as e:
            logger.error(f"Error getting CPU information: {e}")
            return {
                "error": str(e)
            }
    
    def _get_ram_info(self) -> Dict:
        """
        Get RAM information.
        
        Returns:
            Dictionary with RAM specifications
        """
        try:
            # Get memory information
            memory = psutil.virtual_memory()
            
            return {
                "total_gb": round(memory.total / (1024 ** 3), 2),
                "available_gb": round(memory.available / (1024 ** 3), 2),
                "used_gb": round(memory.used / (1024 ** 3), 2),
                "usage_percent": memory.percent
            }
        
        except Exception as e:
            logger.error(f"Error getting RAM information: {e}")
            return {
                "error": str(e)
            }
    
    def _get_disk_info(self) -> Dict:
        """
        Get disk information.
        
        Returns:
            Dictionary with disk specifications
        """
        try:
            # Get disk information for the current directory
            disk_usage = shutil.disk_usage(os.getcwd())
            
            return {
                "total_gb": round(disk_usage.total / (1024 ** 3), 2),
                "used_gb": round(disk_usage.used / (1024 ** 3), 2),
                "free_gb": round(disk_usage.free / (1024 ** 3), 2),
                "usage_percent": round((disk_usage.used / disk_usage.total) * 100, 2)
            }
        
        except Exception as e:
            logger.error(f"Error getting disk information: {e}")
            return {
                "error": str(e)
            }
    
    def _get_gpu_info(self) -> Dict:
        """
        Get GPU information.
        
        Returns:
            Dictionary with GPU specifications
        """
        try:
            # Try to get GPU information using GPUtil
            gpus = GPUtil.getGPUs()
            
            if gpus:
                gpu_info_list = []
                
                for gpu in gpus:
                    gpu_info = {
                        "name": gpu.name,
                        "driver": gpu.driver,
                        "memory_total_gb": round(gpu.memoryTotal / 1024, 2),
                        "memory_used_gb": round(gpu.memoryUsed / 1024, 2),
                        "memory_free_gb": round(gpu.memoryFree / 1024, 2),
                        "usage_percent": round(gpu.memoryUtil * 100, 2),
                        "temperature": gpu.temperature
                    }
                    
                    gpu_info_list.append(gpu_info)
                
                return {
                    "count": len(gpus),
                    "gpus": gpu_info_list,
                    "has_gpu": True
                }
            else:
                # No GPUs found
                return {
                    "count": 0,
                    "gpus": [],
                    "has_gpu": False
                }
        
        except Exception as e:
            logger.error(f"Error getting GPU information: {e}")
            return {
                "error": str(e),
                "has_gpu": False
            }
    
    def check_requirements(self, hardware_info: Dict) -> Dict:
        """
        Check if the hardware meets the requirements.
        
        Args:
            hardware_info: Dictionary with hardware specifications
            
        Returns:
            Dictionary with requirement check results
        """
        logger.info("Checking hardware requirements")
        
        # Check CPU requirements
        cpu_cores = hardware_info.get("cpu", {}).get("logical_cores", 0)
        cpu_min_met = cpu_cores >= self.min_requirements["cpu_cores"]
        cpu_recommended_met = cpu_cores >= self.recommended_requirements["cpu_cores"]
        
        # Check RAM requirements
        ram_gb = hardware_info.get("ram", {}).get("total_gb", 0)
        ram_min_met = ram_gb >= self.min_requirements["ram_gb"]
        ram_recommended_met = ram_gb >= self.recommended_requirements["ram_gb"]
        
        # Check disk requirements
        disk_space_gb = hardware_info.get("disk", {}).get("free_gb", 0)
        disk_min_met = disk_space_gb >= self.min_requirements["disk_space_gb"]
        disk_recommended_met = disk_space_gb >= self.recommended_requirements["disk_space_gb"]
        
        # Check GPU requirements
        gpu_info = hardware_info.get("gpu", {})
        has_gpu = gpu_info.get("has_gpu", False)
        
        if has_gpu and "error" not in gpu_info:
            # Get the GPU with the most VRAM
            gpus = gpu_info.get("gpus", [])
            max_vram = 0
            
            for gpu in gpus:
                vram = gpu.get("memory_total_gb", 0)
                if vram > max_vram:
                    max_vram = vram
            
            gpu_vram_gb = max_vram
        else:
            gpu_vram_gb = 0
        
        gpu_min_met = gpu_vram_gb >= self.min_requirements["gpu_vram_gb"]
        gpu_recommended_met = gpu_vram_gb >= self.recommended_requirements["gpu_vram_gb"]
        
        # Determine overall requirements met
        min_requirements_met = cpu_min_met and ram_min_met and disk_min_met
        recommended_requirements_met = cpu_recommended_met and ram_recommended_met and disk_recommended_met and gpu_recommended_met
        
        # Create requirement check results
        requirement_check = {
            "cpu": {
                "cores": cpu_cores,
                "min_required": self.min_requirements["cpu_cores"],
                "recommended": self.recommended_requirements["cpu_cores"],
                "min_met": cpu_min_met,
                "recommended_met": cpu_recommended_met
            },
            "ram": {
                "gb": ram_gb,
                "min_required": self.min_requirements["ram_gb"],
                "recommended": self.recommended_requirements["ram_gb"],
                "min_met": ram_min_met,
                "recommended_met": ram_recommended_met
            },
            "disk": {
                "free_gb": disk_space_gb,
                "min_required": self.min_requirements["disk_space_gb"],
                "recommended": self.recommended_requirements["disk_space_gb"],
                "min_met": disk_min_met,
                "recommended_met": disk_recommended_met
            },
            "gpu": {
                "has_gpu": has_gpu,
                "vram_gb": gpu_vram_gb,
                "min_required": self.min_requirements["gpu_vram_gb"],
                "recommended": self.recommended_requirements["gpu_vram_gb"],
                "min_met": gpu_min_met,
                "recommended_met": gpu_recommended_met
            },
            "overall": {
                "min_requirements_met": min_requirements_met,
                "recommended_requirements_met": recommended_requirements_met,
                "can_run_locally": min_requirements_met,
                "should_use_cloud": not recommended_requirements_met
            }
        }
        
        return requirement_check
    
    def get_hardware_summary(self) -> Dict:
        """
        Get a summary of hardware capabilities and requirement checks.
        
        Returns:
            Dictionary with hardware summary
        """
        logger.info("Getting hardware summary")
        
        # Detect hardware
        hardware_info = self.detect_hardware()
        
        # Check requirements
        requirement_check = self.check_requirements(hardware_info)
        
        # Create hardware summary
        hardware_summary = {
            "hardware_info": hardware_info,
            "requirement_check": requirement_check,
            "can_run_locally": requirement_check["overall"]["can_run_locally"],
            "should_use_cloud": requirement_check["overall"]["should_use_cloud"]
        }
        
        return hardware_summary


# Example usage
if __name__ == "__main__":
    detector = HardwareDetector()
    summary = detector.get_hardware_summary()
    print(json.dumps(summary, indent=2))
