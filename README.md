# Submission Analysis Data Dicoding

This repository contains the project for Data Analysis using Python and Machine Learning, specifically designed for the Dicoding submission. The project involves data analysis, machine learning modeling, and visualization. It uses libraries such as Streamlit, Pandas, Matplotlib, Seaborn, and Plotly to create an interactive dashboard and generate useful insights.

## Table of Contents

- [Project Description](#project-description)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [License](#license)

## Project Description

This project applies various data analysis and machine learning techniques to explore and analyze a dataset. It includes:
- Data cleaning and preprocessing
- Exploratory Data Analysis (EDA)
- Data visualization
- Machine learning model development
- Streamlit dashboard for interactive data exploration

The purpose is to create an easy-to-use application that helps users gain insights from data using machine learning models.

## Technologies Used

- **Python**: The main programming language used.
- **Streamlit**: For building an interactive web application.
- **Pandas**: For data manipulation and analysis.
- **Matplotlib**: For basic data visualization.
- **Seaborn**: For advanced data visualization.
- **Plotly**: For creating interactive plots.
- **Scikit-learn**: For machine learning algorithms.

## Installation

To run this project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Trancend1/submission-analysis-data-dicoding.git
   cd submission-analysis-data-dicoding
2. Create a virtual environment:
   
   conda create --name submission

3. Activate the environment

  conda activate submission

4. Install the required dependencies

   pip install -r requirements.txt

## File Structure
The repository has the following structure:

submission/
│
├── dashboard/
│   ├── main_data.csv        
│   └── dashboard.py         
│
├── data/
│   ├── data_1.csv           
│   └── data_2.csv 
│   ├── data_3.csv           
│   └── data_4.csv
│   ├── data_5.csv           
│   └── data_6.csv
│   ├── data_7.csv           
│   └── data_8.csv
│
├── Proyek_Analysis_Data_Farhan_Alamsyah.ipynb 
├── README.md                
├── requirements.txt         
└── url.txt                  

## Usage
Once the environment is set up, you can run the Streamlit dashboard by using the following command:

streamlit run dashboard/dashboard.py

This will start a local web server and open the dashboard in your browser.

