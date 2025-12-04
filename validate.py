#!/usr/bin/env python3
"""
Validation script for CryptoBot Dashboard
This script checks if all requirements are met before deployment
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_status(check, status, message=""):
    """Print a status line"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {check}: {'PASS' if status else 'FAIL'} {message}")
    return status

def check_python_version():
    """Check if Python version is 3.9 or higher"""
    version = sys.version_info
    is_valid = version >= (3, 9)
    print_status(
        "Python version",
        is_valid,
        f"(found {version.major}.{version.minor}.{version.micro})"
    )
    return is_valid

def check_file_exists(filepath, description):
    """Check if a file exists"""
    exists = Path(filepath).exists()
    print_status(description, exists, f"({filepath})")
    return exists

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    exists = Path(dirpath).is_dir()
    print_status(description, exists, f"({dirpath})")
    return exists

def check_dependencies():
    """Check if key dependencies can be imported"""
    print_header("Checking Dependencies")
    
    required_packages = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('streamlit', 'streamlit'),
        ('plotly', 'plotly'),
        ('requests', 'requests'),
        ('ccxt', 'ccxt'),
        ('dotenv', 'python-dotenv'),
        ('yaml', 'PyYAML')
    ]
    
    all_ok = True
    for package, package_name in required_packages:
        try:
            __import__(package)
            print_status(f"{package_name}", True)
        except ImportError:
            print_status(f"{package_name}", False, "NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_structure():
    """Check if project structure is correct"""
    print_header("Checking Project Structure")
    
    all_ok = True
    
    # Check required directories
    required_dirs = [
        'src',
        'src/dashboard',
        'src/api',
        'src/utils',
        'config',
        '.streamlit',
        '.github/workflows'
    ]
    
    for dir_path in required_dirs:
        all_ok &= check_directory_exists(dir_path, f"Directory: {dir_path}")
    
    return all_ok

def check_files():
    """Check if required files exist"""
    print_header("Checking Required Files")
    
    all_ok = True
    
    required_files = [
        'requirements.txt',
        'README.md',
        'DEPLOYMENT.md',
        'QUICK_DEPLOY.md',
        'CHANGELOG.md',
        '.env.example',
        '.gitignore',
        'Dockerfile',
        'docker-compose.yml',
        'Procfile',
        'runtime.txt',
        'start.sh',
        'start.bat',
        '.streamlit/config.toml',
        '.streamlit/secrets.toml.example',
        '.github/workflows/ci.yml',
        'src/dashboard/flynt_style_dashboard.py',
        'config/app_config.yaml',
        'config/exchange_config.yaml'
    ]
    
    for file_path in required_files:
        all_ok &= check_file_exists(file_path, f"File: {file_path}")
    
    return all_ok

def check_env_configuration():
    """Check environment configuration"""
    print_header("Checking Environment Configuration")
    
    has_env = Path('.env').exists()
    has_example = Path('.env.example').exists()
    
    if not has_env:
        print_status(".env file", False, "Create from .env.example")
        if has_example:
            print("  💡 Run: cp .env.example .env")
        return False
    else:
        print_status(".env file", True)
        
        # Check if .env has been configured
        with open('.env', 'r') as f:
            content = f.read()
            if 'your_binance_api_key' in content:
                print_status("API keys configured", False, "Update .env with real keys")
                return False
            else:
                print_status("API keys configured", True)
                return True

def check_git_status():
    """Check git configuration"""
    print_header("Checking Git Configuration")
    
    all_ok = True
    
    # Check if .git exists
    all_ok &= check_directory_exists('.git', "Git repository")
    
    # Check if there are uncommitted changes
    if Path('.git').exists():
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            has_changes = bool(result.stdout.strip())
            print_status(
                "Uncommitted changes",
                not has_changes,
                "Commit changes before deploying" if has_changes else ""
            )
        except:
            print_status("Git status check", False, "Could not check git status")
            all_ok = False
    
    return all_ok

def check_docker():
    """Check if Docker is available (optional)"""
    print_header("Checking Docker (Optional)")
    
    try:
        import subprocess
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        print_status("Docker", True, result.stdout.strip())
        return True
    except:
        print_status("Docker", False, "Not installed (optional)")
        return False

def main():
    """Run all validation checks"""
    print_header("🚀 CryptoBot Dashboard Validation")
    print("This script validates your setup before deployment")
    
    results = []
    
    # Run checks
    results.append(("Python Version", check_python_version()))
    results.append(("Project Structure", check_structure()))
    results.append(("Required Files", check_files()))
    
    # Check dependencies (optional if not in venv)
    print("\n💡 If dependencies check fails, run: pip install -r requirements.txt")
    results.append(("Dependencies", check_dependencies()))
    
    results.append(("Environment Config", check_env_configuration()))
    results.append(("Git Status", check_git_status()))
    
    # Optional checks
    check_docker()
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for _, status in results if status)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if passed == total:
        print("\n✨ All checks passed! Your setup is ready for deployment.")
        print("\n📚 Next steps:")
        print("   1. Review DEPLOYMENT.md for deployment options")
        print("   2. Choose your deployment platform")
        print("   3. Follow the platform-specific instructions")
        print("   4. Test with testnet before going live")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
        print("\n📚 Resources:")
        print("   - README.md for setup instructions")
        print("   - DEPLOYMENT.md for deployment guide")
        print("   - QUICK_DEPLOY.md for quick reference")
        return 1

if __name__ == "__main__":
    sys.exit(main())
