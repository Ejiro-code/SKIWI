import unittest
import pymysql
from decimal import *


class TestSQLQueries(unittest.TestCase):

    def test_select_all_employees(self):
        conn = pymysql.connect(host='localhost', user='admin157',
                               password='goodgradeplease', db='CS157_FP')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Purchasable_Items;")
        result = cursor.fetchone()
        print(result)
        expected = ('P001', 'Tickets', 'spring fun',
                    Decimal('94.00'), Decimal('3'))
        # , ('P05', 'Lodges', "Peter's House", 21, 0), ('P09', 'Lessons', 'Skiing Basics', 20.30, 3)
        self.assertEqual(result, expected)
        conn.close()


if __name__ == '__main__':
    unittest.main()
