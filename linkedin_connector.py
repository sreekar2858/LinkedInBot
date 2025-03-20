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
from ai_integration import analyze_profile
import random

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
        
        # Connection counter for this session
        connections_made = 0
        
        for page_num in range(1, max_pages + 1):
            print(f'\nINFO: Processing search results page {page_num}')
            
            # Navigate to search results page
            search_url = f'https://www.linkedin.com/search/results/people/?keywords={search_keywords}&origin=GLOBAL_SEARCH_HEADER&page={page_num}'
            driver.get(search_url)
            
            # Wait for page to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'search-results-container'))
                )
            except Exception:
                print("WARNING: Page load timeout. Continuing anyway...")
            
            time.sleep(5)
            
            # Scroll to bottom of page to load all results
            scroll_page(driver)
            
            # Find all profile cards - try different selectors as LinkedIn may change
            profile_cards = []
            selectors = ['linked-area', 'entity-result__title-text', 'search-entity-result__title']
            
            for selector in selectors:
                profile_cards = driver.find_elements(By.CLASS_NAME, selector)
                if profile_cards:
                    print(f'INFO: Found {len(profile_cards)} profiles using selector "{selector}" on page {page_num}')
                    break
            
            if not profile_cards:
                print(f'WARNING: No profiles found on page {page_num}. LinkedIn might have changed their HTML structure.')
                continue
            
            # Process each profile card
            for index, profile_card in enumerate(profile_cards, start=1):
                # Check if we've reached the session connection limit
                if connections_made >= parameters.max_connections_per_session:
                    print(f"INFO: Reached maximum connections per session ({parameters.max_connections_per_session}). Stopping.")
                    return
                
                try:
                    profile_name = profile_card.text.split('\n')[0]
                    
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
                        
                    connect_button = connect_button_elements[0]
                    
                    # Process based on button text
                    if connect_button.text == 'Connect':
                        try:
                            # Extract profile headline if available
                            profile_headline = ""
                            headline_selectors = ['entity-result__primary-subtitle', 'search-entity-result__primary-subtitle']
                            
                            for selector in headline_selectors:
                                headline_elements = profile_card.find_elements(By.CLASS_NAME, selector)
                                if headline_elements:
                                    profile_headline = headline_elements[0].text
                                    break
                                
                            # Scroll to the connect button
                            scroll_to_element(driver, connect_button)
                            time.sleep(2)
                            
                            # Click connect button
                            connect_button.click()
                            
                            # Wait for modal to appear
                            try:
                                WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, 'artdeco-modal__content'))
                                )
                            except Exception:
                                print(f"WARNING: Connection modal didn't appear for {profile_name}")
                            
                            time.sleep(3)
                            
                            # Check if we can add a note
                            add_note_buttons = driver.find_elements(By.XPATH, "//button[contains(.,'Add a note')]")
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
                                # Log successful connection
                                connection_writer.writerow([profile_name, profile_headline, time.strftime("%Y-%m-%d %H:%M:%S")])
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
                            except:
                                pass
                        
                        # Wait between requests to avoid being rate limited
                        delay = parameters.connection_delay_seconds if hasattr(parameters, 'connection_delay_seconds') else 5
                        time.sleep(delay + random.uniform(1, 3))  # Add randomness to appear more human-like
                    elif connect_button.text == 'Pending':
                        print(f"{index} ) PENDING: {profile_name}")
                    else:
                        if profile_name:
                            print(f"{index} ) UNAVAILABLE: {profile_name} (status: {connect_button.text})")
                        else:
                            print(f"{index} ) ERROR: You might have reached connection limit")
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
        
        # Initialize the driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Execute CDP commands to disable navigator.webdriver flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"ERROR: Failed to initialize browser - {e}")
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
