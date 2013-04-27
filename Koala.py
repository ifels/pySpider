#coding: UTF-8


from bs4 import BeautifulSoup
import re
import uuid
import urlparse
import pymongo
import Utils
import Config

'''
@license: Apache License 2.0
@version: 0.1
@author: 张淳
@contact: mail@zhang-chun.org
@date: 2012-08-16

http://code.google.com/p/pykoala/
'''

class KoalaStatus(object):
	'''
	爬虫状态管理

	# 爬虫状态是爬虫在执行过程中的环境数据。例如当前处理到哪个url，接下来还有哪些url需要处理等等。
	# 保存/恢复状态的意义在于，当爬虫结束（正常/意外）后再启动时，可以继续先前的进度，无需从头开始。
	# 当前版本中，爬虫的状态管理是基于“站点”的，用“站点id”来标识。好处就是简单，爬虫恢复先前进度变得很容易。
	# 但缺点也是显而易见的：当多个爬虫爬同一个站点时，状态的管理就变得相当复杂，会出现“重叠处理”，整体性能并不会加快。
	# 因此，多爬虫爬同一个站点的状态管理，在当前版本中并没有得到有效支持。请暂时不要这样使用，我会在后续版本中进行改进:-)

	状态统一存放在MongoDB、由DB_NAME定义的数据库中、以“站点id+下划线+状态类型”命名的集合里
	目前支持的状态类型：
	1. NextEntry	爬虫将要进入处理的url地址表。集合名格式为"站点id_nextentry"
					文档格式定义：
						doc['Hash']		url的哈希值，唯一索引
						doc['URL']		url地址
	'''
	# 默认使用的数据库名
	DB_NAME 					 = 'koalastatus'

	# 通用字段定义
	DOC_FIELD_DEFAULT_ID		 = '_id'
	# NextEntry类型字段定义
	DOC_FIELD_HASH 				 = 'Hash'
	DOC_FIELD_URL 				 = 'URL'

	def __init__(self, webSiteID):
		'''
		@param webSiteID: 站点id，用来唯一地标识某站点，一般使用站点url的哈希值
		@type webSiteID: 字符串
		'''
		if not webSiteID:
			raise ValueError('You must specified "webSiteID" parameter in constructor')

		self.conn = pymongo.Connection()

		# NextEntry集合
		self.collNextEntry = self.conn[KoalaStatus.DB_NAME]['%s_nextentry' % webSiteID]
		# 为NextEntry集合的Hash键创建唯一索引
		self.collNextEntry.ensure_index(KoalaStatus.DOC_FIELD_HASH, unique=True, dropDups=True)

	def __del__(self):
		self.conn.close()

	def is_have_next_entry(self):
		'''
		判断爬虫是否存在NextEntry

		@return: 存在则返回True，否则返回False
		@rtype: 布尔值
		'''
		if self.collNextEntry.count():
			return True
		else:
			return False

	def get_all_next_entry(self):
		'''
		获取爬虫所有的NextEntry

		@return: NextEntry表，表项为url
		@rtype: 列表，表项为字符串
		'''
		return \
		[
		item[KoalaStatus.DOC_FIELD_URL] for item in \
			self.collNextEntry.find(fields={
				KoalaStatus.DOC_FIELD_URL: 1,
				KoalaStatus.DOC_FIELD_DEFAULT_ID: 0,
			})
		]

	def add_next_entry(self, nextEntries):
		'''
		添加NextEntry到数据库，忽略重复项

		@param nextEntries: NextEntry表
		@type nextEntries: pythpn序列类型

		@return: 无
		'''
		for entryURL in nextEntries:
			doc = dict()
			doc[KoalaStatus.DOC_FIELD_HASH] 	 = Utils.hash(entryURL)
			doc[KoalaStatus.DOC_FIELD_URL] 		 = entryURL
			try:
				self.collNextEntry.insert(doc, safe=True)
			except pymongo.errors.DuplicateKeyError as error:
				Utils.write_stderr(repr(error))

	def remove_next_entry(self, nextEntries):
		'''
		删除数据库中对应的NextEntry

		@param nextEntries: NextEntry表
		@type nextEntries: pythpn序列类型

		@return: 无
		'''
		for entryURL in nextEntries:
			self.collNextEntry.remove({KoalaStatus.DOC_FIELD_HASH: Utils.hash(entryURL)}, safe=True)


