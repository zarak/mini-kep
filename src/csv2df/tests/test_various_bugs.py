import pytest
from csv2df.helpers import PathHelper
from pathlib import Path
import pandas as pd

# regression tests - after bug fixes on occasional errors

ROOT = Path(__file__).parents[3] 


def test_time_index_is_included_in_access():    

    def make_path(freq):
       folder = ROOT / 'data' / 'processed' / 'latest' 
       return str(folder / "df{}.csv".format(freq))
   
    for freq in 'aqm':
        df = pd.read_csv(make_path('a'))
        assert df.columns[0] == 'time_index'

def test_csv_has_no_null_byte():
    csv_path = PathHelper.locate_csv(2015, 2)
    z = csv_path.read_text(encoding='utf-8')
    assert "\0" not in z


if __name__ == "__main__":
    pytest.main([__file__])
