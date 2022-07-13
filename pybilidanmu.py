'''
author: Mz1
email: mzi_mzi@163.com
感谢SocialSisterYi和小伙伴们整理的api文档！

'''

import asyncio
import websockets
import aiohttp
import json
import struct
import re
import ssl
import zlib
import brotli

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
	'Origin': 'https://live.bilibili.com',
	'Connection': 'Upgrade',
	'Accept-Language': 'zh-CN,zh;q=0.9',
}



class Pybilidanmu():
	def __init__(self, roomid='5295848'):
		self.get_danmu_info_url = 'http://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo?id='
		self.roomid = str(roomid)
		self.wss_url = 'wss://tx-bj-live-comet-01.chat.bilibili.com/sub'
		self.token = ""
		
		# ws连接
		self.ws_connect = None
		
		# 获取的弹幕/消息列表
		self.dm_list = []

	# get请求进入房间
	async def enter_room(self):
		url = self.get_danmu_info_url + self.roomid
		print(f'> 正在进入{url} ...')
		async with aiohttp.ClientSession() as s:
			async with s.get(url) as r:
				t = await r.text()
				data = json.loads(t)
				# print(json.dumps(data, indent=4))
				if data['code'] == 0:
					print('  > 进入房间成功')
					self.token = data['data']['token']
					host_list = data['data']['host_list']
					host = "wss://" + host_list[0]['host']
					port = host_list[0]['wss_port']
					self.wss_url = host+":"+str(port)+'/sub'   # 这里要加上sub不然连不上，笑死
					print(f'  > 弹幕地址: {self.wss_url}')
		# 连接弹幕服务器
		await self.connect_dm()
					
	# 心跳包
	async def heartbeat(self):
		while self.ws_connect == None:
			await asyncio.sleep(1)
			print('> 心跳包等待连接')
		while True:
			print('> 发送心跳包')
			await self._send_pack(b'hahahaha', protocol=1, opcode=2)   # 心跳包
			await asyncio.sleep(30)
					
	# 连接wss
	async def connect_dm(self):
		print('=======================================================')
		print('> 正在连接wss服务器...')
		async with websockets.connect(
				self.wss_url, 
				extra_headers=headers
				) as websocket:
			self.ws_connect = websocket  # 保存一下连接
			# 发送登录包等等
			# 不知道现在为啥这个还不行 现在用0的话就是不认证身份（游客）
			enter_pack = '{'+f'"uid":0,"roomid":{self.roomid},"protover":3,"platform":"web","type":2,"key":"{self.token}"'+'}'
			# enter_pack = '{"uid":184432814,"roomid":1942240,"protover":3,"platform":"web","type":2,"key":"Sua6T7_CdTXuLoZOAceMHFIp5BPb0Pxg_Pc_rWXW_f6fEB80KThouiWXQ2lD4dv1XkTG5I5jZzBsYJYLy05PhLiJFWUxdS8Gz8xlwXHFcnCgoKLdg-7raOjXiFkJbIyu8I9Ri09l3z9gnlCCE8KKhR0="}'
			await self._send_pack(enter_pack.encode())
			while True:
				tmp = await self._recv_pack()   # 接收并处理包
				print(tmp, end='\n\n')
				# 尝试解析内容
				self.dm_list.append(tmp)
		
		
		print('> 连接成功')
		
	# 发送包（添加包头部信息）
	# content为bytes
	async def _send_pack(self, content, protocol=1, opcode=7):
		header_length = 0x0010  # 头部长度
		buf = b''
		buf += struct.pack('>I', len(content)+header_length)   # 总长度，大端序 4bytes
		buf += struct.pack('>H', header_length)           # 头部长度 大端序 short
		# protocol = 1   # 认证或心跳是1
		buf += struct.pack('>H', protocol)              # 协议版本
		# opcode = 7    # 认证包
		buf += struct.pack('>I', opcode)           # 操作码（封包类型）
		sequence = 0x00000001     # 说是要递增但是抓包了感觉没啥关系
		buf += struct.pack('>I', sequence)
		# print(buf)  # 输出头部检查
		buf += content   # 加上内容部分
		print('  > 发送包: ',end='')
		print(buf)
		await self.ws_connect.send(buf)   # 发送包
		
	# 用于收包或者解压包
	# content是需要解析的包
	async def _recv_pack(self, content=None):
		if content == None:
			content = await self.ws_connect.recv()
			print('---------------------------------------------------------')
			print('  > 收到数据包:')
		else:
			print('  > 解析数据包:')
		# print(content)
		tmp = content[:4]
		pack_length = struct.unpack('>I', tmp)[0]  # unpack返回元组
		content = content[4:]
		# print(f'    > 数据包总长度:{pack_length}')
		tmp  = content[:2]
		header_length = struct.unpack('>H', tmp)[0]
		content = content[2:]
		# print(f'    > 数据包头部长度:{header_length}')
		tmp  = content[:2]
		protocol = struct.unpack('>H', tmp)[0]
		content = content[2:]
		print(f'    > 协议版本:{protocol}')
		tmp  = content[:4]
		opcode = struct.unpack('>I', tmp)[0]
		content = content[4:]
		print(f'    > 操作码:{opcode}')
		tmp  = content[:4]
		sequence = struct.unpack('>I', tmp)[0]
		content = content[4:]
		# print(f'    > 序列号:{sequence}')
		# protocol为0或1时数据包是不压缩的直接返回即可
		if protocol == 0 or protocol == 1:
			return content
		else:
			print(f' > 此数据包为压缩数据包,压缩类型:{protocol} (2:zlib, 3:brotli)')
			if protocol == 3:
				tmp = brotli.decompress(content)
				# print(f'  > 解压结果:{tmp}')
				tmp = await self._recv_pack(content=tmp)  # 解析这个包
				# print(f'  > 解包结果:{tmp}')
				return tmp     # 返回结果
			if protocol == 2:
				tmp = zlib.decompress(content)
				return tmp
		
		
		
		




if __name__ == '__main__':
	client = Pybilidanmu(23718393)
	tasks = [
		client.enter_room(),
		client.heartbeat(),
	]
	loop = asyncio.get_event_loop()
	try:
		loop.run_until_complete(asyncio.wait(tasks))
	except KeyboardInterrupt:
		for task in asyncio.Task.all_tasks():
			task.cancel()
		loop.run_forever()
	
	loop.close()
