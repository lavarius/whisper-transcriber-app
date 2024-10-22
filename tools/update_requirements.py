import os
import subprocess
import sys

def update_requirements_file(requirements_path):
    # Read existing requirements
    try:
        with open(requirements_path, 'r') as f:
            existing_requirements = f.read().splitlines()
    except FileNotFoundError:
        print("Requirements file not found, creating a new one.")
        existing_requirements = []

    # Run pip freeze to get all installed packages with versions
    result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
    all_packages = dict(line.split('==') for line in result.stdout.splitlines())

    # Update requirements with versions
    updated_requirements = []
    for req in existing_requirements:
        package_name = req.split('==')[0].strip()  # Get package name without version
        if package_name in all_packages:
            updated_requirements.append(f"{package_name}=={all_packages[package_name]}")
        else:
            updated_requirements.append(req)  # Keep original if not found

    # Write updated requirements back to the file
    with open(requirements_path, 'w') as f:
        for req in sorted(updated_requirements):
            f.write(f"{req}\n")

    print(f"Updated requirements file at: {requirements_path}")

# Script execution
def run_update_script():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.normpath(os.path.join(script_dir, '..', 'requirements.txt'))
    update_requirements_file(requirements_path)

if __name__ == "__main__":
    run_update_script()