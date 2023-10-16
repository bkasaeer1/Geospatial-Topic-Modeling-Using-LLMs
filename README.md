# Geospatial-NLP-Using-LLMs
This reposotory includes a framework to scrape public source geospatial text, perform NLP tasks to extract geospatial context, and visualize the final geographically analyzed results as a web application embeded withi an ARCGIS Storymap within the ARCGIS Online platform.  

# Use Case Project: Geospatial Tweet Analysis

This repository contains a set of Python scripts and notebooks for a geospatial analysis project focused on collecting and analyzing COVID-19-related tweets. The project consists of several steps, each addressing a specific aspect of the analysis.

## Step 1: Geographic Buffer Generation

The [GeographicBufferGenerator.py](GeographicBufferGenerator.py) script contains functions for creating Esri file geodatabases and generating buffer areas for cities and states. It utilizes the Geopandas library to read and process geospatial data, calculates buffer sizes, and converts this data into an Esri file geodatabase. The code is used to create buffers around the most populous cities in the US and state centroids for collecting tweets at both city and state levels. The main part of the code executes these functions and measures the processing time. This code is intended for geospatial analysis and data collection, particularly for tweets, allowing data collection within specific buffer areas.

## Step 2: Collecting Data from Various Geographic Locations

The [TweetParser.py](TweetParser.py) code involves Python scripts that scrape Twitter data using the snscrape and Geopandas libraries. It starts by specifying parameters such as search content (keywords), start and end dates for tweet collection, and the file geodatabase name. The code defines functions to create an Esri file geodatabase, generate search center points for tweets, and scrape tweets from these geographic locations based on specified content and date criteria. The collected tweets are stored in a pandas dataframe and saved as a CSV file. The code also measures the processing time and provides information about the process's progress. This code is intended for collecting Twitter data related to a specific subject (e.g., COVID-19) within specific geographic areas.

## Step 3: Sentiment Analysis on the Collected Data

The [SentimentAnalysis.ipynb](SentimentAnalysis.ipynb) notebook is part of a geospatial data analysis project that involves sentiment analysis of COVID-19-related tweets during the Trump and Biden administrations. It imports various libraries for data processing and visualization, cleans the collected tweets, calculates sentiment scores using VADER, and then analyzes and visualizes the sentiment trends in U.S. states. The code creates a geospatial representation of states, analyzes changes in sentiment scores, and provides insights into the distribution of negative and positive tweets during the two administrations. Additionally, it identifies representative tweets for further understanding of sentiment patterns at the state level. This project offers a comprehensive view of how public sentiment regarding the pandemic has evolved geographically over time, providing valuable insights for understanding the social impact of the COVID-19 crisis in the United States.

## Step 4: Topic Modeling on the Collected Data

The [TopicModeling.ipynb](TopicModeling.ipynb) notebook is also part of a geospatial data analysis project focused on the analysis of COVID-19-related tweets. It aims to determine suitable parameters for topic modeling using Uniform Manifold Approximation and Projection (UMAP) and Hierarchical Density-Based Spatial Clustering of Applications with Noise (HDBSCAN) on textual data. The code imports various libraries for data processing, visualization, and natural language processing, sets up the environment, and specifies output directories. It defines a function for text preprocessing, tokenizing, lowercasing, and lemmatization to prepare the text documents for analysis. The code involves cleaning and preprocessing the collected tweets, separating them based on conditions like sentiment and presidential association. It performs dimensionality reduction using UMAP on Large Language Model (LLM) embeddings and applies HDBSCAN for clustering. It visualizes clusters in a 2D space and generates topics using the BERTopic model. The code ultimately transfers results into a geospatial context, creating an Esri file geodatabase, exporting geographic data to a feature layer for geospatial visualization in ARCGIS Online, and facilitating geospatial analysis and visualization of tweet data.

## Step 5: Visualize the Geospatial Results

In this step, results of the analysis are visualized in an ARCGIS [Storymap](https://storymaps.arcgis.com/stories/f7cf855fc55040da9fdae2a3b672a313) within ARCGIS Online. The goal is to demonstrate the power of GIS tools in visualizing meaningful insights from the NLP project into an interactive map that allows users to zoom to their geographic level of interest and review the results for that area.

Feel free to explore the individual scripts and notebooks for more detailed information and to replicate the geospatial tweet analysis.

