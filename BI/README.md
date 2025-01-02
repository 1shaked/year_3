# Business Intelligence Project

This repository contains a comprehensive Business Intelligence (BI) project that encompasses data extraction, transformation, loading (ETL), visualization, and dashboard deployment.

## Project Structure

The repository is organized into the following directories and files:

- **ETL/**: Contains scripts for data processing and graph generation.
  - *df_full.py*: Creates visual representations of the data, and do all the process on the data.
  - *preprocess.py*: Processes raw data into a structured format minimized only the needed operation.

- **dash_app.py**: Hosts the dashboard server for data visualization.

- **graphs/**: Stores all generated graphs for analysis.

- **data/**: Houses the raw and processed datasets.

- **dashboard.twbx**: Tableau file containing data visualizations.

## Getting Started

To explore and utilize this project, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/1shaked/year_3.git
   cd year_3/BI
   ```

2. **Set Up the Environment**:
   - Ensure you have Python installed.
   - Install the required packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Process the Data**:
   - Navigate to the ETL directory:
     ```bash
     cd ETL
     ```
   - Run the data processing script:
     ```bash
     python data_processing.py
     ```
    - link to the running bi site link: https://bi-course.onrender.com/

4. **Generate Graphs**:
   - Execute the graph generation script:
     ```bash
     python graph_generation.py
     ```

5. **Launch the Dashboard**:
   - Return to the main directory:
     ```bash
     cd ..
     ```
   - Start the server:
     ```bash
     python dash_app.py
     ```
   - Access the dashboard at `http://localhost:8050`.

6. **Explore Tableau Visualizations**:
   - Open `dashboard.twbx` in Tableau to interact with the data visualizations.

## Project Overview

This BI project is designed to provide insights through data processing and visualization. The ETL process ensures data is clean and structured, while the dashboard offers an interactive platform for data exploration.

## Contributing

Contributions are welcome. Please fork the repository and create a pull request with your enhancements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

Special thanks to all contributors and the open-source community for their invaluable support.

---

*Note: Ensure all scripts are executed in the correct sequence for optimal performance.* 