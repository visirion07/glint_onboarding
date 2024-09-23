import os
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

from dotenv import load_dotenv
#
# Load variables from .env file
load_dotenv()


def search_service(user_query):
    search_service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
    search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

    credential = AzureKeyCredential(search_api_key)
    semantic_config_name = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIG_NAME")  # Add your semantic configuration name here


    search_client = SearchClient(endpoint=search_service_endpoint, index_name=index_name, credential=credential)


    results = search_client.search(search_text=user_query, query_type=QueryType.SEMANTIC, semantic_configuration_name=semantic_config_name)


    documents = [doc for doc in results]

    return documents

docs = search_service("out-of-pocket costs")
print(docs)

for doc in docs:
    print("Document:")
    print(doc['chunk'])

# print to a file
with open('search_results.txt', 'w') as f:
    for doc in docs:
        f.write(f"{doc}\n")


def openai_response(prompt):
    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version="2024-02-01"
    )

    response = client.chat.completions.create(
        model="gpt35turbo16K", # model = "deployment_name"
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    print(response.choices[0].message.content)


openai_response("Hello, how can I use Azure OpenAI in my Python project? Can you help me with that?")