# NC-Schools-Marketshare

## Intro
The Innovation Project (TIP) works with school districts in North Carolina, and they offer all of their members access to marketshare files and maps of homeschool students in their respective districts.  This project creates marketshare files for every schools district in North Carolina, but only supplies TIP members with homeschool maps.  I compiled the data from the sources below and loaded it into a PostgreSQL database for querying.

## Data Sources
The marketshare data comes from the [North Carolina Department of Public Instruction EDDIE System](https://www.dpi.nc.gov/districts-schools/district-operations/financial-and-business-services/demographics-and-finances/eddie).

The homeschool population data is obtained through public records requests.  All parents must submit an intent form to operate a homeschool, and these forms are available to the public.

## File Structure

### flask_app.py
Creates the flask site to host the marketshare and homeschool maps.

### queries.py
Includes queries used to pull information from the ncschools database.

### Templates
Holds all html files used to build the individual web pages.  These files are built around a Jinja base template file.

### Static
Holds the CSS file used to format the web pages.

## Packages used
    pandas
    psycopg2
    Jinja
    flask
    json
