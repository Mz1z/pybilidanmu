import pybilidanmu
import tkinter
import asyncio


root_window =tkinter.Tk()

root_window.title('Mz1弹幕姬')
root_window.geometry('450x300')


# 添加按钮，以及按钮的文本，并通过command 参数设置关闭窗口的功能
button=tkinter.Button(root_window,text="关闭",command=root_window.quit)
# 将按钮放置在主窗口内
button.pack(side="bottom")



if __name__ == '__main__':
	root_window.mainloop()
