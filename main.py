from bot import GpuBot

if __name__ == '__main__':
	bot = GpuBot('settings.json')
	bot.run()
	bot.join()
	print "Goodbye."
