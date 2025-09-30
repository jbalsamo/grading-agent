#!/usr/bin/env python3
"""
Configuration validation script for the Master Agent System.
Run this script to validate your configuration before starting the system.
"""
import os
import sys
from dotenv import load_dotenv
from utils import ConfigValidator, get_system_info

def main():
    """Main validation function."""
    print("🔍 Master Agent System Configuration Validator")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Validate Azure OpenAI configuration
    print("\n📋 Validating Azure OpenAI Configuration...")
    azure_config = ConfigValidator.validate_azure_config()
    
    if azure_config["valid"]:
        print("✅ Azure OpenAI configuration is valid!")
        print("   Configuration values:")
        for key, value in azure_config["config_values"].items():
            print(f"     {key}: {value}")
        
        if azure_config["warnings"]:
            print("   ⚠️  Warnings:")
            for warning in azure_config["warnings"]:
                print(f"     - {warning}")
    else:
        print("❌ Azure OpenAI configuration is invalid!")
        print("   Missing required variables:")
        for var in azure_config["missing_vars"]:
            print(f"     - {var}")
        print("\n   Please check your .env file and ensure all required variables are set.")
    
    # Validate data directory
    print("\n💾 Validating Data Directory...")
    data_config = ConfigValidator.validate_data_directory()
    
    if data_config["valid"]:
        print("✅ Data directory is properly configured!")
        print(f"   Directory exists: {data_config['exists']}")
        print(f"   Writable: {data_config['writable']}")
        
        if data_config["files"]:
            print("   Existing data files:")
            for file_type, file_info in data_config["files"].items():
                if "error" in file_info:
                    print(f"     - {file_type}: Error - {file_info['error']}")
                else:
                    if file_type == "interactions":
                        print(f"     - {file_type}: {file_info['line_count']} interactions")
                    elif file_type == "context":
                        print(f"     - {file_type}: {len(file_info.get('keys', []))} context keys")
    else:
        print("❌ Data directory configuration issues!")
        for issue in data_config["issues"]:
            print(f"     - {issue}")
    
    # Check Python dependencies
    print("\n📦 Checking Python Dependencies...")
    required_packages = [
        ("langchain", "langchain"),
        ("langchain-openai", "langchain_openai"), 
        ("langgraph", "langgraph"),
        ("python-dotenv", "dotenv"),
        ("pydantic", "pydantic")
    ]
    
    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} - Not installed")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n   Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
    
    # System information
    print("\n🖥️  System Information...")
    sys_info = get_system_info()
    print(f"   Python Version: {sys_info['python_version'].split()[0]}")
    print(f"   Platform: {sys_info['platform']}")
    print(f"   Current Directory: {sys_info['current_directory']}")
    
    # Overall assessment
    print("\n" + "=" * 60)
    
    if azure_config["valid"] and data_config["valid"] and not missing_packages:
        print("🎉 Configuration validation PASSED!")
        print("   Your Master Agent System is ready to run.")
        print("   Execute: python main.py")
        return 0
    else:
        print("⚠️  Configuration validation FAILED!")
        print("   Please fix the issues above before running the system.")
        
        if not azure_config["valid"]:
            print("   - Fix Azure OpenAI configuration in .env file")
        if not data_config["valid"]:
            print("   - Fix data directory permissions")
        if missing_packages:
            print("   - Install missing Python packages")
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
