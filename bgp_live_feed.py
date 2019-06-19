#!/usr/bin/python3

import json
import websocket
from argparse import ArgumentParser

class RISFeed():
	
	def main(self):
		parser = ArgumentParser(description='Monitor global routing changes live using Atlas RIS probes')
		parser.add_argument(
			'-r', '--route-collector',
			type=str,
			default='rrc14',
			help='Change route-collector to receive feed from, collectors can be found on www.ripe.net. Default - RRC14 (Palo Alto IX)'
		)
		parser.add_argument(
			'-a', '--as-path',
			type=str,
			default=None,
			help='Find route changes with specified ASN in AS Path. Regex can be used here. E.g. ^7575 would catch every update where the next hop AS is 7575, or 7575$ would catch all route changes originating from AS7575'
		)
		parser.add_argument(
			'-t', '--change-type',
			type=str,
			default=None,
			help='Filter route updates to only show announcements or withdrawals, e.g. -t announcements or -t withdrawals'
		)
		arguments = parser.parse_args()

		self.feed_url = "wss://ris-live.ripe.net/v1/ws/"
		self.params = {
			"moreSpecific": True,
			"type": "UPDATE",
			"path": arguments.as_path,
			"require": arguments.change_type,
			"host": arguments.route_collector 
		}
		self.web_socket()
		
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
				routing_change = json_data.get('data')
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
	bgp_feed = RISFeed()
	bgp_feed.main()
