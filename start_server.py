# Install the openai package
# pip install openai

from openai import OpenAI
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import Activity
import ngrok

# Set up OpenAI API key
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")



class MyBot(ActivityHandler):
    
    def search_v_db(self, user_query):
        # Search the database for the user query
        return "Here are the search results for your query: " + user_query

    async def on_message_activity(self, turn_context: TurnContext):
        user_query = turn_context.activity.text
        

        prompt = self.search_v_db(user_query)
       

        # Call OpenAI API
        response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant specialized in generating professional LinkedIn posts."},
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

settings = BotFrameworkAdapterSettings(app_id="YOUR_APP_ID", app_password="YOUR_APP_PASSWORD")
adapter = BotFrameworkHttpAdapter(settings)

bot = MyBot()

async def messages(req):
    await adapter.process(req, bot.on_turn)

# Run the bot
import aiohttp
from aiohttp import web

# Define the GET handler
async def handle_get(request):
    return web.Response(text="hi")

app = web.Application()
app.router.add_post("/api/messages", messages)
app.router.add_get("/hi", handle_get)  # Add the GET route



if __name__ == "__main__":
    ngrok.set_auth_token("YOUR_NGROK")
    listener = ngrok.forward(3978)

# Output ngrok url to console
    print(f"Ingress established at {listener.url()}")
    web.run_app(app, host="localhost", port=3978)