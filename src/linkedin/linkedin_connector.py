import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import random
from config import parameters
from ..ai.ai_integration import analyze_profile

# LinkedIn country codes mapping
LINKEDIN_COUNTRY_CODES = {
    "United States": ["us", "103644278"],
    "United Kingdom": ["uk", "101165590"],
    "Canada": ["ca", "101174742"],
    "Australia": ["au", "101452733"],
    "India": ["in", "102713980"],
    "Germany": ["de", "101282230"],
    "France": ["fr", "105015875"],
    "Italy": ["it", "103350119"],
    "Spain": ["es", "105646813"],
    "Netherlands": ["nl", "102890719"],
    # Add more countries as needed
}

def get_profile_headline(profile_card):
    """Extract profile headline from search result card with multiple selector attempts"""
    # Add specific XPath to target the headline element directly
    headline_xpath_selectors = [
        ".//div[contains(@class, 'entity-result__primary-subtitle')]/span[1]",
        ".//div[contains(@class, 'entity-result__primary-subtitle')]",
        ".//div[contains(@class, 'search-entity-result__primary-subtitle')]/span[1]",
        ".//div[contains(@class, 'search-entity-result__primary-subtitle')]"
    ]
    
    # Try XPath selectors first as they are more precise
    for xpath in headline_xpath_selectors:
        try:
            elements = profile_card.find_elements(By.XPATH, xpath)
            if elements:
                for element in elements:
                    headline = element.text.strip()
                    # Filter out common non-headline text
                    if (headline and 
                        len(headline) > 5 and 
                        not any(x in headline.lower() for x in ['view profile', 'profile', '• 1st', '• 2nd', '• 3rd', 'connection'])):
                        return headline
        except Exception:
            continue
    
    # Fallback to class name selectors if XPath fails
    class_selectors = [
        'entity-result__primary-subtitle',
        'search-entity-result__primary-subtitle',
        'entity-result__summary',
        'search-entity-result__summary'
    ]
    
    for selector in class_selectors:
        try:
            elements = profile_card.find_elements(By.CLASS_NAME, selector)
            if elements:
                headline = elements[0].text.strip()
                if (headline and 
                    len(headline) > 5 and 
                    not any(x in headline.lower() for x in ['view profile', 'profile', '• 1st', '• 2nd', '• 3rd', 'connection'])):
                    return headline
        except Exception:
            continue
    
    # Last attempt: Look for elements with job-related keywords
    try:
        all_elements = profile_card.find_elements(By.XPATH, ".//*")
        for element in all_elements:
            text = element.text.strip()
            # Look for text that contains job-related keywords
            job_indicators = ['at ', 'engineer', 'developer', 'manager', 'director', 'specialist', 
                            'professional', 'consultant', 'analyst', 'designer', 'scientist']
            if (text and 
                len(text) > 10 and 
                len(text) < 100 and  # Avoid large text blocks
                any(indicator in text.lower() for indicator in job_indicators) and
                not any(x in text.lower() for x in ['view profile', 'profile', '• 1st', '• 2nd', '• 3rd', 'connection'])):
                return text
    except Exception:
        pass
        
    return ""  # Return empty string if no headline found

