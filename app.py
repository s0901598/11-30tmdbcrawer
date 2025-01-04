from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient 



url="https://www.themoviedb.org/movie"
maxpage=50
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}

res=requests.get(url,headers=headers)
soup=BeautifulSoup(res.text,'lxml')

client=MongoClient("mongodb://localhost:27017")
db=client['tmdb']
collection=db['tmdbproduct']

for page in range(maxpage):
    links=url+"Page="+str(page+1)
    items=soup.select('.page_wrapper > .style_1')

    
    for item in items:
       card = item.select('.content>h2')
       carddate=item.select('.content>p')
       cardpic=item.select('.picture>a>img')
       cardlink=item.select('.content>h2>a')

       if len(card) and len(carddate) and len(cardpic)  and len(cardlink)!= 0:
        name=card[0].text
        date=carddate[0].text
        pic=cardpic[0]['src']
        links="https://www.themoviedb.org"+cardlink[0]["href"]

        contentres=requests.get(links,headers=headers)
        contentsoup=BeautifulSoup(contentres.text,'lxml')
        moviestype=contentsoup.select('.genres')[0].text#電影類型
        userscore=contentsoup.select('.user_score_chart')[0]['data-percent']#電影評分
        movietime=contentsoup.select('.runtime')[0].text.strip()#電影時長
        actor=contentsoup.select('.people>.card>p>a')[0].text#演員
    
        alls=contentsoup.select('.profile')
        for all in alls :
           characterElements = all.select('.character')
           if len(characterElements) !=0 and  'Director' in all.select('.character')[0].text:
             director=all.select('p:nth-child(1)')[0].text#導演姓名
             directorlink="https://www.themoviedb.org"+all.select('p:nth-child(1)>a')[0].attrs['href']#導演連結
             directorinfo=requests.get(directorlink,headers=headers)
             directorsoup=BeautifulSoup(directorinfo.text,'lxml')
             directorElement=directorsoup.select('.content>.text')
             if len(directorElement) !=0 :
                directoestate=directorElement[0].text#導演簡介
             
             directorElements=directorsoup.select('.title>bdi')
             for directorElement in directorElements:
                directorPortfolio=directorElement.text#導演作品

        keywords=contentsoup.select('.keywords li a')
        for keyword in keywords:
            keyword=keyword.text#關鍵字
        OriginlLangue=contentsoup.select('.facts>p')[1].text.split(' ')[2]#原始語言

        performers=contentsoup.select('.people>.card>a')
        for performer in performers:
           performerlink="https://www.themoviedb.org"+performer.attrs['href']#演員連結
           performerinfo=requests.get(performerlink,headers=headers)
           performersoup=BeautifulSoup(performerinfo.text,'lxml')
           actorname=performersoup.select('.title>a')[0].text#演員姓名
           actorElement = performersoup.select('.content>.text')
           if len(actorElement) !=0 :
            
            actorfile=actorElement[0].text#演員簡介

           portfolios=performersoup.select('.poster')
           for portfolio in portfolios:
              actorportfolio=portfolio.attrs['alt']#演出作品
              
           
        data ={
           "name":name,#電影名稱
           "Date":date,#上映日期
           "Type":moviestype,#電影類型
           "Score":userscore,#電影評分
           "MovieTime":movietime,#電影時長
           "Actor":actor,#演員
           "ActorFile":actorfile,#演員簡介
           "ActorPortfolio":actorportfolio,#演出作品
           "Director":director,#導演姓名
           "DirectoeState":directoestate,#導演簡介
           "DirectorPortfolio":directorPortfolio,#導演作品
           "Keyword":keyword,#關鍵字
           "OriginlLangue":OriginlLangue,#原始語言
           "Pic":pic,#海報連結
           "Link":links,#簡介連結
        }
        collection.insert_one(data)
        print(f"插入數據成功")
        