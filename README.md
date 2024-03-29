# web-portal-django-excel-comparator
This django-based web portal lets the user upload excel files and compare them based on different fields, pivots, filters and actions. **Pandas** library has been used extensively for parsing and manipulating excel data.
  - Django version: 3.0.6
  - Python version: 3.7.4
# Instructions to Run
- Clone the repository and create a virtual environment for the project.
> python3 -m venv excelComparatorEnv
- Activate the virtual environment.
> source excelComparatorEnv/bin/activate
- Run the following command in the command line inside the virtual environment to install all the required libraries and modules:
> pip install -r requirements.txt 
- Run the following command to start the server at local host.
> python manage.py runserver
- Go to the *local host address of your server/model_upload* to start the portal.
