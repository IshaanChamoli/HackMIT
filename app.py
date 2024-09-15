import subprocess
import tempfile
from flask import Flask, jsonify

app = Flask(__name__)

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
        raise RuntimeError(f"Error calling canister: {result.stderr}")

@app.route('/patient/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Retrieve a patient by ID from the canister."""
    try:
        # Call the getPatientById method with the patient ID
        response = call_dfx_canister('getPatientById', f"({patient_id})")
        # Print raw response for debugging
        print("Raw Response:", response)
        # Return the raw response text
        return response
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)