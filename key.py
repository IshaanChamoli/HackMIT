import subprocess

def verify_signature(patient_id):
    # Get the patient's data signature
    command = ['dfx', 'canister', 'call', 'patient_transfer_protocol_backend', method, '--network', 'playground']
    print(f"Signature: {result.stdout}")

    # Get the canister's public key for verification
    public_key_result = subprocess.run(['dfx', 'canister', 'call', 'patient_transfer_protocol_backend', 'getPublicKey'], capture_output=True, text=True)
    print(f"Public Key: {public_key_result.stdout}")

# Example usage
verify_signature("")

