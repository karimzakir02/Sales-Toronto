# Sales Data Engineering Project
Welcome to my Sales Data Engineering Project! The project is currently deployed using Linode. You can find the website [here](http://172.105.19.211). I am planning to purchase a domain for the website soon.

If you have any feedback, I would love to hear from you! Feel free to open a GitHub issue or messaging me on [LinkedIn](https://www.linkedin.com/in/karim-zakir-172124171/)

## What does the website do?
At this stage, the website scrapes data daily from three large supermarket chains in Toronto (Loblaws, FreshCo, and Metro) and retrieves information about the products that are on sale. It processes the data, saves it to a database, and then displays some of the information about the products on the front page. 

## Why I built the project?
I built this project in order to develop my data engineering and software engineering skills. I worked on my data engineering skills by writing web scraping algorithms and processing data obtained from different sources to ensure the retrieved data fit into a single database. I worked on my software engineering skills by constantly striving to follow the SOLID principles, CLEAN architecture, and ensuring that my code was readable, modifiable, and easy to build-upon. 

## FAQ
In this section, I will answer some questions you might have about my design choices or other code-related questions. 

### Why Flask?
Prior to this project, I've only read and briefly modified Flask code, but have never built a webapp from the ground up. So, I decided that this would be the perfect opportunity to learn the framework and become more familiar with it. 

### How is the data going to be used?
At the moment, I don't have any concrete plans about the data that the webapp will collect over time. I am planning to create a dashboard in the webapp that will provide some summary statistics and create interesting visualizations based on the data. Additionally, I might analyze the data in more detail in a separate notebook and create more detailed visualizations. Finally, after a year, I will most-likely publish the data somewhere on Kaggle to make the data accessible to everyone. 

### What are the differences between `requests_webscrapers` and `selenium_webscrapers`? Why are `requests_webscrapers` used in production, and not `selenium_webscrapers`?
One of the main problems I had to solve when developing this project was that the sales pages were dynamically updated when sending GET requests to them. This means that a simple GET request to a flyer URL would return a mostly-empty page. To solve this problem, I first wrote the `selenium_webscrapers` package. The idea was that I would create a Selenium object and wait until the page made all of the neccesary requests; I would then loop through those requests, find the ones I needed, and work with their responses. After deploying this method to production, I found that there's a lot of hassle setting up Selenium on a remote server, and the behavior of the package in deployment tended to be quite different from the behavior of the package in the development stage. These problems, along with some other inconviniences, pushed me to find a new solution to my problem. 

To solve these issues, I wrote the `requests_webscrapers` package. Instead of sending GET requests to the flyer webpages, these webscrapers send GET/POST requests directly to the API that the store webpages work with and processes their responses. With this package, I pretty much removed the 'middle-men' that were the flyer pages and started directly working with the API's.

## Future Development Plans
- Add a dashboard to display analysis based on the data
- Add more supermarket chains
- Add unit testing to the app
- Contunue adding other interesting features