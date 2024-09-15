import Principal "mo:base/Principal";
import Text "mo:base/Text";
import Blob "mo:base/Blob";
import Hex "./utils/Hex";
import SHA256 "./utils/SHA256";
import Array "mo:base/Array";
import Nat "mo:base/Nat";  // Import the Nat module for conversion

actor PatientDatabase {
    // Define a simple key for encryption and decryption
    let encryptionKey: Text = "my_secret_key";  // Simple key for demonstration

    // Define the original Patient type
    type Patient = {
        patientID: Text;
        name: { first: Text; last: Text; middle: Text };
        dateOfBirth: Text;
        gender: Text;
        contactInformation: Text;
        emergencyContact: Text;
        medicalHistory: Text;
        currentMedications: Text;
        insuranceDetails: Text;
        primaryPhysician: Text;
        visitRecords: Text;
        laboratoryResults: Text;
    };

    // Define the EncryptedPatient type for internal storage
    type EncryptedPatient = {
        patientID: Text;
        encryptedName: Text;
        encryptedDateOfBirth: Text;
        encryptedGender: Text;
        encryptedContactInformation: Text;
        encryptedEmergencyContact: Text;
        encryptedMedicalHistory: Text;
        encryptedCurrentMedications: Text;
        encryptedInsuranceDetails: Text;
        encryptedPrimaryPhysician: Text;
        encryptedVisitRecords: Text;
        encryptedLaboratoryResults: Text;
    };

    stable var patients: [EncryptedPatient] = [];

    // Encrypt and add a new patient
    public func addPatient(patient: Patient): async () {
        let encryptedPatient = {
            patientID = patient.patientID;
            encryptedName = encrypt(patient.name.first # " " # patient.name.middle # " " # patient.name.last, encryptionKey);
            encryptedDateOfBirth = encrypt(patient.dateOfBirth, encryptionKey);
            encryptedGender = encrypt(patient.gender, encryptionKey);
            encryptedContactInformation = encrypt(patient.contactInformation, encryptionKey);
            encryptedEmergencyContact = encrypt(patient.emergencyContact, encryptionKey);
            encryptedMedicalHistory = encrypt(patient.medicalHistory, encryptionKey);
            encryptedCurrentMedications = encrypt(patient.currentMedications, encryptionKey);
            encryptedInsuranceDetails = encrypt(patient.insuranceDetails, encryptionKey);
            encryptedPrimaryPhysician = encrypt(patient.primaryPhysician, encryptionKey);
            encryptedVisitRecords = encrypt(patient.visitRecords, encryptionKey);
            encryptedLaboratoryResults = encrypt(patient.laboratoryResults, encryptionKey);
        };
        // Store the encrypted patient record
        patients := Array.append(patients, [encryptedPatient]);
    };

    // Simple XOR-based encryption for demonstration purposes
    func encrypt(data: Text, key: Text): Text {
        let keyBytes = Blob.toArray(Text.encodeUtf8(key));
        let dataBytes = Blob.toArray(Text.encodeUtf8(data));
        let encryptedBytes = Array.tabulate<Nat8>(dataBytes.size(), func(i) {
            dataBytes[i] ^ keyBytes[i % keyBytes.size()];
        });
        return Hex.encode(encryptedBytes);
    };

    // Simple XOR-based decryption
    func decrypt(encryptedData: Text, key: Text): Text {
        let encryptedBytes = switch (Hex.decode(encryptedData)) {
            case (#ok bytes) bytes;
            case (#err _) return "Decoding Error"; // Handle decode error
        };
        let keyBytes = Blob.toArray(Text.encodeUtf8(key));
        let decryptedBytes = Array.tabulate<Nat8>(encryptedBytes.size(), func(i) {
            encryptedBytes[i] ^ keyBytes[i % keyBytes.size()];
        });
        return switch (Text.decodeUtf8(Blob.fromArray(decryptedBytes))) {
            case (?text) text;
            case (null) "Decoding Error";
        };
    };

    // Retrieve a patient by number (decrypting the data)
    public query func getPatientById(id: Nat): async ?Patient {
        // Construct the formatted patient ID
        let formattedPatientID = "unique-patient-id-" # Nat.toText(id);

        // Find the patient and return the ID for debugging purposes
        let foundPatient = Array.find<EncryptedPatient>(patients, func (p) = p.patientID == formattedPatientID);
        
        switch (foundPatient) {
            case (?encryptedPatient) {
                // Decrypt the patient data using the same key
                let patient = {
                    patientID = encryptedPatient.patientID;
                    name = {
                        first = decrypt(encryptedPatient.encryptedName, encryptionKey);
                        last = "";
                        middle = "";
                    };
                    dateOfBirth = decrypt(encryptedPatient.encryptedDateOfBirth, encryptionKey);
                    gender = decrypt(encryptedPatient.encryptedGender, encryptionKey);
                    contactInformation = decrypt(encryptedPatient.encryptedContactInformation, encryptionKey);
                    emergencyContact = decrypt(encryptedPatient.encryptedEmergencyContact, encryptionKey);
                    medicalHistory = decrypt(encryptedPatient.encryptedMedicalHistory, encryptionKey);
                    currentMedications = decrypt(encryptedPatient.encryptedCurrentMedications, encryptionKey);
                    insuranceDetails = decrypt(encryptedPatient.encryptedInsuranceDetails, encryptionKey);
                    primaryPhysician = decrypt(encryptedPatient.encryptedPrimaryPhysician, encryptionKey);
                    visitRecords = decrypt(encryptedPatient.encryptedVisitRecords, encryptionKey);
                    laboratoryResults = decrypt(encryptedPatient.encryptedLaboratoryResults, encryptionKey);
                };
                return ?patient;
            };
            case (null) { 
                null
            };
        }
    };

    // Retrieve all patient IDs for debugging
    public query func getPatientIds(): async [Text] {
        return Array.map<EncryptedPatient, Text>(patients, func(p) { p.patientID });
    };

    // Clear all patient records
    public func clearPatients(): async () {
        patients := [];
    };

    public query func zgetEncryptedPatients(): async [EncryptedPatient] {
        return patients;
    };
}
