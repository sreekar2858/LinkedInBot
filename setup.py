from setuptools import setup, find_packages

setup(
    name="linkedin_networking",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'selenium>=4.0.0',
        'webdriver-manager>=4.0.1',
        'requests',
        'python-dotenv>=0.19.0',
        'google-genai',
        'openai'
    ],
    python_requires='>=3.8',
)