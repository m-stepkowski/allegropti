# Allegro Search Optimization

## Overview

This web application serves as an advanced search engine for the Allegro platform, utilizing the Multi-Armed Bandit (MAB) algorithm to optimize search results. It's designed to help users find the best listing prices for products across various categories on Allegro, Poland's leading e-commerce platform. The application has been developed as a part of the master's thesis authored by (me; Maciej Stepkowski)[https://linkedin.com/in/maciej-stepkowski-91b4b11b0] written at Warsaw School of Economics.

## Functionality

The application performs the following key functions:

1. **API Integration**: Connects to Allegro's API to fetch product listings and category information.

2. **Data Retrieval**: Searches for products based on user input, handling large datasets by paginating through results.

3. **Data Processing**: Analyzes the retrieved data, focusing on auctions with active bids and excluding certain price types (e.g., prices with delivery).

4. **Statistical Analysis**: Calculates various statistics such as the number of bids per category and the probability of purchase for each listing.

5. **Optimization**: Employs the Multi-Armed Bandit algorithm to determine the optimal listing price for each category. This algorithm balances exploration (trying different price points) and exploitation (leveraging known successful prices) to maximize the expected value of listings.

6. **Result Presentation**: Generates an HTML table of optimized results, showing the best listing prices for different categories and subcategories.

## Key Features

- Efficient handling of large datasets from Allegro API
- Category-based analysis and optimization
- Implementation of the Multi-Armed Bandit algorithm for price optimization
- User-friendly HTML output of results

## Technologies Used

- **Python**: The core programming language used for the application logic.
- **Django**: Web framework used for building the web application.
- **PostgreSQL**: Database system for storing search results and optimized data.
- **SUDS**: Library used for SOAP client functionality to interact with Allegro's API.
- **Pandas**: Used for data manipulation and analysis.
- **NumPy**: Utilized for numerical operations.
- **SimPy**: Employed in the Multi-Armed Bandit algorithm implementation.

## Multi-Armed Bandit Algorithm

The application uses the Multi-Armed Bandit algorithm to optimize listing prices. This approach treats each potential listing price as an "arm" of a bandit (a gambling machine) and attempts to find the optimal balance between:

- Exploring new price points to gather more data
- Exploiting known successful price points to maximize returns

This method is particularly effective in scenarios where the optimal choice may change over time, making it well-suited for dynamic e-commerce environments.

## Usage

Users can input search terms into the web interface. The application then:

1. Retrieves relevant listings from Allegro
2. Processes and analyzes the data
3. Applies the MAB algorithm to determine optimal pricing
4. Presents the results in an easy-to-understand format

The output includes recommended listing prices for different categories and subcategories, helping sellers optimize their pricing strategy on the Allegro platform.

## Setup and Installation

[Include instructions for setting up the project, including database configuration, API key setup, and any necessary environment variables.]

## Contributing

[Provide guidelines for how others can contribute to the project.]

## License

MIT