"""
Debug Configuration for Enhanced RepoToVideo

This module provides comprehensive logging configuration for debugging
all enhanced features including API integrations, code analysis, and video generation.
"""

import os
import logging
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_debug_logging(log_level: str = "DEBUG", log_file: str = None) -> logging.Logger:
    """
    Set up comprehensive debug logging for all components.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    if not log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"repotovideo_debug_{timestamp}.log"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )
    
    # Create main logger
    logger = logging.getLogger("RepoToVideo")
    logger.setLevel(logging.DEBUG)
    
    # Set up specific loggers for each component
    setup_component_loggers()
    
    logger.info(f"Debug logging initialized. Log file: {log_file}")
    return logger

def setup_component_loggers():
    """Set up specific loggers for each component."""
    
    # Code Analysis Logger
    code_analysis_logger = logging.getLogger("code_analysis")
    code_analysis_logger.setLevel(logging.DEBUG)
    
    # Error Simulation Logger
    error_sim_logger = logging.getLogger("error_simulation")
    error_sim_logger.setLevel(logging.DEBUG)
    
    # Narration Logger
    narration_logger = logging.getLogger("narration")
    narration_logger.setLevel(logging.DEBUG)
    
    # Video Generator Logger
    video_logger = logging.getLogger("video_generator")
    video_logger.setLevel(logging.DEBUG)
    
    # Parser Logger
    parser_logger = logging.getLogger("parsers")
    parser_logger.setLevel(logging.DEBUG)
    
    # API Loggers
    elevenlabs_logger = logging.getLogger("elevenlabs")
    elevenlabs_logger.setLevel(logging.DEBUG)
    
    e2b_logger = logging.getLogger("e2b")
    e2b_logger.setLevel(logging.DEBUG)
    
    # Manim Logger
    manim_logger = logging.getLogger("manim")
    manim_logger.setLevel(logging.DEBUG)

def verify_environment_setup() -> dict:
    """
    Verify that all environment variables and dependencies are properly configured.
    
    Returns:
        Dictionary with verification results
    """
    logger = logging.getLogger("RepoToVideo")
    results = {
        'api_keys': {},
        'dependencies': {},
        'permissions': {},
        'overall_status': 'PASS'
    }
    
    logger.info("=== Environment Verification Started ===")
    
    # Check API Keys
    logger.info("Checking API keys...")
    
    # ElevenLabs API Key
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    if elevenlabs_key:
        logger.info("✅ ELEVENLABS_API_KEY found")
        results['api_keys']['elevenlabs'] = {
            'status': 'FOUND',
            'key_preview': f"{elevenlabs_key[:8]}...{elevenlabs_key[-4:]}" if len(elevenlabs_key) > 12 else '***'
        }
    else:
        logger.warning("⚠️ ELEVENLABS_API_KEY not found - AI narration will use fallback")
        results['api_keys']['elevenlabs'] = {'status': 'NOT_FOUND'}
        results['overall_status'] = 'PARTIAL'
    
    # E2B API Key
    e2b_key = os.getenv('E2B_API_KEY')
    if e2b_key:
        logger.info("✅ E2B_API_KEY found")
        results['api_keys']['e2b'] = {
            'status': 'FOUND',
            'key_preview': f"{e2b_key[:8]}...{e2b_key[-4:]}" if len(e2b_key) > 12 else '***'
        }
    else:
        logger.warning("⚠️ E2B_API_KEY not found - Dynamic execution will use simulation")
        results['api_keys']['e2b'] = {'status': 'NOT_FOUND'}
        results['overall_status'] = 'PARTIAL'
    
    # Check Dependencies
    logger.info("Checking dependencies...")
    
    dependencies_to_check = [
        ('manim', 'Manim for animations'),
        ('e2b', 'E2B for sandbox execution'),
        ('elevenlabs', 'ElevenLabs for voice synthesis'),
        ('pycallgraph2', 'PyCallGraph2 for call graphs'),
        ('pipdeptree', 'Pipdeptree for dependency analysis'),
        ('networkx', 'NetworkX for graph visualization'),
        ('moviepy', 'MoviePy for video generation'),
        ('streamlit', 'Streamlit for web interface')
    ]
    
    for dep_name, description in dependencies_to_check:
        try:
            __import__(dep_name)
            logger.info(f"✅ {dep_name} - {description}")
            results['dependencies'][dep_name] = {'status': 'INSTALLED'}
        except ImportError:
            logger.error(f"❌ {dep_name} - {description} - NOT INSTALLED")
            results['dependencies'][dep_name] = {'status': 'NOT_INSTALLED'}
            results['overall_status'] = 'FAIL'
    
    # Check File Permissions
    logger.info("Checking file permissions...")
    
    # Check if we can write to current directory
    try:
        test_file = Path("test_write_permission.tmp")
        test_file.write_text("test")
        test_file.unlink()
        logger.info("✅ Write permission to current directory")
        results['permissions']['write'] = {'status': 'OK'}
    except Exception as e:
        logger.error(f"❌ Write permission error: {e}")
        results['permissions']['write'] = {'status': 'ERROR', 'message': str(e)}
        results['overall_status'] = 'FAIL'
    
    # Check if logs directory can be created
    try:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        logger.info("✅ Logs directory accessible")
        results['permissions']['logs'] = {'status': 'OK'}
    except Exception as e:
        logger.error(f"❌ Logs directory error: {e}")
        results['permissions']['logs'] = {'status': 'ERROR', 'message': str(e)}
        results['overall_status'] = 'FAIL'
    
    logger.info(f"=== Environment Verification Complete: {results['overall_status']} ===")
    return results

def test_api_connections() -> dict:
    """
    Test API connections to verify they're working correctly.
    
    Returns:
        Dictionary with test results
    """
    logger = logging.getLogger("RepoToVideo")
    results = {
        'elevenlabs': {'status': 'NOT_TESTED'},
        'e2b': {'status': 'NOT_TESTED'}
    }
    
    logger.info("=== API Connection Testing Started ===")
    
    # Test ElevenLabs API
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    if elevenlabs_key:
        logger.info("Testing ElevenLabs API connection...")
        try:
            from narration import AINarrator
            narrator = AINarrator(api_key=elevenlabs_key)
            voices = narrator.get_available_voices()
            if voices:
                logger.info(f"✅ ElevenLabs API working - {len(voices)} voices available")
                results['elevenlabs'] = {
                    'status': 'WORKING',
                    'voices_available': len(voices)
                }
            else:
                logger.warning("⚠️ ElevenLabs API responded but no voices found")
                results['elevenlabs'] = {'status': 'PARTIAL'}
        except Exception as e:
            logger.error(f"❌ ElevenLabs API test failed: {e}")
            results['elevenlabs'] = {'status': 'FAILED', 'error': str(e)}
    else:
        logger.info("Skipping ElevenLabs API test - no key provided")
    
    # Test E2B API
    e2b_key = os.getenv('E2B_API_KEY')
    if e2b_key:
        logger.info("Testing E2B API connection...")
        try:
            from e2b_code_interpreter import code_interpreter_sync
            session = code_interpreter_sync.Sandbox(api_key=e2b_key)
            logger.info("✅ E2B API connection successful")
            results['e2b'] = {'status': 'WORKING'}
        except Exception as e:
            logger.error(f"❌ E2B API test failed: {e}")
            results['e2b'] = {'status': 'FAILED', 'error': str(e)}
    else:
        logger.info("Skipping E2B API test - no key provided")
    
    logger.info("=== API Connection Testing Complete ===")
    return results

def run_comprehensive_test() -> dict:
    """
    Run a comprehensive test of all enhanced features.
    
    Returns:
        Dictionary with test results
    """
    logger = logging.getLogger("RepoToVideo")
    
    logger.info("=== Comprehensive Feature Test Started ===")
    
    # Setup logging
    setup_debug_logging()
    
    # Verify environment
    env_results = verify_environment_setup()
    
    # Test API connections
    api_results = test_api_connections()
    
    # Test core components
    component_results = test_core_components()
    
    # Compile results
    comprehensive_results = {
        'environment': env_results,
        'api_connections': api_results,
        'components': component_results,
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info("=== Comprehensive Feature Test Complete ===")
    return comprehensive_results

def test_core_components() -> dict:
    """
    Test core components of the enhanced system.
    
    Returns:
        Dictionary with component test results
    """
    logger = logging.getLogger("RepoToVideo")
    results = {}
    
    logger.info("Testing core components...")
    
    # Test Code Analysis
    try:
        from code_analysis import EnhancedCodeAnalyzer
        analyzer = EnhancedCodeAnalyzer(".")
        logger.info("✅ Code Analysis component initialized")
        results['code_analysis'] = {'status': 'OK'}
    except Exception as e:
        logger.error(f"❌ Code Analysis component failed: {e}")
        results['code_analysis'] = {'status': 'ERROR', 'error': str(e)}
    
    # Test Error Simulation
    try:
        from error_simulation import ErrorSimulator
        simulator = ErrorSimulator()
        logger.info("✅ Error Simulation component initialized")
        results['error_simulation'] = {'status': 'OK'}
    except Exception as e:
        logger.error(f"❌ Error Simulation component failed: {e}")
        results['error_simulation'] = {'status': 'ERROR', 'error': str(e)}
    
    # Test Narration
    try:
        from narration import AINarrator, NarrationManager
        narrator = AINarrator()
        manager = NarrationManager(narrator)
        logger.info("✅ Narration component initialized")
        results['narration'] = {'status': 'OK'}
    except Exception as e:
        logger.error(f"❌ Narration component failed: {e}")
        results['narration'] = {'status': 'ERROR', 'error': str(e)}
    
    # Test Video Generator
    try:
        from video_generator import VideoGenerator
        generator = VideoGenerator()
        logger.info("✅ Video Generator component initialized")
        results['video_generator'] = {'status': 'OK'}
    except Exception as e:
        logger.error(f"❌ Video Generator component failed: {e}")
        results['video_generator'] = {'status': 'ERROR', 'error': str(e)}
    
    # Test Parser Manager
    try:
        from parsers import ParserManager
        parser_manager = ParserManager()
        logger.info("✅ Parser Manager component initialized")
        results['parser_manager'] = {'status': 'OK'}
    except Exception as e:
        logger.error(f"❌ Parser Manager component failed: {e}")
        results['parser_manager'] = {'status': 'ERROR', 'error': str(e)}
    
    return results

if __name__ == "__main__":
    # Run comprehensive test when executed directly
    results = run_comprehensive_test()
    
    # Print summary
    print("\n" + "="*60)
    print("REPOTOVIDEO ENHANCED FEATURES TEST SUMMARY")
    print("="*60)
    
    print(f"\nEnvironment Status: {results['environment']['overall_status']}")
    print(f"Timestamp: {results['timestamp']}")
    
    print("\nAPI Keys:")
    for api, info in results['environment']['api_keys'].items():
        status = "✅" if info['status'] == 'FOUND' else "⚠️"
        print(f"  {status} {api}: {info['status']}")
    
    print("\nAPI Connections:")
    for api, info in results['api_connections'].items():
        status = "✅" if info['status'] == 'WORKING' else "❌"
        print(f"  {status} {api}: {info['status']}")
    
    print("\nComponents:")
    for component, info in results['components'].items():
        status = "✅" if info['status'] == 'OK' else "❌"
        print(f"  {status} {component}: {info['status']}")
    
    print("\n" + "="*60)
    print("Check the log file for detailed information.")
    print("="*60) 