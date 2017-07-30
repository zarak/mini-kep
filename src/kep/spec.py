# -*- coding: utf-8 -*-
# TODO: edit docstring for better formatting in documentation (eg hanging lines)
""":mod:`kep.spec` module contains data structures used as parsing instructions
in :mod:`kep.tables`. 

:mod:`kep.tables` relies on two global variables from :mod:`kep.spec`:
    
   - **UNITS** (dict) is a mapper dictionary to extract units of measurement 
from table headers. It applies to all of CSV file. 
     
   - **SPEC** (:class:`kep.spec.Specification`) contains parsing instructions 
by segment of CSV file:
       
       - segment start and end line 
       - header strings to match with variable name 
       - (optional) reader function name to extract data from ununsual tables 
   
 **SPEC** is constructed from main (default) and auxillary 
 :class:`kep.spec.Definition` instances, while :class:`kep.spec.Definition` 
 is basically a list of :class:`kep.spec.Indicator` instances with 
 start and end line strings, which delimit CSV file segment.   
 
 :class:`kep.spec.Indicator` holds variable name, text string(s) to match in 
 table header to locate this indicator and (...)
 
        
Notes:
    
- we need parse CSV file by segment , because 
  some table headers repeat themselves in across all of CSV file, so getting 
  unique result would be a problem. Cutting a segment out of CSV file gives 
  a very specific input for parsing. It is usually a few tables in length
   
- most indicators are defined in main (default) parsing definition, 
  retrieved by :method:`kep.spec.Specification.get_main_parsing_definition`
     
- `kep.spec.Specification.get_additional_parsing_definitions` provides 
   segment parsing defintions 
 
   
Previously **UNITS** and **SPEC** were initialised based on yaml file, but this 
led to many errors, so these data structures were created to make definition of 
parsing instructions more stable.    
"""

from collections import OrderedDict as odict

# mapper dictionary to convert text in table headers to unit of measurement
UNITS = odict([  # 1. MONEY
    ('млрд.долларов', 'bln_usd'),
    ('млрд. долларов', 'bln_usd'),
    ('млрд, долларов', 'bln_usd'),
    ('млрд.рублей', 'bln_rub'),
    ('млрд. рублей', 'bln_rub'),
    ('рублей / rubles', 'rub'),
    ('млн.рублей', 'mln_rub'),
    # 2. RATES OF CHANGE
    ("Индекс физического объема произведенного ВВП, в %", 'yoy'),
    ('в % к декабрю предыдущего года', 'ytd'),
    ('в % к предыдущему месяцу', 'rog'),
    ('в % к предыдущему периоду', 'rog'),
    ('% к концу предыдущего периода', 'rog'),
    # this...
    ('период с начала отчетного года в % к соответствующему периоду предыдущего года', 'ytd'),
    #       ... must precede this
    # because 'в % к предыдущему периоду' is found in
    # 'период с начала отчетного года в % к соответствующему периоду предыдущего года'
    ('в % к соответствующему периоду предыдущего года', 'yoy'),
    ('в % к соответствующему месяцу предыдущего года', 'yoy'),
    ('отчетный месяц в % к предыдущему месяцу', 'rog'),
    ('отчетный месяц в % к соответствующему месяцу предыдущего года', 'yoy'),
    ('период с начала отчетного года', 'ytd'),
    # 3. OTHER UNITS (keep below RATES OF CHANGE)
    ('%', 'pct'),
    ('в % к ВВП', 'gdp_percent'),
    # 4. stub for CPI section
    ("продукты питания", 'rog'),
    ("алкогольные напитки", 'rog'),
    ("непродовольственные товары", 'rog'),
    ("непродовольст- венные товары", 'rog'),
    ("услуги", 'rog')
])

# 'official' names of units used in project front
UNIT_NAMES = {'bln_rub': 'млрд.руб.',
              'bln_usd': 'млрд.долл.',
              'gdp_percent': '% ВВП',
              'mln_rub': 'млн.руб.',
              'rub': 'руб.',
              'rog': '% к пред. периоду',
              'yoy': '% год к году',
              'ytd': 'период с начала года',
              'pct': '%'}

# check: all units in mapper dict have an 'offical' name
assert set(UNIT_NAMES.keys()) == set(UNITS.values())


def as_list(x):
    if isinstance(x, str):
        return [x]
    else:
        return x


class ParsingInstruction:
    #FIXME: edit docstring to Google style + heavy editing/rewrite
    """An economic indicator parsing instructions.
    
     Args:     
        varname(string): variable name string like 'GDP', 'CPI', etc
        text(string or list): string(s) found in table header, eg  'Объем ВВП', 'Gross domestic product'
        required_units(string or list) - unit(s) of measurement required for this indicator
                         examples: 'rog', ['rog'],  ['bln_rub', 'yoy']
        desc           - indicator desciption string for frontpage
        sample         - control string - one of raw CSV file rows (not implemented)

    
    """
    
    def __init__(self):
        self.varname_mapper = odict()
        self.required_labels = []
        self.descriptions = odict()
        
        
    def append(self, varname, text, required_units, desc=False):
        # conversion from user interface
        header_strings = as_list(text)
        if desc is False:
             desc = header_strings[0]
        required_units = as_list(required_units)
        # adding values to mappeк
        varname_mapper = odict([(hs, varname) for hs in header_strings])
        self.varname_mapper.update(varname_mapper)        
        # adding values to desc
        self.descriptions.update({varname: desc})
        # IDEA 1: make label a module and store lables here, not pairs
        # IDEA2: sample data also can go here
        # adding values to required
        required_labels = list((varname, unit) for unit in required_units)
        self.required_labels.extend(required_labels)       


    def __eq__(self, x):
        flag1 = self.required_labels == x.required_labels 
        flag2 = self.varname_mapper == x.varname_mapper 
        return bool(flag1 and flag2)

    
