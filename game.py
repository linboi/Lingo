import random
import time
import discord
from config import token

def checkLetters(guess, solution):
	if len(solution) != len(guess):
		return -1 # undefined behaviour

	result = [2] + [0]*(len(solution)-1) # 0 = no match, 1 = wrong position, 2 = match
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
			
async def discordRound(client, channel, author):
	with open('words.txt', 'r') as file:
		lines = file.readlines()
	sol = lines[(random.randint(0, len(lines)))]
	sol = sol[:-1]
	await channel.send(("```" + sol[0] + "  " + "_  "*(len(sol)-1) + "```"))
	playing = True

	def check(message):
		if message.author.id == author and len(message.content) == len(sol):
			return True
		return False
	while playing:
		message = await client.wait_for('message', check=check)
		print(checkLetters(message.content, sol))


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
		print('Logged on as {0}!'.format(self.user))

	async def on_message(self, message):
		if message.author.bot:
			return
		if(message.content.lower().startswith("!lingo") or message.content.lower().startswith("!wordle")):
			await discordRound(self, message.channel, message.author.id)

def main():
	intents = discord.Intents.default()
	intents.members = True

	client = MyClient(intents=intents)

	client.run(token)

if __name__ == '__main__':
	main()