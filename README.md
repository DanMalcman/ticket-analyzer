# Vivenu & Fortress Data Analysis Tool

This script takes ticket data from the Vivenu ticketing system and entry logs from the Fortress access control system for the same event, and analyzes the combined data to provide insights that event managers frequently request. The analysis is customized based on how Leaan LTD typically sets up their events. The application has been deployed as a web app using Streamlit.

## Features

- Processes both Vivenu ticket exports and Fortress entry logs
- Analyzes attendance data for regular tickets and subscription tickets
- Provides key metrics including attendance counts and no-show rates
- Generates downloadable reports in CSV format with UTF-8-sig encoding for proper Hebrew text support
- Offers a user-friendly interface for event managers

## Usage

1. Upload your Vivenu ticket export file (CSV or Excel)
2. Upload your Fortress entry log file (CSV or Excel)
3. View the generated analysis and metrics
4. Download specific data segments or the complete analysis as needed

## Requirements

- Vivenu export must include: barcode, ticketName, origin columns
- Fortress export must include: Barcode column

## Deployment

This application is deployed on Streamlit.io and can be accessed by authorized Leaan LTD event managers.

## Link for the app
https://ticket-analyzer-vivenu-fortress.streamlit.app/
