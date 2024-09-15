import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(PatientInfoApp());

class PatientInfoApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Patient Info App',
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: PatientInfoScreen(),
    );
  }
}

class PatientInfoScreen extends StatefulWidget {
  @override
  _PatientInfoScreenState createState() => _PatientInfoScreenState();
}

class _PatientInfoScreenState extends State<PatientInfoScreen> {
  final TextEditingController _controller = TextEditingController();
  Map<String, dynamic>? patientData;

  Future<void> fetchPatientData(int id) async {
    final url = 'http://10.189.94.178:5000/patient/$id';
    try {
      final response = await http.get(Uri.parse(url));
      if (response.statusCode == 200) {
        setState(() {
          patientData = jsonDecode(response.body);
        });
      } else {
        setState(() {
          patientData = {'error': 'Failed to load patient data.'};
        });
      }
    } catch (e) {
      setState(() {
        patientData = {'error': 'Failed to connect to the server.'};
      });
    }
  }

  Widget displayPatientInfo() {
    if (patientData == null) {
      return Center(child: Text('Enter a Patient ID to get information'));
    } else if (patientData!.containsKey('error')) {
      return Center(child: Text(patientData!['error']));
    } else {
      return GridView.builder(
        padding: EdgeInsets.all(8.0),
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2, // Display two elements in a row
          childAspectRatio: 2 / 1.2, // Adjusted aspect ratio
          mainAxisSpacing: 10,
          crossAxisSpacing: 10,
        ),
        itemCount: patientData!.length,
        itemBuilder: (context, index) {
          String key = patientData!.keys.elementAt(index);
          var value = patientData![key];

          return Container(
            padding: const EdgeInsets.all(12.0),
            decoration: BoxDecoration(
              color: Colors.grey[850],
              borderRadius: BorderRadius.circular(8.0),
              border: Border.all(color: Colors.blueAccent),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      getIconForKey(key),
                      color: Colors.blueAccent,
                    ),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        key,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.blueAccent,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 10),
                Expanded(
                  child: SingleChildScrollView(
                    child: Text(
                      formatValue(key, value),
                      style: TextStyle(fontSize: 14, color: Colors.white70),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      );
    }
  }

  IconData getIconForKey(String key) {
    switch (key) {
      case 'contactInformation':
        return Icons.contact_mail;
      case 'currentMedications':
        return Icons.medical_services;
      case 'dateOfBirth':
        return Icons.cake;
      case 'emergencyContact':
        return Icons.contact_phone;
      case 'gender':
        return Icons.person;
      case 'insuranceDetails':
        return Icons.health_and_safety;
      case 'laboratoryResults':
        return Icons.science;
      case 'medicalHistory':
        return Icons.history;
      case 'name':
        return Icons.account_circle;
      case 'primaryPhysician':
        return Icons.local_hospital;
      case 'visitRecords':
        return Icons.record_voice_over;
      default:
        return Icons.info;
    }
  }

  String formatValue(String key, dynamic value) {
    try {
      if (value is String && (value.startsWith('{') || value.startsWith('['))) {
        var parsedValue =
            jsonDecode(value.replaceAll("'", '"')); // Decode stringified JSON
        return prettyPrintJson(parsedValue);
      }
    } catch (e) {
      return value.toString(); // Return raw value if parsing fails
    }

    if (key == 'name' && value is Map) {
      return '${value['first']} ${value['middle']} ${value['last']}';
    } else if (value is List) {
      return value.join(', ');
    }

    return value.toString();
  }

  String prettyPrintJson(dynamic parsedJson) {
    if (parsedJson is Map) {
      return parsedJson.entries.map((e) => "${e.key}: ${e.value}").join('\n');
    } else if (parsedJson is List) {
      return parsedJson.map((e) => e.toString()).join('\n');
    } else {
      return parsedJson.toString();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Patient Information'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _controller,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: 'Enter Patient ID',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                if (_controller.text.isNotEmpty) {
                  fetchPatientData(int.parse(_controller.text));
                }
              },
              child: Text('Get Patient Info'),
            ),
            SizedBox(height: 20),
            Expanded(child: displayPatientInfo()),
          ],
        ),
      ),
    );
  }
}
