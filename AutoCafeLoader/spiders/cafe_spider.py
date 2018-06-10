import scrapy
import os
import urllib.request
import datetime

class CafeSpider(scrapy.Spider):
    name = "cafe"

    def start_requests(self):
        # read file into a list
        db = []
        with open("manga_db.txt","r") as file:
            for line in file:
                db.append(''.join(e for e in line if e.isalnum() or e == ' '))
        print("# of Entries: " + str(len(db)))


        urls = [
            ''
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"db":db})




    def parse(self, response):
        try:
            # go through group on the current page
            for group in response.css('div.group'):
                title = group.css("a::text").extract_first()
                folder_path = "download/" + ''.join(e for e in title if e != '?' and e != '>' and e != '<' and e != '|' and e != '*' and e != '/'and e != ':'and e != '"'and e != '\\')

                # every group has a title and a link
                title_exist = False;
                if (''.join(e for e in title if e.isalnum() or e == ' ') in response.meta["db"]):     # comparing each line in the file with the title (after removing all special character) note: strip() removes whitespace
                    title_exist = True
                    print("STATUS: The title, "+ title +" already exist!")


                if (not title_exist):
                    accept = ""
                    while (accept != "y" and accept != "n"):
                        accept = input("Would you like to download (y/n): " + title + "?")
                    if (accept == "y"):
                        # if title doesn't exist, write the title to the file holding all the titles
                        print("STATUS: The title, " + title +" , missing!")

                        with open("manga_db.txt","a") as file:
                            file.write(''.join(e for e in title if e.isalnum() or e == ' ') + "\n")


                        # Create a folder with the same title
                        if not os.path.exists(folder_path):
                            print("STATUS: Creating folder for, " + title)
                            os.makedirs(folder_path)

                        # follow the link to proceed to download
                        link = group.css("div.element div.title a::attr(href)").extract_first() # page with pictures
                        yield scrapy.Request(link, callback=self.parse_manga_page, meta={"folder_path":folder_path})

            # prepare for next page
            next_page = response.css("div.next a::attr(href)").extract()[1]
            yield scrapy.Request(next_page, callback=self.parse, meta=response.meta)
        except:
            pass



    def parse_manga_page(self, response):
        try:
            next_page = response.css("div.inner a::attr(href)").extract_first()
            #print("The next page is: " + next_page)

            image = response.css("div.inner img::attr(src)").extract_first()
            #print("The image url is: " + image)


            filename = image.split('/')[-1]
            #print("Filename is: " + filename)

            #downloading image
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(image, response.meta["folder_path"]+"/"+filename)

            yield scrapy.Request(next_page, callback=self.parse_manga_page, meta=response.meta)
        except:
            pass
