#!/usr/bin/python3

import json
import websocket

class main():

	feed_url = "wss://ris-live.ripe.net/v1/ws/"
	params = {
		"moreSpecific": True,
		"type": "UPDATE",
		"host": "rrc00"
	}

	def web_socket(self):
		while True:
			ris_feed = websocket.WebSocket()
			ris_feed.connect(self.feed_url)
		
			ris_feed.send(json.dumps({
				"type": "ris_subscribe",
				"data": self.params
			}))

			for routing_update in ris_feed:
				json_data = json.loads(routing_update)
				routing_change = json_data["data"]

				timestamp = routing_change['timestamp']
				update_asn = 'AS{0}'.format(routing_change.get('peer_asn'))

				announcements = routing_change.get('announcements', None)
				withdrawals = routing_change.get('withdrawals', None)

				if announcements is not None:
					update_type = 'Announcement'
					try:
						announcement_as_path = ' '.join(str(asn) for asn in routing_change.get('path', None))
					except:
						announcement_as_path = ''
					
					for update in announcements:
						updated_prefixes = ' '.join(str(prefix) for prefix in update.get('prefixes', None))
						self.print_update(timestamp, update_asn, announcement_as_path, updated_prefixes, update_type)
				
				if withdrawals is not None:
					update_type = 'Withdrawal'
					announcement_as_path = None
					updated_prefixes = ' '.join(str(prefix) for prefix in withdrawals)
					self.print_update(timestamp, update_asn, announcement_as_path, updated_prefixes, update_type)

	def print_update(self, timestamp, update_asn, announcement_as_path, updated_prefixes, update_type):
		print('\nRouting update from: {0}'.format(update_asn))
		print('Update Type: {0}'.format(update_type))
		if announcement_as_path != None:
			print('AS Path: {0}'.format(announcement_as_path))
		print('Prefixes: {0}'.format(updated_prefixes))

if __name__ == '__main__':
	code = main()
	code.web_socket()
