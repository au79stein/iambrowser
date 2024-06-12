#!/usr/bin/env python3

import etcd

'''
client = etcd.Client(
  host='192.168.1.78',
  port=4001,
  allow_reconnect=True,
  protocol='https',
  )
'''

client = etcd.Client()


# create key only
client.write('/nodes/n1', 'test', prevExist=False)