def get_profile_name(profile_card):
    """Extract profile name from search result card with multiple selector attempts"""
    name_selectors = [
        'app-aware-link',
        'entity-result__title-text',
        'search-entity-result__title',
        'entity-result__title',
        'search-result__result-title',
        'actor-name'
    ]
    
    # First attempt: Try class name selectors
    for selector in name_selectors:
        try:
            elements = profile_card.find_elements(By.CLASS_NAME, selector)
            if elements:
                name = elements[0].text.strip()
                if name and not name.startswith(('View', 'Connect')):
                    return name
        except Exception:
            continue
    
    # Second attempt: Try more specific XPath approaches
    xpath_selectors = [
        ".//span[contains(@class, 'entity-result__title-text')]",
        ".//span[contains(@class, 'search-entity-result__title')]",
        ".//a[contains(@class, 'app-aware-link')]",
        ".//div[contains(@class, 'entity-result__title')]//span",
        ".//span[@dir='ltr']"
    ]
    
    for xpath in xpath_selectors:
        try:
            elements = profile_card.find_elements(By.XPATH, xpath)
            if elements:
                for element in elements:
                    name = element.text.strip()
                    if name and len(name) > 2 and not name.startswith(('View', 'Connect', '1st', '2nd', '3rd')):
                        return name
        except Exception:
            continue
    
    return ""

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
        login_success = login_to_linkedin(driver)
        if not login_success:
            print("ERROR: Failed to log in to LinkedIn. Please check your credentials.")
            return
        
        connections_made = 0
        base_url = 'https://www.linkedin.com/search/results/people/?keywords={keywords}&origin=SWITCH_SEARCH_VERTICAL'
        
        if parameters.search_geo_urn:
            geo_param = f'&geoUrn={parameters.search_geo_urn}'
            base_url += geo_param
            print(f"INFO: Filtering results using geoUrn ID: {parameters.search_geo_urn}")
            if parameters.search_country:
                print(f"INFO: Country name set to: {parameters.search_country} (for reference only)")
        
        for page_num in range(1, max_pages + 1):
            print(f'\nINFO: Processing search results page {page_num}')
            
            search_url = base_url.format(keywords=urllib.parse.quote(search_keywords))
            if page_num > 1:
                search_url += f'&page={page_num}'
            
            # Navigate with retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    driver.get(search_url)
                    
                    # Wait for either the results container or no results message
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'search-results-container'))
                    )
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"ERROR: Failed to load page {page_num} after {max_retries} attempts: {str(e)}")
                        return
                    print(f"WARNING: Retrying page load, attempt {attempt + 2}/{max_retries}")
                    time.sleep(5)
            
            # Wait for dynamic content to load
            time.sleep(5)
            
            # Scroll to load all results
            scroll_page(driver)
            
            # Find all profile cards - try different selectors
            profile_cards = []
            selectors = [
                'reusable-search-simple-insight-components',
                'entity-result__item',
                'search-result__occluded-item',
                'search-entity-result',
                'entity-result',
                'linked-area'
            ]
            
            for selector in selectors:
                try:
                    profile_cards = driver.find_elements(By.CLASS_NAME, selector)
                    if profile_cards:
                        print(f'INFO: Found {len(profile_cards)} profiles using selector "{selector}" on page {page_num}')
                        break
                except Exception:
                    continue
            
            if not profile_cards:
                print(f'WARNING: No profiles found on page {page_num}. LinkedIn might have changed their HTML structure.')
                try:
                    screenshot_path = f'search_results_page_{page_num}.png'
                    driver.save_screenshot(screenshot_path)
                    print(f'INFO: Saved debug screenshot to {screenshot_path}')
                except Exception:
                    pass
                continue
            
            # Process each profile card
            for index, profile_card in enumerate(profile_cards, start=1):
                if connections_made >= parameters.max_connections_per_session:
                    print(f"INFO: Reached maximum connections per session ({parameters.max_connections_per_session}). Stopping.")
                    return
                
                try:
                    # Get profile name using the new extraction function
                    profile_name = get_profile_name(profile_card)
                    
                    if not profile_name:  # Skip if we couldn't get the name
                        print(f"{index} ) ERROR: Empty profile name detected")
                        continue
                    
                    # Get headline before any clicks
                    profile_headline = get_profile_headline(profile_card)
                    print(f"Processing: {profile_name} - {profile_headline}")
                    
                    # Skip profiles in the exclude list
                    if profile_name in excluded_profiles or profile_name.strip() in excluded_profiles:
                        print(f"{index} ) SKIPPED: {profile_name} (in exclude list)")
                        continue
                    
                    # Add a small random delay to appear more human-like
                    time.sleep(random.uniform(1, 3))
                    
                    # Find the Connect button
                    connect_button_elements = profile_card.find_elements(By.CLASS_NAME, 'artdeco-button__text')
                    
                    if not connect_button_elements:
                        print(f"{index} ) UNAVAILABLE: {profile_name} (no connect button found)")
                        continue
                    
                    connect_button = None
                    for btn in connect_button_elements:
                        if btn.text.strip() == 'Connect':
                            connect_button = btn
                            break
                    
                    if not connect_button:
                        print(f"{index} ) UNAVAILABLE: {profile_name} (no connect button found)")
                        continue
                    
                    # Process based on button text
                    try:
                        # Scroll and click
                        scroll_to_element(driver, connect_button)
                        time.sleep(2)
                        connect_button.click()
                        
                        # Wait for modal to appear
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'artdeco-modal__content'))
                            )
                        except Exception:
                            print(f"WARNING: Connection modal didn't appear for {profile_name}")
                        
                        time.sleep(3)
                        
                        # Check if we can add a note - fixed XPath selector
                        add_note_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Add a note')]")
                        if add_note_buttons:
                            # Click "Add a note" button
                            add_note_buttons[0].click()
                            
                            # Wait for the message field to appear
                            try:
                                custom_message_field = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.ID, 'custom-message'))
                                )
                                
                                # Generate personalized message
                                personalized_message = analyze_profile(profile_name, profile_headline)
                                
                                # Enter the message in the text area
                                custom_message_field.send_keys(personalized_message)
                                time.sleep(1)
                            except Exception as e:
                                print(f"WARNING: Couldn't add note to {profile_name} - {e}")
                        
                        # Send the connection request
                        send_buttons = driver.find_elements(By.CLASS_NAME, 'artdeco-button--primary')
                        if send_buttons and send_buttons[0].is_enabled():
                            send_buttons[0].click()
                            
                            # Log successful connection with headline
                            connection_writer.writerow([
                                profile_name,
                                profile_headline,  # Now we have the headline
                                time.strftime("%Y-%m-%d %H:%M:%S")
                            ])
                            print(f"{index} ) CONNECTED: {profile_name}")
                            
                            # Increment connection counter
                            connections_made += 1
                            print(f"INFO: Made {connections_made}/{parameters.max_connections_per_session} connections this session")
                        else:
                            # Close the modal if unable to send
                            dismiss_buttons = driver.find_elements(By.CLASS_NAME, 'artdeco-modal__dismiss')
                            if dismiss_buttons:
                                dismiss_buttons[0].click()
                            print(f"{index} ) FAILED: {profile_name} (send button disabled)")
                    except Exception as e:
                        print(f'{index} ) ERROR: {profile_name} - {str(e)}')
                        # Close any open modals
                        try:
                            dismiss_buttons = driver.find_elements(By.CLASS_NAME, 'artdeco-modal__dismiss')
                            if dismiss_buttons:
                                dismiss_buttons[0].click()
                        except Exception:
                            pass
                    
                    # Wait between requests to avoid being rate limited
                    delay = parameters.connection_delay_seconds if hasattr(parameters, 'connection_delay_seconds') else 5
                    time.sleep(delay + random.uniform(1, 3))  # Add randomness to appear more human-like
                except Exception as e:
                    print(f'{index} ) ERROR processing profile: {str(e)}')
    finally:
        # Always close the browser
        driver.quit()
        
        if connections_made > 0:
            print(f"\nINFO: Session summary - sent {connections_made} connection requests")

