# cpquant
# Project Description: 
Building the "cpquant" Python Package for Financial Data Handling

# Project Work
All project work will be compiled in this GitHub Repo

# Project Members:
Charlie Ray

Seth Johnson

# Overview
This project aims to build a Python package, "cpquant," designed to retrieve and handle financial data. This package will incorporate wrappers for APIs from Alpaca and ThetaData, two leading financial data providers. Additionally, it will include standard quantitative functions essential for financial analysis. The final deliverable is a comprehensive documentation page that covers all the functionalities of the "cpquant" package.

# Objectives
Develop Python wrappers for each of the endpoints detailed in Alpaca and ThetaData's documentation.

Design and implement standard quantitative functions (e.g., correlation matrix) within the package. The choice of additional functions is left to the members' discretion.

Ensure robustness of the package by writing and executing extensive unit tests for all functions.

Create thorough and user-friendly documentation for the "cpquant" package, detailing its functionality, usage, and examples.

# Deliverables
A fully functional Python package, "cpquant," that includes the mentioned features.

Unit tests for all functions within the package.

A comprehensive documentation page for the "cpquant" package.

# Methodology
Members should begin by thoroughly understanding the APIs of Alpaca and ThetaData. Following this, wrappers should be created for each endpoint according to their specifications. The choice of additional quantitative functions should be guided by their potential usefulness in financial data analysis. Unit tests must be designed to ensure each function behaves as expected in a variety of scenarios. Finally, comprehensive documentation should be created, providing clear instructions and examples on using the package.

# Timeline
While the project timeline may vary based on the team's pace, it is advised to follow this rough outline:

Weeks 1-2: Understanding Alpaca and ThetaData APIs and building wrappers.

Weeks 3-4: Incorporating standard quantitative functions into the package.

Weeks 5-6: Designing and running unit tests.

Weeks 7-8: Developing comprehensive documentation.

# Roles and Responsibilities
Roles should be divided amongst the team to encourage effective collaboration.

# Resources
[Alpaca API Documentation](https://docs.alpaca.markets/reference/stockbars)

[ThetaData API Documentation](https://thetadata.stoplight.io/docs/thetadata-rest-api/611e2468ac8fe-end-of-day)

[Python Unit Testing](https://docs.python.org/3/library/unittest.html)

[How to Write Effective Documentation](https://guides.lib.berkeley.edu/how-to-write-good-documentation)

[Using Python Requests](https://realpython.com/python-requests/#ssl-certificate-verification)

[Introduction to Pandas](https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html)

# Evaluation Criteria
Although no third party will directly be evaluating this project, it will be helpful to ask yourself how well the project completes the following criteria.

The completeness and accuracy of the Python wrappers.

The relevance and functionality of the quantitative functions included.

The comprehensiveness and effectiveness of the unit tests.

The clarity and thoroughness of the package documentation.

# Communication and Collaboration
Regular meetings should be scheduled to discuss progress, clarify doubts, and resolve issues. All members are encouraged to share their insights and findings throughout the project. We will have (weekly/bi-weekly, TBD) meetings on Microsoft Teams, and members are encouraged to reach out to other members if problems arise.

# Creativity and Learning
While the project's objectives are clear, members are encouraged to bring in their creativity and learning to enhance the package's capabilities. The package should ultimately serve as a reliable tool for quantitative finance analysis, shaped by your insights and expertise.

# Additional Notes
The wrappers should heavily utilize pandas data frames, and all data should be returned in a neatly organized data frame. For AlpacaData, only provide wrappers for the API endpoints under “Stock”  “News” “Screener” “Logos”. Others can be added at a later date but are not needed ATM. All endpoints under “Trading API” should be included as the HFT system may use them, prioritize the most important ones. We currently only have a free version of ThetaData, so for now only provide wrappers for endpoints with the free version, don't worry about stock data from ThetaData. That is what Alpaca is for. Just do “OPTIONS HISTORICAL FREE” & “List roots, expirations, strikes, dates”

For ThetaData, they require you to set up a local server to make requests, which doesn't work particularly well for the club. I set up a server with a reverse proxy to forward all requests to a master ThetaData server at 142.93.58.224, so instead of using the documented url of http://127.0.0.1:25510, use http://142.93.58.224:25510 This should work, although I’m doing things that ThetaData wasn’t designed for, so contact Charlie if something is wrong.

