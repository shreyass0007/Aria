import os
import subprocess
import sys

TESTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests")

def run_test_file(filepath):
    # Run pytest on the file
    # We set PYTHONPATH to current directory
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", filepath],
            capture_output=True,
            text=True,
            env=env
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print(f"Scanning {TESTS_DIR}...")
    failed_tests = []
    passed_tests = []
    
    test_files = []
    for root, dirs, files in os.walk(TESTS_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(os.path.join(root, file))
    
    print(f"Found {len(test_files)} test files.")
    
    for i, filepath in enumerate(test_files):
        filename = os.path.basename(filepath)
        print(f"[{i+1}/{len(test_files)}] Running {filename}...", end="", flush=True)
        
        success, stdout, stderr = run_test_file(filepath)
        
        if success:
            print(" PASS")
            passed_tests.append(filename)
        else:
            print(" FAIL")
            failed_tests.append((filename, stdout, stderr))
            
    print("\n" + "="*40)
    print(f"Passed: {len(passed_tests)}")
    print(f"Failed: {len(failed_tests)}")
    print("="*40)
    
    if failed_tests:
        print("\nFailures:")
        for name, out, err in failed_tests:
            print(f"\n--- {name} ---")
            # Print last 10 lines of output to give a hint
            lines = out.splitlines()
            print("\n".join(lines[-20:]))
            if err:
                print("STDERR:")
                print(err)

if __name__ == "__main__":
    main()