def initialize_browser():
    """Initialize and return a Chrome webdriver instance with anti-detection measures"""
    try:
        # Set up Chrome options
        chrome_options = webdriver.ChromeOptions()
        
        # Set a user agent to reduce detection
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # Disable automation flags
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Initialize the driver without specifying version
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
        except Exception as chrome_error:
            print(f"First attempt failed, trying alternative initialization: {chrome_error}")
            # Fallback to basic initialization if the first attempt fails
            driver = webdriver.Chrome(options=chrome_options)
        
        # Execute CDP commands to disable navigator.webdriver flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"ERROR: Failed to initialize browser - {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Chrome is installed and up to date")
        print("2. Try closing all Chrome windows and trying again")
        print("3. Check if any antivirus is blocking ChromeDriver")
        return None

def login_to_linkedin(driver):
    """Log in to LinkedIn using credentials from parameters"""
    try:
        driver.get('https://www.linkedin.com/login')
        
        # Check if credentials are available
        if not parameters.linkedin_username or not parameters.linkedin_password:
            print("ERROR: LinkedIn credentials not found in parameters")
            return False
        
        # Wait for username field to be present
        try:
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            username_field.send_keys(parameters.linkedin_username)
            
            password_field = driver.find_element(By.ID, 'password')
            password_field.send_keys(parameters.linkedin_password)
            
            # Click login button
            driver.find_element(By.XPATH, '//*[@type="submit"]').click()
            
            # Wait for login to complete
            time.sleep(10)
            
            # Check if login was successful
            if "feed" in driver.current_url or "checkpoint" in driver.current_url:
                print("INFO: Successfully logged in to LinkedIn")
                return True
            elif "login-submit" in driver.page_source:
                print("ERROR: Login failed - incorrect credentials")
                return False
            else:
                print("WARNING: Login might have failed - unexpected redirect")
                return False
        except Exception as e:
            print(f"ERROR: Login page elements not found - {e}")
            return False
    except Exception as e:
        print(f"ERROR: Login failed - {e}")
        return False

def scroll_page(driver):
    """Scroll to the bottom of the page to load all results"""
    try:
        # Scroll down in multiple steps to appear more human-like
        for _ in range(3):
            html = driver.find_element(By.TAG_NAME, 'html')
            html.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
        
        html.send_keys(Keys.END)
        time.sleep(3)
    except Exception as e:
        print(f"ERROR: Failed to scroll page - {e}")

def scroll_to_element(driver, element):
    """Scroll to make an element visible"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(1)  # Give time for smooth scrolling
    except Exception as e:
        print(f"ERROR: Failed to scroll to element - {e}")

def main():
    """Main entry point for the LinkedIn connector"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Automation Tool')
    parser.add_argument('--max-connections', type=int, default=10,
                      help='Maximum number of connection requests to send')
    parser.add_argument('--test-mode', action='store_true',
                      help='Run in test mode with additional logging')
    args = parser.parse_args()
    
    # Update max connections parameter
    parameters.max_connections_per_session = args.max_connections
    
    # Set up CSV writer for connections
    with open('connections.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        try:
            connect_to_profiles(
                search_keywords='software engineer OR data scientist OR machine learning',
                max_pages=3,
                connection_writer=writer
            )
        except Exception as e:
            print(f"ERROR: Script execution failed - {e}")

if __name__ == "__main__":
    main()
