import socket

class page_content():			#类中定义不同函数，每个函数定义具体页面内容，如：http://127.0.0.1:port/page1
	def __init__(self):
		pass

	def home_page(self):							#首页： 提供导航，点击导航链接是post请求
		f = open('home_page.html','rb')
		data = f.read()
		return data


	def page1(self):
		f = open('page1_login.html','rb')			#关联同文件夹中的html文件，实现login; 注意open时一定要'rb'模式
		data = f.read()
		return data


	def page2(self):
		f = open('page2_static.html', 'rb')			#实现静态表单
		data = f.read()
		return data


	def page3(self):
		f = open('page3_dynamic.html', 'r', encoding='UTF-8')			#实现简单动态页面,实时更新显示当前时间，因为需要对open数据处理，使用'r'模式，后续再转为bytes
		data = f.read()
		import time
		ctime = time.time()
		data = data.replace('@time@', str(ctime))
		return bytes(data,encoding='UTF-8')


	def page4(self):
		return b'page4: send text'					#模拟通过网页发送文本给用户: 网络上传输文本，一定要转为bytes类型


	def page5(self):								#调取数据库内容，实现动态信息显示, 但是渲染部分采用笨办法

		#连接mysql数据库
		import pymysql
		conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='Intech.2018',database='store', charset='utf8')
		cursor = conn.cursor()
		cursor.execute('select * from web_test;')				#执行SQL
		conn.commit()
		data = cursor.fetchall()

		#收集数据库数据并生成html配置文件， 俗称模板渲染render
		replace_info = ""
		for item in data:
			replace ="""<tr><th>{0:}</th><th>{1:}</th><th>{2:}</th></tr>""".format(item[0],item[1],item[2])
			replace_info += replace

		#替换html配置
		f = open('page5_mysql_info.html', 'r', encoding='UTF-8')
		data = f.read()
		data = data.replace("@replace@",replace_info)

		return bytes(data, encoding='UTF-8')


	def page6(self):
		"""
		使用jinja2渲染html，优化page5中生成渲染部分
		"""

		#连接mysql数据库
		import pymysql
		conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='Intech.2018',database='store', charset='utf8')
		cursor = conn.cursor()
		cursor.execute('select * from web_test;')				#执行SQL
		conn.commit()
		db_entry = cursor.fetchall()

		#用jinja2 渲染模板
		f = open('page6_render_jinja2.html', 'r', encoding='UTF-8')		#步骤1: 读取html模板数据
		data = f.read()

		from jinja2 import Template						#步骤2: 导入jinja2，并将html模板数据加入Template
		templates = Template(data)

		data = templates.render(list_entry=db_entry)	#步骤3: 渲染，与page6_render_jinja2 中的{% for a,b,c in list_entry%} 语法关联

		return bytes(data, encoding='UTF-8')



def run(listen_ip,listen_port):
	#socket listen ip and port
	sock = socket.socket()
	sock.bind((listen_ip,listen_port))
	sock.listen(5)

	#主循环处理用户请求数据并作出相应respond
	while True:
		conn, addr = sock.accept()									#hold on utill new users'request
		data = conn.recv(8096)										#接收用户数据

		print("用户请求信息: ",data)													#打印请求内容
		print("用户IP信息: ",addr,'\n')													#打印用户IP

		#处理用户get请求:得到用户请求的URL
		user_request= str(data,encoding='UTF-8')
		header,body = user_request.split('\r\n\r\n')
		get,url,protocol = header.split('\r\n')[0].split(' ')

		#关联用户URL和网站Page
		func_name = None
		for item in router:											#判断用户请求的URL是否在路由中
			if item[0] == url:
				func_name = item[1]
				break

		if func_name:												#如果用户请求的URL在路由中，则执行路由中对应的函数
			response = func_name()
		else:
			response = b'404 NOT FOUND'								#如果用户请求的URL不再路由中，则返回404

		#发送数据
		conn.send(b'HTTP/1.1 200 OK\r\n\r\n')						#服务器发送数据时的响应头
		conn.send(response)											#服务器响应内容
		conn.close()												#响应完毕即关闭链接，http特点: 一次性，短链接



if __name__ == '__main__':


	"""
	极简web框架，用户理解网页交互逻辑，设计思路如下：
	1. 监听本机端口
	2. 获取用户HTTP 请求信息(URL)
	3. 编写URL对应的网页内容。若需要关联处理HTML文件，则该处理过程叫做渲染
	4. 建立URL与网页内容的关联，俗称路由
	5. 判断用户请求的URL是否存在，存在则返回第四步对应的URL页面内容给用户；不存在则404
	提示：page5和page6 涉及的数据库名称叫做web_test, 数据表仅三列字段：id/name/age
	"""


	# 指定本机监听IP和端口
	listen_ip = "127.0.0.1"
	listen_port = 8443

	page = page_content()		#定义网页内容

	# 定义用户：URL---->页面 的关联, 俗称路由； 用户访问链接应为: http://127.0.0.1:8443/page* , * 为路由中的具体page值
	router = [
		('/', page.home_page),				#首页
		('/page1', page.page1),
		('/page2', page.page2),
		('/page3', page.page3),
		('/page4', page.page4),
		('/page5', page.page5),
		('/page6', page.page6),
	]

	# 运行主程序
	print("开始监听: {0:}:{1:}\n请在浏览器中输入: http://{2:}:{3:}\n".format(listen_ip,listen_port,listen_ip,listen_port))
	run(listen_ip,listen_port)
