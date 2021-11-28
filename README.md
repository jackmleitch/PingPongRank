# Ping Pong Ranking System
## Project Overview
* Created a ping pong ranking system for me and my friends to record all of our games.
* The ranking system is based on an altered version of the **ELO rating system** used in chess. 
* All match data is stored in a cloud-based **SQL database** and it is queried using the **BigQuery** python API.
* Built an **interactive app** for the rankings using Streamlit.

<p align="center">
<img src="https://github.com/jackmleitch/PingPongRank/blob/main/input/ranking.png" width="600" height="262">
</p>

## Motivation
My friends and I have a ping pong table in our garage and there are always hot debates on who is the best player. To end all arguments once and for all, I decided to make **Boise State's Official and Definitive Ping Pong Rankings**. Every game played can be added to the SQL database by using the Streamlit app, the rankings then update accordingly. This project was the perfect way to practice my SQL and python skills, with the added social bonus of being 'the creator' of the ranking system (which nicely trumps all ping pong-related arguments…).

## Code Used 
**Python Version:** 3.7 \
**Packages:** pandas, numpy, google-cloud-bigquery, streamlit, seaborn, matplotlib \
**Requirements:** ```pip install -r requirements.txt```

## How It Works
Inside the project hosted on GCP are three tables: current_rank, history, and ranking_history. 
* current_rank stores the current ranking of each player along with every player's total number of games played.
* history records the players of each match along with the winner of the match.
* ranking_history stores information about how each player's rank changes over time.

By querying these three tables in different ways, the app has the following features:
* The general ranking table 
* A lookup player stats section
* A head-to-head section where players can see how they match up against different opponents.
* Add player / Delete player / Remove last entered game functionality.

<p align="center">
<img src="https://github.com/jackmleitch/PingPongRank/blob/main/input/head2head.png" width="600" height="418">
</p>

## Productionization
In this step, I built a Streamlit app that is hosted publicly using Heroku. The app uses the BigQuery API to update ranking information automatically.
