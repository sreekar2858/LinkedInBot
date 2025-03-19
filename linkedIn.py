import parameters
import csv
import os.path
import time
from linkedin_connector import connect_to_profiles

def main():
    try:
        # Set up CSV logging
        connections_file = parameters.connections_file
        file_exists = os.path.isfile(connections_file)
        
        with open(connections_file, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            
            # Write header if file is new
            if not file_exists:
                csv_writer.writerow(['Name', 'Headline', 'Connection Date'])
            
            # Process excluded profiles
            excluded_profiles = []
            if parameters.exclude_connections:
                excluded_profiles = [name.strip() for name in parameters.exclude_connections.split(',') if name]
            
            # Start connecting
            connect_to_profiles(
                search_keywords=parameters.search_keywords,
                max_pages=parameters.max_pages_to_search,
                connection_writer=csv_writer,
                excluded_profiles=excluded_profiles
            )
            
    except KeyboardInterrupt:
        print("\n\nINFO: Process interrupted by user\n")
    except Exception as e:
        print(f'ERROR: {str(e)}')

if __name__ == "__main__":
    main()
