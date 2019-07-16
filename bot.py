import webbrowser
import requests
import bs4
import urllib2
import newegg
import threading
import json
import re
from sys import platform
if platform == "linux" or platform == "linux2" or platform == "darwin": # Mac & Linux
    	import pygame 
elif platform == "win32":
    	import winsound
import counter
import time
from urlparse import urlparse
import util

class GpuBot:

	def __init__(self, filename):
		self.settings = json.load(open(filename))
		self.counter = counter.Counter(self.settings['counter'])
		self.threads, self.link_map = [], {}
		util.print_header("Settings:", json.dumps(self.settings, indent=2))

	def run(self):
		gpus_lst = [(gpu, use) for gpu, use in self.settings['gpus'].iteritems() if use]
		for gpu, use in gpus_lst[1:]:
			t = threading.Thread(target=self.monitor_loop, args=(gpu,))
			t.daemon=True
			t.start()
			self.threads.append(t)
		
		gc = threading.Thread(target=self.run_gc)
		gc.daemon=True
		gc.start()

		self.monitor_loop(gpus_lst[0][0])

	def monitor_loop(self, gpu):
		while True:
			self.monitor(gpu)
			time.sleep(self.settings['check_interval_sec'])
	
	def monitor(self, gpu):
		soup = bs4.BeautifulSoup(urllib2.urlopen("https://www.nowinstock.net/computers/videocards/" + gpu), 'html.parser')

		# <div id="data">
		# <table width="610">
		# 		<tr bgcolor="#CCCCCC">
		# 			<th id="nameh">Name</th>
		# 			<th width="90">Status<span style="vertical-align:super; font-size:8px;">1</span></th>
		# 			<th width="65">Last Price<span style="vertical-align:super; font-size:8px;">1</span></th>
		# 			<th width="100">Last Stock<span style="vertical-align:super; font-size:8px;">1</span></th>
		# 		</tr><tr id="tr29860" onMous.......
		trs = soup.find('table').find_all('tr')[1:] # strip the header tag
		trs = trs[0:len(trs)-1] # trim the last two for "item alerts via google groups" tag

		for found in [tr for tr in trs if "out of stock" not in tr.text.lower()]:
			link = found.find('a', attrs={'href': re.compile("^http")})
			# print 'link:', link
			if link is None:
				print 'error, why couldnt we find a link:', found
				continue
			
			# decode it
			link = urllib2.unquote(str(link.get('href')))
			if 'ebay' in link:
				continue # ignore the ebay links

			if self.is_new_link(link):
				self.dispatch_link(gpu, link)

	def is_new_link(self, link):
		if link not in self.link_map:
			self.link_map[link] = time.time()
			return True
		return False
		
	def run_gc(self):
		while True:
			for l, tt in self.link_map.items():
				if time.time() - tt > self.settings['gc_expire_sec']:
					print "expired link, removing:", l
					del self.link_map[l]
			time.sleep(self.settings["gc_interval_sec"])

	def dispatch_link(self, gpu, link):
		link = self.strip_referrals(link)
		domain = urlparse(link).hostname
		print "found", gpu, "url:", link
		self.counter.incr('gpus', gpu)
		self.counter.incr('domains', domain)
		# take action
		if 'newegg' in link:
			item_id = link.split('?Item=')[1].split('&ignorebbr=')[0]
			newegg.Newegg(item_id)
			if platform == "linux" or platform == "linux2" or platform == "darwin": # Mac & Linux
					pygame.mixer.init()
					pygame.mixer.music.load('sound_file')
					pygame.mixer.music.play()
			elif platform == "win32":
    				winsound.PlaySound(self.settings['sound_file'], winsound.SND_ASYNC)
			return
		elif 'amazon' in link:
			pass #TODO			
		elif 'bhphotovideo' in link:
			pass #TODO
		elif 'nvidia' in link:
			pass #TODO			
		else:
			pass #TODO			
		
		print 'havent implemented', domain
		util.print_header("PARSED LINK:", link)
		webbrowser.open(link)
		if platform == "linux" or platform == "linux2" or platform == "darwin": # Mac & Linux
				pygame.mixer.init()
				pygame.mixer.music.load('sound_file')
				pygame.mixer.music.play()
		elif platform == "win32":
    			winsound.PlaySound(self.settings['sound_file'], winsound.SND_ASYNC)
	
	def strip_referrals(self, link):
		# screw that site, they put referral links!
		if 'send.onenetworkdirect.net' in link:
			link = link.split('&lnkurl=')[1]
		elif 'redirect.viglink.com' in link:
			link = link.split('&u=')[1]
		else:
			link = 'http' + link.split('http')[-1:][0] # grab the last if there exists mmore than 1 http
			
		return link

	def join(self):
		for t in self.threads:
			t.join()
