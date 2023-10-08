import xml.etree.ElementTree as ET
import argparse
from datetime import datetime
import csv

def unix_timestamp_to_datetime(ts):
    """Convert UNIX timestamp to human-readable format."""
    return datetime.utcfromtimestamp(int(ts))

def parse_malresults(filename, csv_filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    # Initialize counters for summary
    tls_delivery_count = 0
    tls_received_count = 0
    not_available_count = 0

    # Open CSV file for writing
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['UID', 'Date', 'Time', 'To Email Address', 'From Email Address', 'TLS Delivery', 'TLS Received']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()  # write header to the CSV

        for message in root.findall('message'):
            uid = message.get('UID')
            events = {event.get('name'): event.text for event in message.find('events')}
            event_times = {event.get('name'): event.get('time') for event in message.find('events')}  # Extracting times

            # Extract details
            date, time = unix_timestamp_to_datetime(event_times.get('ACCEPT', '0')).strftime('%Y-%m-%d %H:%M:%S').split()
            to_email_address = events.get('ORCPTS', 'N/A')
            from_email_address = events.get('SENDER', 'N/A')
            tls_delivery = events.get('TLS_DELIVERY', 'Not available')
            tls_received = events.get('TLS_RECEIVED', 'Not received with TLS')

            # Count TLS details for summary
            if tls_delivery != "Not available":
                tls_delivery_count += 1
            else:
                not_available_count += 1
            if tls_received != "Not received with TLS":
                tls_received_count += 1

            # Write the extracted details to the CSV file
            writer.writerow({
                'UID': uid,
                'Date': date,
                'Time': time,
                'To Email Address': to_email_address,
                'From Email Address': from_email_address,
                'TLS Delivery': tls_delivery,
                'TLS Received': tls_received
            })

    # Print the summary to console
    print(f"Number of messages with TLS Delivery available: {tls_delivery_count}")
    print(f"Number of messages with TLS Delivery not available: {not_available_count}")
    print(f"Number of messages received with TLS: {tls_received_count}")

def main():
    parser = argparse.ArgumentParser(description='Parse XML data from a file to extract email details and write to a CSV file.')
    parser.add_argument('filename', help='Path to the XML file to parse')
    parser.add_argument('csv_filename', help='Name of the CSV file for output')
    args = parser.parse_args()

    parse_malresults(args.filename, args.csv_filename)

if __name__ == '__main__':
    main()
