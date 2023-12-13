import openai
import os
import sys
import imaplib
import email
from email.mime.text import MIMEText
import smtplib
from email.utils import parseaddr
import time
from keep_alive import keep_alive
keep_alive()

# Setup OpenAI API key
try:
    openai.api_key = os.environ['key.txt']
except KeyError:
    sys.stderr.write("Error: OpenAI API key not found. Please set it up.\n")
    exit(1)

# Function to connect to the email server
def connect_to_email(username, password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    return mail

# Function to fetch the latest email
# Function to fetch the most recent email from a specific sender
def fetch_latest_email(mail):
  mail.select("inbox")
  _, message_numbers = mail.search(None, 'FROM', '"bryanedwardlongmd@gmail.com"')
  if not message_numbers[0]:
      return None  # Return None if no emails are found from the specified sender

  # Get the most recent email id, ignoring previously processed ones
  latest_email_id = message_numbers[0].split()[-1]
  _, data = mail.fetch(latest_email_id, '(RFC822)')
  email_message = email.message_from_bytes(data[0][1])

  return email_message





# Function to process the email content using OpenAI


  

def process_email_content(email_message):
    body = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = email_message.get_payload(decode=True).decode()

      # Using the v1/chat/completions endpoint for ChatGPT model
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Specify the GPT-4 model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Transform the provided information into a comprehensive urgent care telehealth note, adhering to the following format:Basic Information: Include Date, Patient Name, and DOB. Chief Complaint (CC): Detail the primary reason for the patient's visit. History of Present Illness (HPI): Elaborate on the current illness or injury. Medications: List current medications but no those prescribed today, this will go into the plan. Drug Allergies: Note any known drug allergies. Past Medical History: Provide relevant past medical history. Review of Systems (ROS): State 'negative except as above' unless otherwise specified. Physical Exam (PE): Focus on telemedicine aspects. Document when possible a direct visual exam with patient's or caregiver's assistance, and thoroughly interrogate for physical findings when a visual exam couldn't be done.  Telehealth Consultation Conducted: This appointment was held remotely via video call. No in-person physical examination was performed. All evaluations and recommendations are based on the patient's self-reported medical history and symptoms, as well as any available remote assessment tools. Labs and Imaging: Include details if mentioned in the statement, if the patient had labs recently mention those here.  If they will be ordered by the clinican today , mention the labs in the plan and mention patient was sent to the nearest Labcorps (or Simonmed imaging if imaging) based on the patients zipcode, determine their local lab corps abd place the instructions into their discharge statement, place which lab or imaging center the patient was sent to in the plan after the medication (or imaging if imaging ordered).  Impression: List the top three differential diagnoses if not stated in the statement. Plan: Provide a treatment plan using www.emedicine.com as a resource, put this reference at the bottom of the note.. Include appropriate medications, labs, imaging.  Note that over 40 minutes were spent with the patient. Prescriptions (RX): State as noted in the chart and discuss medication use, pros, cons, and potential side effects. Discharge Instructions: Written instructions provided. Specific Instructions include: Return or call immediately if symptoms worsen or change. Seek emergency care after office hours if needed. The patient should see their primary doctor or another qualified physician within the discussed timeframe. Recheck/Follow up within 2 days. Emergent Care Directions: Advise seeking emergency treatment for new or increasing pain, fever, chills, vomiting uncontrolled by medication, or significantly worsening symptoms. Verbal Understanding: Ensure the responsible individual verbalizes understanding of the assessment, treatment plan, and signs/symptoms for urgent and emergent medical follow-up. Code for 99214 (new patient) or 99204 (follow-up patient) with justification.  Coding should be placed below the last section, the plan." + body}
        ]
    )

    return response.choices[0].message['content'] if response.choices else "No response"



# Function to send the processed email
def send_processed_email(sender, receiver, password, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

# Main Execution
username = "aipatientprocessing@gmail.com"
password = "dzqk mjfi mgrn qnnm"
processed_ids = set()
last_processed_email_id = None

while True:
  try:
      mail = connect_to_email(username, password)
      latest_email = fetch_latest_email(mail)

      if latest_email is not None:
          # Extract the ID of the latest email
          latest_email_id = latest_email.get('ID')  # Replace 'ID' with the correct attribute for the email ID

          # Check if this email has already been processed
          if latest_email_id != last_processed_email_id:
              processed_content = process_email_content(latest_email)
              send_processed_email(username, "bryanedwardlongmd@gmail.com", password, "Processed Email Content", processed_content)
              send_processed_email(username, "aipatientprocessing@gmail.com", password, "Processed Email Content", processed_content)

              # Update the last processed email ID
              last_processed_email_id = latest_email_id

      time.sleep(5)  # Wait for 5 seconds before checking again

  except Exception as e:
      print(f"An error occurred: {e}")
      time.sleep(60)  # Wait a minute before trying again

