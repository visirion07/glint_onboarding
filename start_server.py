# Install the openai package
# pip install openai

from azure.identity import ManagedIdentityCredential, DefaultAzureCredential, AzureCliCredential, CertificateCredential
from msal import ConfidentialClientApplication
from botbuilder.integration.aiohttp import BotFrameworkHttpAdapter
from msrestazure.azure_active_directory import MSIAuthentication
from openai import OpenAI
from botbuilder.core import ActivityHandler, TurnContext, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
import ngrok

import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("YOUR_OPENAI_API_KEY"))

managed_identity_client_id = os.getenv("MANAGED_IDENTITY_CLIENT_ID")
# credential = ManagedIdentityCredential(client_id=managed_identity_client_id)
# credential = MSIAuthentication()
# credential = AzureCliCredential()
client_id = os.getenv("BOT_APP_ID")
# tenant_id = os.getenv("BOT_TENANT_ID")
# certificate_path = "vgbot-keyvaultlocal-local-20240920.pfx"

# credential = CertificateCredential(tenant_id=tenant_id, client_id=client_id, certificate_path=certificate_path)

# # Function to get access token using Managed Identity
def get_access_token():
    tbr = "Bearer " + credential.get_token("https://api.botframework.com/.default").token
    return tbr


# # Custom Bot Adapter that authenticates using Managed Identity
class CustomBotFrameworkHttpAdapter(BotFrameworkHttpAdapter):
    async def authenticate_request(self, req):
        token = get_access_token()
        req.headers['Authorization'] = token


class MyBot(ActivityHandler):
    
    def search_v_db(self, user_query):
        # Search the database for the user query
        
        return "Here are the search results for your query: " + user_query

    async def on_message_activity(self, turn_context: TurnContext):
        user_query = turn_context.activity.text
        

        prompt = self.search_v_db(user_query)
       

        # Call OpenAI API
        response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Bot is searching the database for the user query"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
        
        # Extract the response text
        openai_response =  response.choices[0].message.content
        
        # Send the response back to the user
        await turn_context.send_activity(f"OpenAI says: {openai_response}")

# Set up the bot and run it
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.integration.aiohttp import BotFrameworkHttpClient, BotFrameworkHttpAdapter

# settings = BotFrameworkAdapterSettings(app_id=os.getenv("YOUR_APP_ID"), app_password=os.getenv("YOUR_APP_PASSWORD"))
settings = BotFrameworkAdapterSettings(app_id=os.getenv("BOT_APP_ID"))

adapter = BotFrameworkHttpAdapter(settings)

# adapter = CustomBotFrameworkHttpAdapter(settings)

bot = MyBot()

async def messages(req):
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    auth_header2 = get_access_token()
    # print(activity)
    print("AUTH HEADER", auth_header)
    print("AUTH HEADER2", auth_header2)
    print("====================")
    await adapter.process_activity(activity, auth_header, bot.on_turn)
    # await adapter.process_activity(activity, bot.on_turn)

# Run the bot
import aiohttp
from aiohttp import web

# Define the GET handler
async def handle_get(request):
    res = "Hello, world!"
    return web.Response(text=res)

app = web.Application()
app.router.add_post("/api/messages", messages)
app.router.add_get("/hi", handle_get)  # Add the GET route



if __name__ == "__main__":
    ngrok.set_auth_token(os.getenv("YOUR_NGROK"))
    listener = ngrok.forward(3978)

# Output ngrok url to console
    print(f"Ingress established at {listener.url()}")
    web.run_app(app, host="localhost", port=3978)