# FE_Crawler
Envato and Freepik General Information Crawler

###########################


Please consider these steps to run the project: 

1. Unzip the whole project pack in a folder/directory

2. Create a python virtual environment using this command:
	python -m venv env 
	
3. Activate the environment:
	source/env/bin/activate
	
4. Install requirements: 
	pip install -r requirements.txt

5. Initiate playwright browsers ( for freepik ):
	playwright install 

6. run project:
	python src/main.py


* Note: you could use this project in different ways; I personaly prefer 
Gunicorn and running the project in the background and adding new links 
to the sqlite database. But of course you are free to use it in other ways
including but not limited to: Making api ( using fastApi or DjanogApi ), 
embeding in differet project, run in routine managment apps and so on. 




#####################################################

- How does the whole thing work: 
The code is run on a sequence of urls from freepik.com and envato.com
You have to put links inside the sqlite database named baaak.db, within 
a table called processed_urls. Each link has an status code of 0, 1, 2
if its new and not crawled before, its 0. then the codes starts to crawl 
each 0 status link and tries to download the related page (a.k.a saves it)
using the special crawler of the domain. If that is successful, the status 
will be changed to 1. then the code tries to pars information from the downloaded page. Again if successful, the status would be chaned to 2 and the data would be written into the mysql database. 

There is also a log, saved in the log folder with INFO, WARNING and ERROR statuses to capture information. 

- Configurations:
Please consider that you can change configurations in the main.py within the config {} section. 
here are the things you can change based on your needs:
	config = {
        'output_dir':  The directory in which html and json files are saved 
        'log_file': The directory in which log is saved 
        'start_id': The id of the first file to start from and save the name by. please don't change it if there is no need to. 
        'proxy': Proxy list and type in json. You could use http, https, socks4 and socks5 proxy types
        'crawl_delay': Delay in seconds between each URL crawl
    }
