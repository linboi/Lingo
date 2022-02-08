import random
import time
import discord
from config import token
import sys
import string
import asyncio
import threading

emojiLetters = { 
"a":"🇦",
"b":"🇧",
"c":"🇨",
"d":"🇩",
"e":"🇪",
"f":"🇫",
"g":"🇬",
"h":"🇭",
"i":"🇮",
"j":"🇯",
"k":"🇰",
"l":"🇱",
"m":"🇲",
"n":"🇳",
"o":"🇴",
"p":"🇵",
"q":"🇶",
"r":"🇷",
"s":"🇸",
"t":"🇹",
"u":"🇺",
"v":"🇻",
"w":"🇼",
"x":"🇽",
"y":"🇾",
"z":"🇿"
}

def checkLetters(guess, solution):
	if len(solution) != len(guess):
		return -1 # undefined behaviour

	guess = guess.lower()
	result = [0]*(len(solution)) # 0 = no match, 1 = wrong position, 2 = match
	unmatchedLetters = []
	for i in range(len(solution)):
		if guess[i] == solution[i]:
			result[i] = 2
		else:
			unmatchedLetters.append(solution[i])
	# All matches must be found before wrong positions can be recorded
	for i in range(len(solution)):
		if result[i] != 2 and guess[i] in unmatchedLetters:
			result[i] = 1
			unmatchedLetters.remove(guess[i])
	return result

def round(seed=213):
	#random.seed(seed)
	start = time.time()
	with open('words.txt', 'r') as file:
		lines = file.readlines()
	sol = lines[(random.randint(0, len(lines)))].lower()
	sol = sol[:-1]
	print(sol[0] + "  " + "_  "*(len(sol)-1))
	playing = True
	atts = 0
	while playing:
		badInput = True
		while badInput:
			guess = input()
			if len(guess) == len(sol):
				badInput = False
				atts += 1
				print(" " + "  ".join(list(guess)))
			else:
				print("Wrong word length")
		att = checkLetters(guess, sol)
		prompt = " "
		print(att)
		for i in range(len(sol)):
			if att[i] == 2:
				prompt += sol[i] + "  "
			else:
				prompt += "_  "

		if len(set(att))==1:
			print("You win")
			print("Your time: ", (time.time()-start))
			return True
		#elif 
		print(prompt)
			
async def lingoRound(client, channel, author, seed=None, mode=0, timed=None):
	wasChosen = True
	if(seed==None):
		random.seed(time.time())
		seed = random.randrange(sys.maxsize)
		wasChosen = False
	random.seed(seed)
	print("Started round with: " + str(author.name))
	if mode == 2:
		sol = random.choice(client.possibleWords).lower()
	elif mode == 1:
		sol = random.choice(client.mediumDict).lower()
	else:
		sol = random.choice(client.lines).lower()
	sol = sol[:-1]
	await channel.send("Seed: " + str(seed))
	atts, attemptGraph, finishTime = await playRound(client, channel, author, sol, timed=timed)
	endMessage = "Attempts: " + str(atts) + "\n" + attemptGraph + "\nSeed: " + str(seed) + " Was seeded: " + str(wasChosen)
	await channel.send("You win\n")
	await channel.send("```" + endMessage + "\nYour time: " + "{:.2f}".format(finishTime) + " seconds ```")

async def dailyRound(client, channel, author, seed, mode=0, timed=None):
	if time.strftime("%a%d%b%Y") != client.date:
		client.date = time.strftime("%a%d%b%Y")
		client.leaderboard = []
		client.dailyInProgress = []
	else:
		if author.id in client.dailyInProgress:
			return
		for record in client.leaderboard:
			if record[0] == author.name:
				await channel.send("Daily already complete")
				return
	client.dailyInProgress.append(author.id)
	random.seed(seed)
	print("Started daily round with: " + str(author.name))
	sol = random.choice(client.lines).lower()
	sol = sol[:-1]
	atts, attemptGraph, finishTime = await playRound(client, author, author, sol)
	await author.send("You win\n")
	endMessage = "Attempts: " + str(atts) + "\n" + attemptGraph + "\nDaily " + time.strftime("%a, %d %b, %Y")
	#await channel.send("```" + endMessage + "\nYour time: " + "{:.2f}".format(finishTime) + " seconds ```")
	await author.send("```" + endMessage + "\nYour time: " + "{:.2f}".format(finishTime) + " seconds ```")
	if time.strftime("%a%d%b%Y") == client.date:
		client.leaderboard.append((author.name, (atts*100+finishTime), atts, finishTime))
		await displayLeaderboard(client, channel)
	else:
		await author.send("Midnight passed during round, score not added to leaderboard")

async def displayLeaderboard(client, channel):
	def byScore(elem):
		return elem[1]
	client.leaderboard.sort(key=byScore)
	message = "```"
	if len(client.leaderboard) == 0:
		message += " "
	for idx, record in enumerate(client.leaderboard):
		message += str(idx+1) + ". " + record[0].ljust(20, " ") + "att: " + str(record[2]) + ", time: " + "{:.1f}s".format(record[3]) + "\n"
	message += "```"
	await channel.send(message)

