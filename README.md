# Good News API

## Checking out the API 
If you would simply like to take a look at the API, please visit https://good-news-capstone.herokuapp.com/. For instructions on how to set up the project on your machine, please keep reading.

## News API Key
  1. Go to https://newsapi.org/ and follow the instructions to create an account to get an API key.

## Azure API Key
1. Sign up for a free account at https://azure.microsoft.com/en-us/services/cognitive-services/text-analytics/.
2. Create a new resource from your portal by clicking on **Create a resource**. Then go to the **AI + Machine Learning** tab and navigate to **Text Analytics** and fill in the information (name, region, resource group, pricing tier).
3. After completing this step, you should be able to go to your resource and follow the instructions on the **Quick Start** page to get started with making API requests. There is also a tab called **Keys and Endpoints** that has your API key and endpoint url. The following link from the documentation has instructions for how to send a request for sentiment analysis:
https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-sentiment-analysis?tabs=version-3
4. Once you have your endpoint url and API key, go to the ```news.py``` file and change the endpoint url in the ```process_news``` method to the endpoint url obtained from creating your own text analytics resource.

## Firebase Project Setup 
1. Go to https://console.firebase.google.com/ and click on **Add Project** and follow on screen instructions to create a project. 
2. Once the project has been created, go to **Project Settings** and add a web app to your project.
3. After adding a web app to your project, go to the **Service Accounts** tab, select Python and then click on **Generate new private key**. These keys will be used to create the [Python .env file](#Create-an-env-file).

## Create Firestore Database 
1. Go to the Cloud Firestore tab and click on **Create Database**.
2. Start in test mode and select your region (note: it may already be selected for you).

## Enable Firebase Authentication 
1. Go to the **Authentication** tab and click on **Get Started**.
2. Go to the **Sign-in method** tab and **enable Google sign in**. 

## Get the code

```shell=bash
# Clone the code
git clone https://github.com/roshni-patel/good-news-api.git 

# Go into the code folder
cd good-news-api

# Setup the virtual environment and install the requirements 
python3 -m venv venv
pip install -r requirements.txt 
```

## Create an env file
Create an `.env` file in the `good-news-api` folder that looks like this:
```shell=sh
X_API_KEY="Insert News API key here"
OCP_APIM_SUBSCRIPTION_KEY="Insert Text Analytics API key here"
FIREBASE_TYPE=service_account
FIREBASE_PRIVATE_KEY_ID="Insert private key id here"
FIREBASE_PRIVATE_KEY="Insert private key here"
FIREBASE_CLIENT_EMAIL="Insert email here"
FIREBASE_CLIENT_ID="Insert clientid here"
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_PROJECT_ID="Insert project-id here"
FIREBASE_CLIENT="Insert client here"
```

## Running Locally 
* Start the Python server within your virtual environment using python app.py and it should be available on http://localhost:5000 


## Deploying to Heroku
* Follow these instructions to deploy the Python Flask app to Heroku: https://devcenter.heroku.com/articles/getting-started-with-python

## Setting up the frontend
* The frontend connected to this API can be found at https://github.com/roshni-patel/good-news. 
* Once you've completed the backend setup here, please follow along with the instructions included in the frontend repository if you would like to run the Good News app on your machine. 