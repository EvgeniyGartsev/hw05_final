import datetime as dt


# context processor for add current date in footer
def current_year(request):
    current_year = dt.datetime.now().year
    return {"current_year": current_year}
