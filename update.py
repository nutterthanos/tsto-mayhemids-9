# Define file path and increment
main_script_path = "/home/runner/work/tsto-mayhemids/tsto-mayhemids/grab_mayhemids.py"
increment = 1000000
max_end_id = 1001000000  # define the upper limit for END_ID

# Read the main script file
with open(main_script_path, "r") as file:
    lines = file.readlines()

# Update START_ID and END_ID
for i, line in enumerate(lines):
    if line.strip().startswith("START_ID ="):
        # Extract current START_ID value and increment it
        current_start_id = int(line.split("=")[1].strip())
        new_start_id = current_start_id + increment
        lines[i] = f"START_ID = {new_start_id}\n"
        
    if line.strip().startswith("END_ID ="):
        # Extract current END_ID value and increment it
        current_end_id = int(line.split("=")[1].strip())
        new_end_id = current_end_id + increment
        # Check if the new END_ID exceeds max_end_id
        if new_end_id > max_end_id:
            print("END_ID has reached or exceeded the maximum limit.")
            new_end_id = max_end_id
        lines[i] = f"END_ID = {new_end_id}\n"

# Write the updated lines back to the main script file
with open(main_script_path, "w") as file:
    file.writelines(lines)

print(f"Updated START_ID to {new_start_id} and END_ID to {new_end_id} in {main_script_path}")
