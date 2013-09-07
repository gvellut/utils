require 'rubygems'
require 'fileutils'
require 'mechanize'
require 'logger'
require 'ostruct'
require 'open-uri'
require "appscript"
include Appscript

class Crawler
  
  LOG = Logger.new STDOUT
  
  class << self

    def crawl(n = 10)
      FileUtils.mkdir_p("crawl")
      agent = WWW::Mechanize.new
      page = agent.get("http://muxtape.com/")
      page.save_as "crawl/main.html"
      new_mixtapes = {}
      (page/"ul.featured li a").each_with_index do |mixtape,i|
        link = mixtape.attributes['href']
        name = mixtape.inner_text
        file_name = "crawl/" + name + "_mixtape.html"
        break if  i + 1 > n 
        next if File.exist?(file_name) #don't crawl/analyze... if already crawled
        new_mixtapes[name] = file_name
        LOG.info "Downloading #{name}..."
        agent.get(link).save_as(file_name)
      end
      new_mixtapes
    end

    def analyze(mixtapes)
      mixtape_songs = {}
      mixtapes.each do |name,file_name|
        LOG.info("Analyzing #{name}...")
        page = Hpricot(open(file_name))
        songs = []
        (page/"script").each do |script|
          src = script.inner_text
          if src =~ /new\s+Kettle\(\[([^\]]+)\],\[([^\]]+)\]/
            ids, codes = [$1, $2].map {|a| a.gsub("'",'').split(",") }
            ids.zip(codes).each do |ic|
              songs << OpenStruct.new(:sid =>"#{ic[0]}.mp3", :url => "http://muxtape.s3.amazonaws.com/songs/#{ic[0]}?#{ic[1]}")
            end
          end
        end
        mixtape_songs[name] = songs
      end
      mixtape_songs
    end

    def download(mixtapes)
      FileUtils.mkdir_p("dl")
      mixtape_songs = {}
      mixtapes.each do |mixtape, songs|
        LOG.info("Downloading songs for #{name}...")
        dl_songs = []
        songs.each do |song| 
          num_tries = 3
          begin
            song_file =  "dl/#{song.sid}"
            if not File.exist?(song_file)
              LOG.info("Downloading song #{song.sid}...")
              open(song.url) do |f| 
                open(song_file,"wb") {|mp3| mp3.write f.read }
              end
            end
            dl_songs << song_file
          rescue
            num_tries -= 1
            LOG.info("Error downloading: #{num_tries} left")
            next if num_tries == 0
            retry
          end
        end
        mixtape_songs[mixtape] = dl_songs
      end
      mixtape_songs
    end

    def itunes(mixtapes)
      LOG.info("Launching iTunes...")
      i_tunes = app('iTunes')
      mixtapes.each do |mixtape,song_files|
        next if i_tunes.playlists[its.name.eq(mixtape)].exists #skip if exists
        LOG.info("Creating playlist #{mixtape}...")
        pl = i_tunes.make(:new => :user_playlist, :with_properties => {:name => mixtape})
        LOG.info("Adding files...")
        song_files.each do |sf| 
          i_tunes.add(MacTypes::FileURL.path(File.expand_path(File.dirname(__FILE__) + "/#{sf}")),  :to => pl) 
        end
      end
    end
  end
end

Crawler.itunes(Crawler.download(Crawler.analyze(Crawler.crawl(1))))
