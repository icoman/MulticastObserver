{'application':{'type':'Application',
          'name':'Template',
    'backgrounds': [
    {'type':'Background',
          'name':'bgTemplate',
          'title':'Standard Template with File->Exit menu',
          'size':(642, 438),
          'style':['resizeable'],

        'menubar': {'type':'MenuBar',
         'menus': [
             {'type':'Menu',
             'name':'menuFile',
             'label':'&File',
             'items': [
                  {'type':'MenuItem',
                   'name':'menuFileAbout',
                   'label':u'&About',
                   'command':'about',
                  },
                  {'type':'MenuItem',
                   'name':'menuFileExit',
                   'label':'E&xit',
                   'command':'exit',
                  },
              ]
             },
         ]
     },
         'components': [

{'type':'CheckBox', 
    'name':'enablebroadcast', 
    'position':(215, 25), 
    'label':'Enable multicast server on:', 
    },

{'type':'ComboBox', 
    'name':'selectedInterface', 
    'position':(390, 20), 
    'size':(125, -1), 
    'items':[], 
    'text':'ComboBox1', 
    },

{'type':'StaticText', 
    'name':'textclock', 
    'position':(560, 10), 
    'text':'textclock', 
    },

{'type':'TextField', 
    'name':'mynodename', 
    'position':(85, 20), 
    'text':'mynodename', 
    },

{'type':'StaticText', 
    'name':'StaticText1', 
    'position':(25, 25), 
    'text':'My name:', 
    },

{'type':'MultiColumnList', 
    'name':'nodelist', 
    'position':(14, 54), 
    'size':(604, 319), 
    'backgroundColor':(255, 255, 255, 255), 
    'columnHeadings':[], 
    'items':[], 
    'maxColumns':20, 
    'rules':1, 
    },

] # end components
} # end background
] # end backgrounds
} }
