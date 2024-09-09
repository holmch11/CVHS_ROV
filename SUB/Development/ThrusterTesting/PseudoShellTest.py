

done = False

print('CVHS PWM Testing Shell:')
print('\t- Please enter an integer [0, 100] to set the duty cycle')
print('\t- "freq,####" changes the default frequency')
print('\t- Enter "exit" to quit')
print('---------------------------------------------------------------------------------')

while not done:
	rslt = input('\t# ')

	splitRslt = rslt.split(',')

	if splitRslt[0] == 'exit':
		done = True
		continue

	elif splitRslt[1] == 'freq':
		print('freq')
	else:
		try:
			intRslt = int(rslt)

		except:
			print(f'\t\t{rslt} is not a valid integer. please ')

		print(f'\t\tType: {type(rslt)}')