class Koala(object):
	'''
	爬虫
	'''
	def __init__(self, webSiteURL, entryFilter=None, yieldFilter=None, identifier=None, enableStatusSupport=False):
		'''
		@param webSiteURL: 网站url地址
		@type webSiteURL: 字符串
		@param entryFilter: 入口过滤器，指定了爬虫可以进入哪些url。定义为字典，详情如下：
							['Type']
								'allow'	允许模式，只要满足过滤项目表中的任意一项即允许
								'deny'	排除模式，只要满足过滤项目表中的任意一项即排除
							['List']
								过滤项目列表，每一项均为正则表达式，字符串
		@type entryFilter: 字典
		@param yieldFilter: 生成过滤器，指定了爬虫要生成哪些url。定义为字典，详情如下：
							['Type']
								'allow'	允许模式，只要满足过滤项目表中的任意一项即允许
								'deny'	排除模式，只要满足过滤项目表中的任意一项即排除
							['List']
								过滤项目列表，每一项均为正则表达式，字符串
		@type yieldFilter: 字典
		@param identifier: 爬虫的id，用来标识爬虫
		@type identifier: 字符串
		@param enableStatusSupport: 是否启用状态支持，默认不启用
		@type enableStatusSupport: 布尔值
		'''
		if not webSiteURL:
			raise ValueError('You must specified "webSiteURL" parameter in constructor')

		webSiteURL = Utils.to_unicode(webSiteURL)

		# 如果url没有协议前缀，则使用默认协议前缀
		webSiteURL = Utils.ensure_url_default_scheme(webSiteURL)

		self.domain 		 = Utils.get_host(webSiteURL)
		self.webSiteURL 	 = webSiteURL
		self.entryFilter 	 = entryFilter
		self.yieldFilter 	 = yieldFilter

		# 如果没有指定id，则生成uuid
		if not identifier:
			self.identifier = str(uuid.uuid1())
		else:
			self.identifier = identifier

		# 是否启用状态支持的标记
		if not enableStatusSupport:
			self.koalaStatus = None
		else:
			self.koalaStatus = KoalaStatus(Utils.hash(self.webSiteURL))

		# 记录访问过的页面
		self.visitedEntriesHash = set()

	def get_id(self):
		'''
		获取爬虫id

		@return: 爬虫id
		@rtype: 字符串
		'''
		return self.identifier

	def go(self, maxDepth=10):
		'''
		启动爬虫，迭代返回抓取到的url

		@param maxDepth: 最大抓取深度
		@type maxDepth: 整数

		@return: 抓取到的url
		@rtype: 字符串
		'''
		# 恢复状态执行
		if self.koalaStatus:
			if self.koalaStatus.is_have_next_entry():
				nextEntries = self.koalaStatus.get_all_next_entry()
				for entryURL in nextEntries:
					for url in self.__crawl_proc(entryURL, maxDepth):
						yield url
				return

		# 全新执行
		for url in self.__crawl_proc(self.webSiteURL, maxDepth):
			yield url

	def __crawl_proc(self, entryURL, maxDepth):
		'''
		爬行的执行过程

		@param entryURL: 爬虫的入口url
		@type entryURL: 字符串
		@param maxDepth: 最大抓取深度
		@type maxDepth: 整数

		@return: 满足过滤条件的url
		@rtype: 字符串
		'''
		# 如果达到最大深度则返回
		if maxDepth <= 0:
			return

		# 解析出页面中所有的链接
		try:
			source = Utils.get_url_html(entryURL)
			soup = BeautifulSoup(source, Config.DEFAULT_HTML_PARSER)
			if self.__yield_filter(entryURL):
				self.__parse(soup)
		except Exception as error:
			Utils.write_stderr(repr(error))
			return
		links = list()
		for elemA in soup.find_all('a'):
			try:
				links.append(elemA['href'])
			except KeyError as error:
				#Common.write_stderr(repr(error))
				pass

		# 生成符合规则的链接，并记录符合规则的子页面
		nextEntries = list()
		for link in links:
			url = urlparse.urljoin(entryURL, link)
			if self.__global_filter(entryURL, url):
				if self.__yield_filter(url):
					yield url
				if self.__entry_filter(url):
					nextEntries.append(url)

		# 执行到此处代表一个（子）页面（EntryURL）处理完成

		# 需要记录到已处理页面集合中。处于性能考虑，记录url的hash值而非url本身
		self.visitedEntriesHash.add(Utils.hash(entryURL))

		# 如果启用状态支持，则同步删除数据库中对应的NextEntry数据（如果有的话）
		if self.koalaStatus:
			self.koalaStatus.remove_next_entry([entryURL])

		# 如果即将达到最大深度，处于性能考虑，不再进入子页面
		if maxDepth - 1 <= 0:
			return
		else:
			# 准备进入子页面之前，同步更新状态
			if self.koalaStatus:
				self.koalaStatus.add_next_entry(nextEntries)

			# 广度优先抓取
			for nextEntryURL in nextEntries:
				if Utils.hash(nextEntryURL) not in self.visitedEntriesHash:
					for url in self.__crawl_proc(nextEntryURL, maxDepth - 1):
						yield url

	def __global_filter(self, currentEntryURL, checkURL):
		'''
		全局过滤器

		@param currentEntryURL: 当前正在处理的页面url
		@type currentEntryURL: 字符串
		@param checkURL: 交给过滤器检查的url
		@type checkURL: 字符串

		@return: 通过检查则返回True，否则返回False
		@rtype: 布尔值
		'''
		# 不能为非本站的url
		if Utils.get_host(checkURL) != self.domain:
			return False

		# 不能和站点url相同
		if Utils.is_two_url_same(self.webSiteURL, checkURL):
			return False

		# 不能和当前正在处理的页面url相同
		if Utils.is_two_url_same(currentEntryURL, checkURL):
			return False

		return True

	def __entry_filter(self, checkURL):
		'''
		入口过滤器
		决定了爬虫可以进入哪些url指向的页面进行抓取

		@param checkURL: 交给过滤器检查的url
		@type checkURL: 字符串

		@return: 通过检查则返回True，否则返回False
		@rtype: 布尔值
		'''
		# 如果定义了过滤器则检查过滤器
		if self.entryFilter:
			if self.entryFilter['Type'] == 'allow':		# 允许模式，只要满足一个就允许，否则不允许
				result = False
				for rule in self.entryFilter['List']:
					pattern = re.compile(rule, re.I | re.U)
					if pattern.search(checkURL):
						result = True
						break
				return result
			elif self.entryFilter['Type'] == 'deny':		# 排除模式，只要满足一个就不允许，否则允许
				result = True
				for rule in self.entryFilter['List']:
					pattern = re.compile(rule, re.I | re.U)
					if pattern.search(checkURL):
						result = False
						break
				return result

		# 没有过滤器则默认允许
		return True

	def __yield_filter(self, checkURL):
		'''
		生成过滤器
		决定了爬虫可以返回哪些url

		@param checkURL: 交给过滤器检查的url
		@type checkURL: 字符串

		@return: 通过检查则返回True，否则返回False
		@rtype: 布尔值
		'''
		# 如果定义了过滤器则检查过滤器
		if self.yieldFilter:
			if self.yieldFilter['Type'] == 'allow':		# 允许模式，只要满足一个就允许，否则不允许
				result = False
				for rule in self.yieldFilter['List']:
					pattern = re.compile(rule, re.I | re.U)
					if pattern.search(checkURL):
						result = True
						break
				return result
			elif self.yieldFilter['Type'] == 'deny':		# 排除模式，只要满足一个就不允许，否则允许
				result = True
				for rule in self.yieldFilter['List']:
					pattern = re.compile(rule, re.I | re.U)
					if pattern.search(checkURL):
						result = False
						break
				return result

		# 没有过滤器则默认允许
		return True
	
	def __parse(self, beautifulSoup):
		self.parse(beautifulSoup) #Expected to be defined



