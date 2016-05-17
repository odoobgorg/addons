# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo Bulgaria Accounting, Open Source Accounting and Invoiceing Module
#    Copyright (C) 2016 BGO software LTD, Lumnus LTD, Prodax LTD
#    (http://www.bgosoftware.com, http://www.lumnus.net, http://wwprodax.bg)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

#-------------------------------------------------------------
# Bulgarian
#-------------------------------------------------------------


to_19_bg = ( u'нула',  u'един',   u'два',  u'три', u'четири',   u'пет',   u'шест',
          u'седем', u'осем', u'девет', u'десет',   u'единадесет', u'дванадесет', u'тринадесет',
          u'четиринадесет', u'петнадесет', u'щестнадесет', u'седемнадесет', u'осемнадесет', u'деветнадесет' )
sto_bg = ( u'',  u'сто',   u'двeста',  u'триста', u'четиристотин',   u'петстотин',   u'шестстотин',
          u'седемстотин', u'осемстотин', u'деветстотин' )		  
tens_bg  = ( u'двадесет', u'тридесет', u'четиридесет', u'петдесет', u'шестдесет', u'седемдесет', u'осемдесет', u'деветдесет')

denom_bg = ( u'',  u'хиляди',         u'милиона',    u'миларда',    'Billions',       'Quadrillions',
          'Quintillion',  'Sextillion',      'Septillion',    'Octillion',      'Nonillion',
          'Décillion',    'Undecillion',     'Duodecillion',  'Tredecillion',   'Quattuordecillion',
          'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Icosillion', 'Vigintillion' )

def _convert_nn_bg(val):
    """ convert a value < 100 to Bulgarian
    """
    if val < 20:
        return to_19_bg[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_bg)):
        if dval + 10 > val:
            if val % 10:
                return dcap + u' и ' + to_19_bg[val % 10]
            return dcap

def _convert_nnn_bg(val):
    """ convert a value < 1000 to bulgarian
    
        special cased because it is the level that kicks 
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        word = sto_bg[rem] + u' '
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn_bg(mod)
    return word
	
def _convert_hil_bg(val):
    """ convert a value < 2000 to Bulgarian
    """
    ret = u'хиляда'

    return ret

def _convert_dvehil_bg(val):
    """ convert a value < 3000 to Bulgarian
    """
    ret = u'две хиляди'

    return ret		

def bulgarian_number(val):
    if val < 100:
        return _convert_nn_bg(val)
    if val < 1000:
         return _convert_nnn_bg(val)
    #if val < 2000:
    #    return _convert_hil_bg(val)	
    #if val < 3000:
    #    return _convert_dvehil_bg(val)				
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_bg))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            if l <2:
				ret = u'хиляда'
            elif l <3:
				ret = u'две хиляди'
            else:
				ret = _convert_nnn_bg(l) + ' ' + denom_bg[didx]			
            if r > 0:
				if r < 20 or (r < 100 and r % 10 == 0) or (r >= 100 and r % 100 == 0):
					ret = ret + u' и ' + bulgarian_number(r)
				else:
					ret = ret + u' ' + bulgarian_number(r)			
            return ret

def amount_to_text_bg(number, currency):
    number = '%.2f' % number
    units_name = u'лева'
    list = str(number).split('.')
    start_word = bulgarian_number(abs(int(list[0])))
    end_word = list[1]
    cents_number = int(list[1])
    cents_name =  u' ст.'
    final_result = start_word +' '+units_name+u' и '+ end_word +' '+cents_name
    return final_result

#-------------------------------------------------------------
# Dutch
#-------------------------------------------------------------

to_19_nl = ( 'Nul',  'Een',   'Twee',  'Drie', 'Vier',   'Vijf',   'Zes',
          'Zeven', 'Acht', 'Negen', 'Tien',   'Elf', 'Twaalf', 'Dertien',
          'Veertien', 'Vijftien', 'Zestien', 'Zeventien', 'Achttien', 'Negentien' )
tens_nl  = ( 'Twintig', 'Dertig', 'Veertig', 'Vijftig', 'Zestig', 'Zeventig', 'Tachtig', 'Negentig')
denom_nl = ( '',
          'Duizend', 'Miljoen', 'Miljard', 'Triljoen', 'Quadriljoen',
           'Quintillion', 'Sextiljoen', 'Septillion', 'Octillion', 'Nonillion',
           'Decillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quattuordecillion',
           'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion' )

def _convert_nn_nl(val):
    """ convert a value < 100 to Dutch
    """
    if val < 20:
        return to_19_nl[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_nl)):
        if dval + 10 > val:
            if val % 10:
                return dcap + '-' + to_19_nl[val % 10]
            return dcap

def _convert_nnn_nl(val):
    """ convert a value < 1000 to Dutch
    
        special cased because it is the level that kicks 
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        word = to_19_nl[rem] + ' Honderd'
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn_nl(mod)
    return word

def dutch_number(val):
    if val < 100:
        return _convert_nn_nl(val)
    if val < 1000:
         return _convert_nnn_nl(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_nl))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn_nl(l) + ' ' + denom_nl[didx]
            if r > 0:
                ret = ret + ', ' + dutch_number(r)
            return ret

def amount_to_text_nl(number, currency):
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = dutch_number(int(list[0]))
    end_word = dutch_number(int(list[1]))
    cents_number = int(list[1])
    cents_name = (cents_number > 1) and 'cent' or 'cent'
    final_result = start_word +' '+units_name+' '+ end_word +' '+cents_name
    return final_result

#-------------------------------------------------------------
# Generic functions
#-------------------------------------------------------------

_translate_funcs = {'bg' : amount_to_text_bg, 'nl' : amount_to_text_nl}

def add_amount_to_text_function(lang, func):
    _translate_funcs[lang] = func
    
#TODO: we should use the country AND language (ex: septante VS soixante dix)
#TODO: we should use en by default, but the translation func is yet to be implemented
def amount_to_text(nbr, lang='bg', currency=u'лева'):
    """ Converts an integer to its textual representation, using the language set in the context if any.

        Example::
        
            1654: mille six cent cinquante-quatre.
    """
#    if nbr > 1000000:
##TODO: use logger   
#        print "WARNING: number too large '%d', can't translate it!" % (nbr,)
#        return str(nbr)
    
    if not _translate_funcs.has_key(lang):
#TODO: use logger   
        print "WARNING: no translation function found for lang: '%s'" % (lang,)
#TODO: (default should be en) same as above
        lang = 'bg'
    return _translate_funcs[lang](abs(nbr), currency)

if __name__=='__main__':
    from sys import argv
    
    lang = 'nl'
    if len(argv) < 2:
        for i in range(1,200):
            print i, ">>", amount_to_text(i, lang)
        for i in range(200,999999,139):
            print i, ">>", amount_to_text(i, lang)
    else:
        print amount_to_text(int(argv[1]), lang)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