class Definition(object):
    
    def __init__(self, scope=False, reader=False):
        self.instr = ParsingInstruction()
        self.scope = scope
        self.reader = reader

    def append(self, *arg, **kwarg):
        self.instr.append(*arg, **kwarg)        
    
    def set_scope(self, sc):
        self.scope = sc

    def set_reader(self, rdr):
        self.reader = rdr

    def get_varname_mapper(self):
        """EDIT: Combine varname regex strings for all indicators."""
        return self.instr.varname_mapper

    def get_required_labels(self):
        """EDIT: Combine list of required variables for all indicators."""
        return self.instr.required_labels

    def get_varnames(self):
        varnames = self.get_varname_mapper().values()
        return list(set(varnames))


class Scope():
    """Start and end lines for CSV file segment and associated variables
       defintion.

       Holds several versions of start and end line, return applicable line
       for a particular CSV file versions. This solves problem of different
       headers for same table at various releases.
    """

    def __init__(self, start, end, reader=None):
        self.__markers = []
        self.add_bounds(start, end)
    #     self.definition = Definition(reader)

    def add_bounds(self, start, end):
        if start and end:
            self.__markers.append(dict(start=start, end=end))
        else:
            raise ValueError("Cannot accept empty line as Scope() boundary")

    def get_bounds(self, rows):
        """Get start and end line markers, which can be found in *rows*"""
        rows = [r for r in rows]  # consume iterator
        for marker in self.__markers:
            s = marker['start']
            e = marker['end']
            if self.__is_found(s, rows) and self.__is_found(e, rows):
                return s, e
        msg = self.__error_message(rows)
        raise ValueError(msg)

    @staticmethod
    def __is_found(line, rows):
        """Return True, is *line* found at start of any entry in *rows*"""
        for r in rows:
            if r.startswith(line):
                return True
        return False

    def __error_message(self, rows):
        msg = []
        msg.append("start or end line not found in *rows*")
        for marker in self.__markers:
            s = marker['start']
            e = marker['end']
            msg.append("is_found: {} <{}>".format(self.__is_found(s, rows), s))
            msg.append("is_found: {} <{}>".format(self.__is_found(e, rows), e))
        return "\n".join(msg)

    def __repr__(self):
        s = self.__markers[0]['start'][:10]
        e = self.__markers[0]['end'][:10]
        return "bound by start <{}...> and end <{}...>".format(s, e)


class Specification:
    """EDIT: Specification holds a list of defintions in two variables:

       .main ()
       .scope (segment defintitions)
       
    """

    def __init__(self, default):
        # main parsing definition
        self.main = default
        # additional parsing instructions for segments
        self.segment_definitions = []

    def append(self, pdef):
        self.segment_definitions.append(pdef)
        # WONTFIX: validate order of markers - ends are not starts

    def get_main_parsing_definition(self):
        return self.main

    def get_segment_parsing_definitions(self):
        return self.segment_definitions
    
    def all_definitions(self):        
        return [self.main] + self.segment_definitions    

    def get_required_labels(self):
        req = []
        for pdef in self.all_definitions():
            req.extend(pdef.get_required_labels())
        return req

    def get_varnames(self):
        varnames = set()
        for pdef in self.all_definitions():
            varnames.add(pdef.get_varnames())
        return list(varnames)



# global (default) parsing defintion
main = Definition()
main.append(varname="GDP",
            text=["Oбъем ВВП",
                  "Индекс физического объема произведенного ВВП, в %",
                  "Валовой внутренний продукт"],
            required_units=["bln_rub", "yoy"],
            desc="Валовый внутренний продукт (ВВП)")
# sample="1999	4823	901	1102	1373	1447"
main.append(varname="INDPRO",
            text="Индекс промышленного производства",
            required_units=["yoy", "rog"],
            desc="Промышленное производство")
# create Specification based on 'main' parsing instruction
SPEC = Specification(default=main)

# segment definitions
# -- investment
sc = Scope("1.6. Инвестиции в основной капитал",
           "1.6.1. Инвестиции в основной капитал организаций")
sc.add_bounds("1.7. Инвестиции в основной капитал",
              "1.7.1. Инвестиции в основной капитал организаций")
d = Definition(scope=sc)
d.append("INVESTMENT",
          "Инвестиции в основной капитал",
          ["bln_rub", "yoy", "rog"])
SPEC.append(d)

# -- CPI
sc = Scope(start="3.5. Индекс потребительских цен",
           end="4. Социальная сфера")
sc.add_bounds(start="4.5. Индекс потребительских цен",
              end="5. Социальная сфера")           
d = Definition(scope=sc)
d.append("CPI",
          text="Индекс потребительских цен",
          required_units="rog",
          desc="Индекс потребительских цен (ИПЦ)")
d.append("CPI_NONFOOD",
          text=["непродовольственные товары",
                "непродовольст- венные товары"],
          required_units="rog",
          desc="ИПЦ (непродтовары)")
SPEC.append(d)