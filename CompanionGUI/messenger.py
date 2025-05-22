import discord

# TOKEN = "YOUR TOKEN HERE"
# ID = "YOUR ID HERE"

class Messenger(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        # if (message.author != self.user): 
        print('Message from {0.author}: {0.content}'.format(message))

    async def send_msg(self, usr, msg):
        global ID
        user = discord.utils.get(self.users, name=usr)
        channel = self.get_channel(ID)
        await channel.send(f'{user.mention}: {msg}')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

msg_client = Messenger(intents=intents)
msg_client.run(TOKEN)