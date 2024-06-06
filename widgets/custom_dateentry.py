from tkcalendar import DateEntry
from communication.data_structure import Timestamp2020


class CustomCalendar(DateEntry):

    def __init__(self, parent, **kw):
        super().__init__(parent, date_pattern='yyyy-mm-dd', style='DateEntry',
                         mindate=Timestamp2020.convert_to_datetime(0), **kw)

    def set_pattern(self, pattern):
        formatted_pattern = pattern.replace('%Y', 'yyyy').replace('%d', 'dd').replace('%m', 'mm')
        self.configure(date_pattern=formatted_pattern)
