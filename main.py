import discord
import os
import datetime
import asyncio
from dotenv import load_dotenv
import csv

eventList = []
messageList = []
load_dotenv()
client = discord.Client(intents=discord.Intents.default())
token = os.getenv('token')
admin = int(os.getenv('admin'))
event_running = False

class event:
    def __init__(self, post_date, end_date, message):
        self.post_date = post_date
        self.end_date = end_date
        self.message = message
        self.post_sent = False

async def process_events():
    channel = client.get_channel(int(os.getenv('channel')))
    global event_running
    while(True):
        await asyncio.sleep(5)
        now = datetime.datetime.now()
        for i in range(len(eventList)):
            if (now>eventList[i].post_date) and (eventList[i].post_sent==False):
                messageList.clear()
                await channel.send(eventList[i].message.replace("\\n", "\n"))
                eventList[i].post_sent = True
                event_running = True
            if (now>eventList[i].end_date):
                await create_attendance()
                del eventList[i]
                messageList.clear()
                event_running = False


def csv_to_list(file_name,list):
    with open(file_name, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            list.append([row['name'],""])
    return list

def list_to_csv(file_path, list):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(list)

async def create_attendance():
    data = []
    data = csv_to_list("template.csv",data)
    for i in (data):
        for j in messageList:
            if j.author.id == int(i[0]):
                i[2] = i[2] + "[" + j.content + "]"
    file_name = 'attendance/'+ datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv"
    list_to_csv(file_name,data)
    user = await client.fetch_user(admin)
    with open(file_name, "rb") as file:
        print("done")
        await user.send("Here's the file you requested:", file=discord.File(file, "example.txt"))
        print("done")

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await process_events()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if isinstance(message.channel, discord.channel.DMChannel):
        if message.author.id == admin:
            # creates event when dm'd message of format -create_event yyyy/MM/dd/hh/mm,yyyy/MM/dd/hh/mm,message
            if "-create_event " in message.content:
                try:
                    event_command=(message.content).replace("-create_event ", "").split(",")
                    post_date = event_command[0].split('/')
                    end_date = event_command[1].split('/')
                    eventList.append(event(datetime.datetime(int(post_date[0]),int(post_date[1]),int(post_date[2]),int(post_date[3]),int(post_date[4])),datetime.datetime(int(end_date[0]),int(end_date[1]),int(end_date[2]),int(end_date[3]),int(end_date[4])),event_command[2]))
                    await message.author.send('Event sceduled')
                except Exception as e:
                    print(e)
                    await message.author.send("Error: -create_event command improperly formatted")
            if "-print_events" in message.content:
                msg="Events are as follows:\n"
                for i in range(len(eventList)):
                    msg=msg+str(i+1)+": "+eventList[i].post_date.strftime("%Y-%m-%d %H:%M:%S")+ " | " + eventList[i].post_date.strftime("%Y-%m-%d %H:%M:%S")+"\n"
                await message.author.send(msg)
            #removes event at index specified by -print events formatted -remove_event index
            if "-remove_event" in message.content:
                try:
                    index=int((message.content).replace("-remove_event ", ""))
                    del eventList[index-1]
                    await message.author.send("Event at index "+str(index)+" has been removed")
                except:
                    await message.author.send("Error: -remove_event command improperly formatted or out of range")
        else:
            if event_running:
                messageList.append(message)
                await message.author.send("Your response has been recorded")
            else:
                await message.author.send("There is no event currently running")
        with open("message_log.txt", "a") as file:
            file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" | "+ str(message.author)+ " | "+str(message.content)+"\n")
            file.close()
client.run(token)