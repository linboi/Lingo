import random
import time
import discord
from config import token
import sys
import string

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
	sol = lines[(random.randint(0, len(lines)))]
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
			
async def discordRound(client, channel, author, lines, possibleWords, seed=None):
	wasChosen = True
	if(seed==None):
		random.seed(time.time())
		seed = random.randrange(sys.maxsize)
		wasChosen = False
	random.seed(seed)
	print("Started round with: " + str(author.name))
	attemptedLetters = {}
	for c in string.ascii_lowercase:
		attemptedLetters[c] = False
	sol = lines[(random.randint(0, len(lines)))]
	sol = sol[:-1]
	foundLetters = []
	foundLetters.append(sol[0])
	for i in range(len(sol)-1):
		foundLetters.append("\\_")
	
	await channel.send(("" + sol[0] + "  " + "\\_  "*(len(sol)-1) + "\nSeed: " + str(seed) + ""))
	playing = True
	atts = 0
	attemptGraph = ""
	def check(message):
		if message.author.id == author.id and len(message.content) == len(sol):
			return True
		return False

	start = time.time()
	while playing:
		response = ""
		badInput = True
		while badInput:
			guess = await client.wait_for('message', check=check)
			guess = guess.content.lower()
			if len(guess) == len(sol) and (guess.upper() + '\n') in possibleWords:
				badInput = False
				atts += 1
				response += " "
				for c in guess:
					if c not in sol:
						attemptedLetters[c] = True
					if c >= 'a' and c <= 'z':
						response += emojiLetters[c] + " "
				response += ("\n")
			else:
				await channel.send("Wrong word length or not a word idk")
		att = checkLetters(guess, sol)
		correctLetters = ""
		for num in att:
			if num == 2:
				correctLetters += '🟩 '
			if num == 1:
				correctLetters += '🟨 '
			if num == 0:
				correctLetters += '🟥 '
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
			endMessage = "Attempts: " + str(atts) + "\n" + attemptGraph + "\nSeed: " + str(seed) + " Was seeded: " + str(wasChosen)
			await channel.send("You win\n")
			await channel.send("```" + endMessage + "\nYour time: " + str(time.time()-start) + "```")
			return True
		#elif 
		response += "\n"
		for c in attemptedLetters:
			if not attemptedLetters[c]:
				response += c
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
	with open('bigshmoke.txt', 'w') as newFile:
		newFile.writelines(linesNew)


class MyClient(discord.Client):
	async def on_ready(self):
		with open('words.txt', 'r') as file:
			self.lines = file.readlines()
		with open('scrabbleWords.txt', 'r') as file:
			self.possibleWords = file.readlines()
		print('Logged on as {0}!'.format(self.user))

	async def on_message(self, message):
		if message.author.bot:
			return
		if(message.content.lower().startswith("!lingo") or message.content.lower().startswith("!wordle")):
			if len(message.content.split()) == 1:
				await discordRound(self, message.channel, message.author, self.lines, self.possibleWords)
			else:
				parts = message.content.split()
				await discordRound(self, message.channel, message.author, self.lines, self.possibleWords, seed=int(parts[1]))
				

def main():
	intents = discord.Intents.default()
	intents.members = True

	client = MyClient(intents=intents)

	client.run(token)

if __name__ == '__main__':
	main()