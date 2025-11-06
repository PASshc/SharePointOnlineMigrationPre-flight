# Test Script for SPO Preflight Scanner
# This script creates a test directory structure to validate all checks

import os
import tempfile
import shutil
from pathlib import Path

def create_test_structure():
    """
    Create a test directory with various issues for validation.
    """
    # Create temporary test directory
    test_root = os.path.join(tempfile.gettempdir(), 'SPO_Preflight_Test')
    
    # Clean up if it exists
    if os.path.exists(test_root):
        shutil.rmtree(test_root)
    
    os.makedirs(test_root)
    print(f"Created test directory: {test_root}")
    
    # Test 1: Normal file (no issues)
    normal_file = os.path.join(test_root, 'normal_file.txt')
    with open(normal_file, 'w') as f:
        f.write('This is a normal file with no issues.')
    print("✓ Created normal file")
    
    # Test 2: Invalid characters in filename
    invalid_chars_dir = os.path.join(test_root, 'invalid_chars')
    os.makedirs(invalid_chars_dir)
    
    # Create files with various invalid characters (where OS allows)
    invalid_filenames = [
        'file_with_trailing_space .txt',
        'file_with_trailing_period.txt.',
        ' leading_space.txt',
        'file###with###hashes.txt',
        'file%percent%signs.txt',
    ]
    
    for filename in invalid_filenames:
        try:
            filepath = os.path.join(invalid_chars_dir, filename)
            with open(filepath, 'w') as f:
                f.write('Test file with invalid characters.')
            print(f"✓ Created: {filename}")
        except Exception as e:
            print(f"✗ Could not create {filename}: {e}")
    
    # Test 3: Long filename (>255 characters)
    long_name = 'A' * 260 + '.txt'
    try:
        long_file = os.path.join(test_root, long_name)
        with open(long_file, 'w') as f:
            f.write('File with very long name.')
        print(f"✓ Created long filename ({len(long_name)} chars)")
    except Exception as e:
        print(f"✗ Could not create long filename: {e}")
    
    # Test 4: Blocked extensions
    blocked_dir = os.path.join(test_root, 'blocked_extensions')
    os.makedirs(blocked_dir)
    
    blocked_files = ['test.exe', 'script.bat', 'library.dll', 'command.cmd']
    for filename in blocked_files:
        filepath = os.path.join(blocked_dir, filename)
        with open(filepath, 'w') as f:
            f.write('Blocked extension file.')
        print(f"✓ Created blocked file: {filename}")
    
    # Test 5: Deep folder structure
    deep_path = test_root
    for i in range(25):  # Create 25 levels
        deep_path = os.path.join(deep_path, f'level_{i:02d}')
    
    try:
        os.makedirs(deep_path)
        deep_file = os.path.join(deep_path, 'deep_file.txt')
        with open(deep_file, 'w') as f:
            f.write('File in very deep folder structure.')
        print(f"✓ Created deep folder structure (25 levels)")
    except Exception as e:
        print(f"✗ Could not create deep structure: {e}")
    
    # Test 6: Large file (simulated - create 1MB file)
    large_file = os.path.join(test_root, 'large_file.bin')
    with open(large_file, 'wb') as f:
        f.write(b'0' * (1024 * 1024))  # 1 MB (not truly large, but enough for testing)
    print("✓ Created 1MB test file")
    
    # Test 7: Long path (combine long folder names)
    long_path_base = test_root
    segment = 'Very_Long_Folder_Name_That_Exceeds_Normal_Limits_ABCDEFGHIJ_'
    
    try:
        for i in range(5):
            long_path_base = os.path.join(long_path_base, segment + str(i))
        
        os.makedirs(long_path_base)
        long_path_file = os.path.join(long_path_base, 'file_in_long_path.txt')
        
        with open(long_path_file, 'w') as f:
            f.write('File in very long path.')
        
        print(f"✓ Created long path structure ({len(long_path_file)} chars total)")
    except Exception as e:
        print(f"✗ Could not create long path: {e}")
    
    print("\n" + "="*70)
    print("Test structure created successfully!")
    print("="*70)
    print(f"\nTest directory: {test_root}")
    print("\nNow run the scanner on this directory:")
    print(f'python spo_preflight.py "{test_root}"')
    print("\nExpected issues:")
    print("  - Files with invalid characters")
    print("  - Files with leading/trailing spaces or periods")
    print("  - Long filenames (>255 chars)")
    print("  - Blocked extensions (.exe, .dll, .bat, .cmd)")
    print("  - Excessive folder depth (>20 levels)")
    print("  - Long paths (>400 chars)")
    print("\n" + "="*70)
    
    return test_root

if __name__ == '__main__':
    test_dir = create_test_structure()
    
    print("\nTest directory structure:")
    print("-" * 70)
    
    # Display directory tree (simple version)
    for root, dirs, files in os.walk(test_dir):
        level = root.replace(test_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        sub_indent = ' ' * 2 * (level + 1)
        for file in files[:5]:  # Limit to first 5 files per directory
            print(f"{sub_indent}{file}")
        
        if len(files) > 5:
            print(f"{sub_indent}... and {len(files) - 5} more files")
        
        if level > 3:  # Don't display too deep
            print(f"{sub_indent}... (structure continues)")
            break
