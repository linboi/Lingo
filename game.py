import random
import time

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


def main():
	round()

if __name__ == '__main__':
	main()