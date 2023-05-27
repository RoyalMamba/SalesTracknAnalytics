# SalesTracknAnalytics

SalesTracknAnalytics is a web application built with Flask and React for tracking and analyzing sales data. It allows users to fetch and analyze sales data from a government website and provides insights and reports based on the data.

## Features

- **Sales Data Retrieval:** The application retrieves sales data from the government website using web scraping techniques. It fetches data for a specific month and year and processes it to create a structured dataframe.

- **Data Analysis:** The retrieved sales data is analyzed to generate reports and perform further operations. The application provides insights such as daily sales, total sales, sale count, and more.

- **Remaining Cards Calculation:** The application calculates the remaining cards based on the sales data. It fetches additional data from Excel files and calculates the probability of remaining cards for each source number.

- **Card Status Tracking:** The application tracks the status of the remaining cards by making requests to a government website. It determines whether a card is ported, taken, or pending.

- **Data Visualization:** The application presents the analyzed data and card status information in an interactive and user-friendly manner. It includes visualizations such as tables and charts to facilitate data interpretation.

## Deployment

To deploy the SalesTracknAnalytics project, follow these steps:

1. Clone the repository: `git clone https://github.com/RoyalMamba/SalesTracknAnalytics.git`

2. Install the necessary dependencies for the Flask backend and frontend.

3. Run the Flask backend: `python main.py`

4. Access the application through a web browser at `http://localhost:8080`.

Note: Make sure to configure the necessary paths in the code according to your system setup.

## Contributing

Contributions to SalesTracknAnalytics are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

## Acknowledgments

The SalesTracknAnalytics project was inspired by the need to track and analyze sales data efficiently. Thanks to the open-source community for providing helpful libraries and frameworks used in this project.

