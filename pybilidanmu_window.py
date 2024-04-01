import pybilidanmu
import tkinter
import asyncio
import threading
import time

# 连接弹幕服务器
def connect():
	client = pybilidanmu.Pybilidanmu(30805550)
	coroutine1 = client.enter_room()
	coroutine2 = client.heartbeat()
	coroutine3 = fetch_dm(client)	         # 获取弹幕并显示的coroutine
	new_loop = asyncio.new_event_loop()                        #在当前线程下创建时间循环，（未启用），在start_loop里面启动它
	t = threading.Thread(target=start_loop,args=(new_loop,))   #通过当前线程开启新的线程去启动事件循环
	t.start()
	
	asyncio.run_coroutine_threadsafe(coroutine1,new_loop)
	asyncio.run_coroutine_threadsafe(coroutine2,new_loop)
	asyncio.run_coroutine_threadsafe(coroutine3,new_loop)


async def fetch_dm(client):
	text.insert('end', f'已连接上弹幕服务器, 当前房间号: {client.roomid}\r\n')
	while True:
		if len(client.dm_list) > 0:
			tmp = client.dm_list.pop(0)
			if len(tmp) > 20:    # 精简消息显示
				tmp = tmp[:30]+b'...'
			text.insert('end', f'消息: {tmp}\r\n')
			text.see('end')
		else:
			await asyncio.sleep(0.5)
		

root_window =tkinter.Tk()

root_window.title('Mz1弹幕姬')
root_window.geometry('500x300')

button=tkinter.Button(root_window,text="关闭",command=root_window.quit)
button.pack(side="bottom")
button0=tkinter.Button(root_window,text="连接",command=connect)
button0.pack(side="bottom")

# width 一行可见的字符数；height 显示的行数
text = tkinter.Text(root_window, width=60, height=25)
# 适用 pack(fill=X) 可以设置文本域的填充模式。比如 X表示沿水平方向填充，Y表示沿垂直方向填充，BOTH表示沿水平、垂直方向填充
text.pack()


#定义一个专门创建事件循环loop的函数，在另一个线程中启动它
def start_loop(loop):
	asyncio.set_event_loop(loop)
	loop.run_forever()

def main():    
	text.insert('end', '正在启动...\r\n启动完毕\r\n')
	root_window.mainloop()

if __name__ == '__main__':
	main()
	
