import sys, os
from urllib2 import Request, urlopen, URLError, HTTPError
from bs4 import BeautifulSoup

mangas = {"btoom" :
	("http://mangafox.me/manga/btooom/v{0:02d}/c{1:03d}/{2:d}.html", (9, 51, 47), (2, 14, 2), "btoom")
}

class Manga(object):
	def __init__(self, volume, chapter, page):
		self.volume = volume
		self.chapter = chapter
		self.page = page
		self.current_increment = 2
	
	def increment_page(self):
		self.page += 1
		self.current_increment = 2

	def increment_chapter(self):
		self.page = 1
		self.chapter += 1
		self.current_increment = 1

	def increment_volume(self):
		self.page = 1
		# chapter is is not reset between volumes
		# chapter = 1
		self.volume += 1
		self.current_increment = 0

			

def download_manga(spec):
	if not os.path.exists(spec[3]):
    		os.makedirs(spec[3])

	manga = Manga(spec[1][0],spec[1][1], spec[1][2])
	not_a_manga_page_counter = 0
	
	while(True):
		if manga.volume == spec[2][0] and manga.chapter == spec[2][1] and manga.page == spec[2][2]:
			print "Spec says we are done. Exiting..."
			break

		print "Processing volume %d, chapter %d, page %d..." % (manga.volume, manga.chapter, manga.page)
		page_url = spec[0].format(manga.volume, manga.chapter, manga.page)
		req = Request(page_url)
		try:
    			response = urlopen(req)
			if response.geturl() != page_url:
				# a redirect was followed
				raise HTTPError(response.geturl(), 302, "", None, None)
			web_page = response.read()
			is_manga_page = download_image(BeautifulSoup(web_page), spec[3], "m_%d_%d_%d" % (manga.volume, manga.chapter, manga.page))
			if is_manga_page:
				manga.increment_page()
				not_a_manga_page_counter = 0
			else:
				print  "Not a manga page..."
				# to prevent infinite loop : see http://mangafox.me/manga/btooom/v02/c013/3.html
				# this allows only 5 chapter holes in a manga eg btoom missing 13
				# some problem if the hole is between volumes but ignore for now
				manga.increment_chapter()
				not_a_manga_page_counter += 1
				if not_a_manga_page_counter == 4:
					# assume it is the end
					print "Too many. Assume we are done... "
					break
				
		except HTTPError as e:
       			print 'Error code: ', e.code
			if manga.current_increment == 2:
				manga.increment_chapter()
				print "Incrementing chapter..."
			elif manga.current_increment == 1:
				manga.increment_volume()
				print "Incrementing volume..."
			else:
				print "No more page to fetch"
				break
			continue
		except URLError as e:
    			print 'We failed to reach a server.'
    			print 'Reason: ', e.reason

def download_image(page, directory, prefix):
	meta_thumb = page.find_all("meta", property="og:image")
	if len(meta_thumb) > 0:
		image_url = meta_thumb[0]['content']
		if not "thumbnails" in image_url and not "mini." in image_url:
			return False
		image_url = image_url.replace("thumbnails", "compressed")
		image_url = image_url.replace("mini.","")
		image_req = Request(image_url)
		try:
			image = urlopen(image_req)
			image_file = open(directory + "/" + prefix + ".jpg", "wb")
			image_file.write(image.read())
			image_file.close()
			return True
		except HTTPError, e:
			print "HTTP Error:",e.code , image_url
		except URLError, e:
			print "URL Error:",e.reason , image_url
	
	return False

_, title = sys.argv

download_manga(mangas[title])
