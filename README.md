# Sales Data Engineering Project
Welcome to my Sales Data Engineering Project! The project is currently deployed and is in the beta stage. You can find the website [here](http://172.105.19.211). I am planning to purchase a domain for the website soon.

## What does the website do?
At this stage, the website scrapes data daily from three large supermarket chains in Toronto (Loblaws, FreshCo, and Metro) and retrieves information about the products that are on sale. It processes the data, saves it to a database, and then displays some of the information about the products on the front page. 

## Why I built the project
I built this project in order to develop my data engineering and software engineering skills. I worked on my data engineering skills by writing web scraping algorithms and processing data obtained from different sources to ensure it fits into a single database. I worked on my software engineering skills by constantly striving to follow SOLID principles, CLEAN architecture, and ensuring that my code was readable, modifiable, and easy to build-upon. 

## FAQ
In this section, I will answer some questions you might have about my design choices or other code-related questions. 

### Why Flask?
Prior to this project, I've only read and briefly modified Flask code, but have never built a webapp from the ground up. So, I decided that this would be the perfect opportunity to learn the framework and become more familiar with it. 

### How is the data going to be used?
At the moment, I don't have any concrete plans about the data that the webapp will collect over time. I am planning to create a dashboard in the webapp that will provide some summary statistics and create interesting visualizations based on the data. Additionally, I might analyze the data in more detail in a separate notebook and create more detailed visualizations. Finally, after a year, I will most-likely publish the data somewhere on Kaggle to make the data accessible to everyone. 

## What is left to do before first release?
- Ensure the Loblaws scraper works consistently during deployment
- Improve the accuracy of old price data retrieval
- Better organize the files/modules

## Future Development Plans
- Add a dashboard to display analysis based on the data
- Add more supermarket chains
- Continue developing interesting features
- Add unit testing to the app