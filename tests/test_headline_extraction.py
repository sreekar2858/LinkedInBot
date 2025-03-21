#!/usr/bin/env python
"""
Test script to validate LinkedIn profile headline extraction
"""

import sys
import time
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
from selenium.webdriver.common.by import By

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import functions to test
from src.linkedin.linkedin_connector import get_profile_headline

class TestHeadlineExtraction(unittest.TestCase):
    """Tests for LinkedIn profile headline extraction"""
    
    def test_headline_extraction_class_selectors(self):
        """Test headline extraction using class selectors"""
        # Create a mock profile card with headline in 'entity-result__primary-subtitle'
        mock_element = MagicMock()
        mock_element.text = "Senior Software Engineer at Microsoft"
        
        mock_profile_card = MagicMock()
        mock_profile_card.find_elements.return_value = [mock_element]
        
        # Test first selector
        headline = get_profile_headline(mock_profile_card)
        
        # Verify find_elements was called with the right selector
        mock_profile_card.find_elements.assert_called_with(By.CLASS_NAME, 'entity-result__primary-subtitle')
        
        # Verify the headline was extracted correctly
        self.assertEqual(headline, "Senior Software Engineer at Microsoft")
    
    def test_headline_extraction_xpath(self):
        """Test headline extraction using XPath selectors"""
        # Create a mock profile card that fails on class selectors but works with XPath
        mock_element = MagicMock()
        mock_element.text = "Data Scientist | AI Researcher"
        
        mock_profile_card = MagicMock()
        # First call (class selectors) returns empty list
        # Second call (XPath) returns element with headline
        mock_profile_card.find_elements.side_effect = [
            [], [], [], [], [], [],  # All class selectors fail
            [mock_element]  # First XPath selector succeeds
        ]
        
        headline = get_profile_headline(mock_profile_card)
        
        # Verify the headline was extracted correctly
        self.assertEqual(headline, "Data Scientist | AI Researcher")
    
    def test_headline_extraction_spans(self):
        """Test headline extraction from spans"""
        # Create a mock profile card that fails on class and XPath selectors
        mock_span = MagicMock()
        mock_span.text = "Engineering Manager with 10+ years experience in cloud computing"
        
        mock_profile_card = MagicMock()
        # All previous selectors fail, but span extraction works
        mock_profile_card.find_elements.side_effect = [
            [], [], [], [], [], [],  # All class selectors fail
            [], [], [], [], [],      # All XPath selectors fail
            [mock_span]              # Span selector returns our element
        ]
        
        headline = get_profile_headline(mock_profile_card)
        
        # Verify the headline was extracted correctly
        self.assertEqual(headline, "Engineering Manager with 10+ years experience in cloud computing")
    
    def test_headline_extraction_job_keywords(self):
        """Test headline extraction using job keywords"""
        # Create elements with job-related text
        mock_element1 = MagicMock()
        mock_element1.text = "View profile"  # Should be ignored
        
        mock_element2 = MagicMock()
        mock_element2.text = "Product Manager at Google"  # Contains job indicator 'manager'
        
        mock_profile_card = MagicMock()
        # All previous methods fail, but keyword detection works
        mock_profile_card.find_elements.side_effect = [
            [], [], [], [], [], [],  # All class selectors fail
            [], [], [], [], [],      # All XPath selectors fail
            [],                      # Span selector fails
            [mock_element1, mock_element2]  # Elements for keyword detection
        ]
        
        headline = get_profile_headline(mock_profile_card)
        
        # Verify the headline was extracted correctly
        self.assertEqual(headline, "Product Manager at Google")
    
    def test_headline_extraction_empty(self):
        """Test headline extraction when no headline can be found"""
        # Create a mock profile card where all extraction methods fail
        mock_profile_card = MagicMock()
        mock_profile_card.find_elements.return_value = []
        
        headline = get_profile_headline(mock_profile_card)
        
        # Verify the result is an empty string
        self.assertEqual(headline, "")
        
    def test_headline_extraction_filters_buttons(self):
        """Test that button text is not mistaken for headlines"""
        # Create a mock element with text that should be filtered out
        mock_element = MagicMock()
        mock_element.text = "Connect"  # Should be filtered out
        
        mock_profile_card = MagicMock()
        mock_profile_card.find_elements.return_value = [mock_element]
        
        headline = get_profile_headline(mock_profile_card)
        
        # Verify the result is an empty string since "Connect" is filtered
        self.assertEqual(headline, "")

if __name__ == "__main__":
    unittest.main()