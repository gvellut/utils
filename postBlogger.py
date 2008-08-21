from __future__ import with_statement
from gdata import service
import gdata
import atom
import cPickle as pickle
import os
import feedparser

def login(user, password):
  blogger_service = service.GDataService(user,password)
  blogger_service.source = 'content-filler-1.0'
  blogger_service.service = 'blogger'
  blogger_service.server = 'www.blogger.com'
  blogger_service.account_type = 'GOOGLE' 
  blogger_service.ProgrammaticLogin()
  return blogger_service

def post(blogger_service, blog_id, author,title,content,tags,draft=True):
  entry = gdata.GDataEntry()
  entry.author.append(atom.Author(atom.Name(text=author)))
  entry.title = atom.Title('html', title)
  for tag in tags:
    category = atom.Category(term=tag, scheme="http://www.blogger.com/atom/ns#")
    entry.category.append(category)
  entry.content = atom.Content(content_type='html', text=content)
  if draft:
      control = atom.Control()
      control.draft = atom.Draft(text='yes')
      entry.control = control
  post = blogger_service.Post(entry, '/feeds/%s/posts/default' % blog_id)


def blogPost(pkl_file,blog_id,feed,user,password,author,draft,link_text):
  if os.path.exists(pkl_file):
    with open(pkl_file) as f:
      posts = pickle.load(f)
  else:
    posts = {}
    
  blogger = login(user,password)
    
  d = feedparser.parse(feed)
  for e in d.entries:
    if e.id in posts:
      continue
    print "Adding %s..." % e.title
    title = e.title
    description = e.description + '<p><a href=\'%s\'>%s</a></p>' % (e.link,link_text)
    post(blogger, blog_id,author,title,description,['bi','gis'],draft)
    posts[e.id] = True
      
  with open(pkl_file,"w") as f:
    pickle.dump(posts,f,True)











