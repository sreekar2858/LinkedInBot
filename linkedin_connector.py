from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import parameters
from gemini_integration import analyze_profile

def connect_to_profiles(search_keywords, max_pages, connection_writer, excluded_profiles=[]):
    """
    Search for LinkedIn profiles matching keywords and send connection requests
    
    Args:
        search_keywords: Keywords to search for
        max_pages: Maximum number of search result pages to process
        connection_writer: CSV writer to log successful connections
        excluded_profiles: List of profile names to ignore
    """
    driver = initialize_browser()
    
    if not driver:
        print("ERROR: Failed to initialize browser")
        return
        
    try:
        login_to_linkedin(driver)
        
        for page_num in range(1, max_pages + 1):
            print(f'\nINFO: Processing search results page {page_num}')
            
            # Navigate to search results page
            search_url = f'https://www.linkedin.com/search/results/people/?keywords={search_keywords}&origin=GLOBAL_SEARCH_HEADER&page={page_num}'
            driver.get(search_url)
            time.sleep(5)
            
            # Scroll to bottom of page to load all results
            scroll_page(driver)
            
            # Find all profile cards
            profile_cards = driver.find_elements(By.CLASS_NAME, 'linked-area')
            print(f'INFO: Found {len(profile_cards)} profiles on page {page_num}')
            
            # Process each profile card
            for index, profile_card in enumerate(profile_cards, start=1):
                profile_name = profile_card.text.split('\n')[0]
                
                # Skip profiles in the exclude list
                if profile_name in excluded_profiles or profile_name.strip() in excluded_profiles:
                    print(f"{index} ) SKIPPED: {profile_name} (in exclude list)")
                    continue
                    
                # Find the Connect button
                connect_button_elements = profile_card.find_elements(By.CLASS_NAME, 'artdeco-button__text')
                
                if not connect_button_elements:
                    print(f"{index} ) UNAVAILABLE: {profile_name} (no connect button found)")
                    continue
                    
                connect_button = connect_button_elements[0]
                
                # Process based on button text
                if connect_button.text == 'Connect':
                    try:
                        # Extract profile headline if available
                        profile_headline = ""
                        headline_elements = profile_card.find_elements(By.CLASS_NAME, 'entity-result__primary-subtitle')
                        if headline_elements:
                            profile_headline = headline_elements[0].text
                            
                        # Scroll to the connect button
                        scroll_to_element(driver, connect_button)
                        time.sleep(2)
                        
                        # Click connect button
                        connect_button.click()
                        time.sleep(3)
                        
                        # Check if we can add a note
                        add_note_buttons = driver.find_elements(By.XPATH, "//button[contains(.,'Add a note')]")
                        if add_note_buttons:
                            # Click "Add a note" button
                            add_note_buttons[0].click()
                            time.sleep(2)
                            
                            # Generate personalized message
                            personalized_message = analyze_profile(profile_name, profile_headline)
                            
                            # Enter the message in the text area
                            custom_message_field = driver.find_element(By.ID, 'custom-message')
                            custom_message_field.send_keys(personalized_message)
                            time.sleep(1)
                        
                        # Send the connection request
                        send_buttons = driver.find_elements(By.CLASS_NAME, 'artdeco-button--primary')
                        if send_buttons and send_buttons[0].is_enabled():
                            send_buttons[0].click()
                            # Log successful connection
                            connection_writer.writerow([profile_name, profile_headline, time.strftime("%Y-%m-%d %H:%M:%S")])
                            print(f"{index} ) CONNECTED: {profile_name}")
                        else:
                            # Close the modal if unable to send
                            dismiss_buttons = driver.find_elements(By.CLASS_NAME, 'artdeco-modal__dismiss')
                            if dismiss_buttons:
                                dismiss_buttons[0].click()
                            print(f"{index} ) FAILED: {profile_name} (send button disabled)")
                    except Exception as e:
                        print(f'{index} ) ERROR: {profile_name} - {str(e)}')
                    
                    # Wait between requests to avoid being rate limited
                    time.sleep(5)
                elif connect_button.text == 'Pending':
                    print(f"{index} ) PENDING: {profile_name}")
                else:
                    if profile_name:
                        print(f"{index} ) UNAVAILABLE: {profile_name} (status: {connect_button.text})")
                    else:
                        print(f"{index} ) ERROR: You might have reached connection limit")
    finally:
        # Always close the browser
        driver.quit()

def initialize_browser():
    """Initialize and return a Chrome webdriver instance"""
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"ERROR: Failed to initialize browser - {e}")
        return None

def login_to_linkedin(driver):
    """Log in to LinkedIn using credentials from parameters"""
    try:
        driver.get('https://www.linkedin.com/login')
        
        # Enter username and password
        driver.find_element(By.ID, 'username').send_keys(parameters.linkedin_username)
        driver.find_element(By.ID, 'password').send_keys(parameters.linkedin_password)
        
        # Click login button
        driver.find_element(By.XPATH, '//*[@type="submit"]').click()
        
        # Wait for login to complete
        time.sleep(10)
        
        # Check if login was successful
        if "feed" in driver.current_url or "checkpoint" in driver.current_url:
            print("INFO: Successfully logged in to LinkedIn")
            return True
        else:
            print("WARNING: Login might have failed - unexpected redirect")
            return False
    except Exception as e:
        print(f"ERROR: Login failed - {e}")
        return False

def scroll_page(driver):
    """Scroll to the bottom of the page to load all results"""
    try:
        html = driver.find_element(By.TAG_NAME, 'html')
        html.send_keys(Keys.END)
        time.sleep(5)
    except Exception as e:
        print(f"ERROR: Failed to scroll page - {e}")

def scroll_to_element(driver, element):
    """Scroll to make an element visible"""
    try:
        coordinates = element.location_once_scrolled_into_view
        driver.execute_script(f"window.scrollTo({coordinates['x']}, {coordinates['y']});")
    except Exception as e:
        print(f"ERROR: Failed to scroll to element - {e}")
