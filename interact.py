import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

def call_dfx_canister(method, args=None):
    """Call a method on the Motoko canister using `dfx`."""
    command = ['dfx', 'canister', 'call', 'ptc2_backend', method, '--network', 'playground']  # Adjust the network as needed

    if args:
        # Write the arguments to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
            temp_file.write(args)
            temp_file_path = temp_file.name
        
        # Use --argument-file to pass the temporary file to dfx
        command.extend(['--argument-file', temp_file_path])

    # Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)

    # Return the output or error
    if result.returncode == 0:
        return result.stdout
    else:
        return result.stderr

def add_patient(patient_data):
    """Add a single patient to the canister."""
    # Convert patient data to Candid format
    try:
        candid_data = patient_to_candid(patient_data)
        response = call_dfx_canister('addPatient', f"({candid_data})")
        print(response)
    except Exception as e:
        print(f"Error adding patient: {e}")

def patient_to_candid(patient_data):
    """Convert patient data to Candid format for `dfx`."""
    # Convert each field to the Candid format
    return f"""
    record {{
        patientID = "{patient_data['patientID']}";
        name = record {{
            first = "{patient_data['name']['first']}";
            last = "{patient_data['name']['last']}";
            middle = "{patient_data['name']['middle']}";
        }};
        dateOfBirth = "{patient_data['dateOfBirth']}";
        gender = "{patient_data['gender']}";
        contactInformation = "{patient_data['contactInformation']}";
        emergencyContact = "{patient_data['emergencyContact']}";
        medicalHistory = "{patient_data['medicalHistory']}";
        currentMedications = "{patient_data['currentMedications']}";
        insuranceDetails = "{patient_data['insuranceDetails']}";
        primaryPhysician = "{patient_data['primaryPhysician']}";
        visitRecords = "{patient_data['visitRecords']}";
        laboratoryResults = "{patient_data['laboratoryResults']}";
    }}
    """

def add_patients_from_file(file_path):
    """Add patients to the canister from a JSON file using parallel processing."""
    # Read JSON data from file
    with open(file_path, 'r') as f:
        patients_data = json.load(f)

    # Use ThreadPoolExecutor to parallelize the patient additions
    with ThreadPoolExecutor(max_workers=25) as executor:
        executor.map(add_patient, patients_data)

# Example usage
file_path = 'patient_data.json'  # Replace this with the path to your JSON file

# Add patients to the blockchain from the JSON file
add_patients_from_file(file_path)
