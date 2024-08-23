import os
import sys
import subprocess
import time

def restart_touchdesigner(project_path):
    # Save the current project
    print("Saving project...")
    project.save()

    # Get the current TouchDesigner executable path
    touchdesigner_path = sys.executable

    # Print paths for debugging
    print(f"TouchDesigner path: {touchdesigner_path}")
    print(f"Project path: {project_path}")

    # Delay to ensure the project is fully saved before closing
    time.sleep(2)

    # Restart TouchDesigner with the specified project
    command = f'"{touchdesigner_path}" "{project_path}"'
    print(f"Running command: {command}")
    
    # Close the current instance of TouchDesigner
    subprocess.Popen(command, shell=True)

    # Exit the current instance of TouchDesigner
    sys.exit()

# Get the project path from the argument
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No project path provided.")
        sys.exit(1)
    
    project_path = sys.argv[1]
    restart_touchdesigner(project_path)
