from random import randint

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

def round():
	with open('words.txt', 'r') as file:
		lines = file.readlines()
	sol = lines[(randint(0, len(lines)))]
	sol = sol[:-1]
	print(sol[0] + "  " + "_  "*(len(sol)-1))
	playing = True
	while playing:
		badInput = True
		while badInput:
			guess = input()
			if len(guess) == len(sol):
				badInput = False
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
		print(prompt)
			

def prune():
	def pruneCondition(line):
		for c in line:
				if c != '\n' and (c < 'a' or c > 'z'):
					return True
		return False
	linesNew = []
	with open('words.txt', 'r') as file:
		lines = file.readlines()
		for line in lines:
			if not pruneCondition(line):
				linesNew.append(line)
	with open('wordsNew.txt', 'w') as newFile:
		newFile.writelines(linesNew)


def main():
	round()

if __name__ == '__main__':
	main()