async def playRound(client, channel, author, sol, timed=None):
	attemptedLetters = {}
	for c in string.ascii_lowercase:
		attemptedLetters[c] = False
	foundLetters = []
	foundLetters.append(sol[0])
	for i in range(len(sol)-1):
		foundLetters.append("\\_")
	
	await channel.send((sol[0] + "  " + "\\_  "*(len(sol)-1)))
	playing = True
	atts = 0
	attemptGraph = ""
	def check(message):
		if message.author.id == author.id and (len(message.content) == len(sol) or message.content.lower().startswith("!quit")):
			return True
		return False

	keyboardLineOne = "qwertyuiop"
	keyboardLineTwo = "asdfghjkl"
	keyboardLineThree = "zxcvbnm"
	start = time.time()
	while playing:
		response = ""
		badInput = True
		while badInput:
			try:
				#if timed != None:
				#	t = threading.Thread(target=asyncio.run, args=(testEdit(client, channel),))
				#	t.start()
				guess = await client.wait_for('message', check=check, timeout=timed)
			except asyncio.TimeoutError:
				await channel.send("Timeout occurred")
				return
			else:
				guess = guess.content.lower()
				if guess == "!quit":
					await channel.send("Word is: " + str(sol))
					return False
				if len(guess) == len(sol) and (guess.lower() + '\n') in client.possibleWords:
					badInput = False
					atts += 1
					response += " "
					for c in guess:
						if c >= 'a' and c <= 'z':
							response += emojiLetters[c] + " "
					response += ("\n")
				else:
					await channel.send("Wrong word length or not a word idk")
		att = checkLetters(guess, sol)
		correctLetters = ""
		for idx, num in enumerate(att):
			if num == 2:
				correctLetters += '🟩 '
			if num == 1:
				correctLetters += '🟨 '
			if num == 0:
				correctLetters += '🟥 '
				attemptedLetters[guess[idx]] = True
		response += correctLetters + "\n"
		attemptGraph += correctLetters + "\n"
		won = True
		for i in range(len(sol)):
			if att[i] == 2:
				foundLetters[i] = sol[i]
			else:
				won = False

		for c in foundLetters:
			response += c + "    "
		if won:
			return (atts, attemptGraph, (time.time()-start))
			#endMessage = "Attempts: " + str(atts) + "\n" + attemptGraph + "\nSeed: " + str(seed) + " Was seeded: " + str(wasChosen)
			#await channel.send("You win\n")
			#await channel.send("```" + endMessage + "\nYour time: " + str(time.time()-start) + "```")
			#return True
		#elif 
		response += "\n```"
		for c in keyboardLineOne:
			if not attemptedLetters[c]:
				response += c + " "
			else:
				response += "  "
		response += "\n "
		for c in keyboardLineTwo:
			if not attemptedLetters[c]:
				response += c + " "
			else:
				response += "  "
		response += "\n  "
		for c in keyboardLineThree:
			if not attemptedLetters[c]:
				response += c + " "
			else:
				response += "  "
		response += "```"
		
		await channel.send("" + response + "")


def prune():
	def keepCondition(line):
		return (len(line) < 8 and len(line) > 4)
	linesNew = []
	with open('wordlist.txt', 'r') as file:
		lines = file.readlines()
		for line in lines:
			if keepCondition(line):
				linesNew.append(line)
	with open('newWords.txt', 'w') as newFile:
		newFile.writelines(linesNew)


class MyClient(discord.Client):
	async def on_ready(self):
		with open('words.txt', 'r') as file:
			self.lines = file.readlines()
		with open('scrabbleWords.txt', 'r') as file:
			self.possibleWords = file.readlines()
		with open('wordsShort.txt', 'r') as file:
			self.mediumDict = file.readlines()
		self.date = time.strftime("%a%d%b%Y")
		self.leaderboard = []
		self.dailyInProgress = []
		print('Logged on as {0}!'.format(self.user))


	async def on_message(self, message):
		if message.author.bot:
			return
		if(message.content.lower().startswith("!lingo") or message.content.lower().startswith("!wordle")):
			if len(message.content.split()) == 1:
				await lingoRound(self, message.channel, message.author)
			else:
				parts = message.content.split()
				await lingoRound(self, message.channel, message.author, seed=int(parts[1]))
		if(message.content.lower().startswith("!dingo") or message.content.lower().startswith("!abecedarian")):
			if len(message.content.split()) == 1:
				await lingoRound(self, message.channel, message.author, mode=2)
			else:
				parts = message.content.split()
				await lingoRound(self, message.channel, message.author, seed=int(parts[1]), mode=2)
		if(message.content.lower().startswith("!mingo")):
			if len(message.content.split()) == 1:
				await lingoRound(self, message.channel, message.author, mode=1)
			else:
				parts = message.content.split()
				await lingoRound(self, message.channel, message.author, seed=int(parts[1]), mode=1)
		if(message.content.lower().startswith("!tingo")):
			if len(message.content.split()) == 1:
				await lingoRound(self, message.channel, message.author, mode=0, timed=30)
			else:
				parts = message.content.split()
				await lingoRound(self, message.channel, message.author, seed=int(parts[1]), mode=0, timed=30)
		if(message.content.lower().startswith("!daily")):
			await dailyRound(self, message.channel, message.author, seed=time.strftime("%a%d%b%Y"))
		if(message.content.lower().startswith("!lb") or message.content.lower().startswith("!leaderboard")):
			await displayLeaderboard(self, message.channel)
		#if(message.content.lower().startswith("!test")):
		#	await testEdit(self, message.channel)
				
async def testEdit(client, channel):
	n = 15
	msg = await channel.send('🟥'*n)
	while n > 0:
		await msg.edit(content=('🟥'*n))
		n -= 1
		await asyncio.sleep(1)

def main():
	intents = discord.Intents.default()
	intents.members = True

	client = MyClient(intents=intents)

	client.run(token)

if __name__ == '__main__':
	main()