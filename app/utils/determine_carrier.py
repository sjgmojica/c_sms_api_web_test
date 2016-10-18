"""
Determine carrier for local mobile networks

This class determines the network provider of a given mobile number.

Checking is done by comparing the mobile number to different regular expression
formats.

@author Arthemus Malicdem
"""
from tornado.httpclient import AsyncHTTPClient2
from tornado.options import options

import urllib
import urlparse
  
import urllib
import urlparse
import re2 as re

"""
Regular expression pattern for Globe mobile phones
"""
GLOBE_PREFIX = "05|06|15|16|17|26|27|35|37"

"""
Regular expression pattern for Smart mobile phones
"""
SMART_PREFIX = "18|19|20|10|21|28|29|09|08|07|99|12|30|39|46|47|48|49|98|99"

"""
Regular expression pattern for Sun mobile phones
"""
SUN_PREFIX = "22|23|25|32|33|42|43"

"""
Regular expression pattern of Hong-Kong mobile phones
"""
HK_PREFIX = "^[+| ]?85[2|3][0-9]{8,8}$"

"""
Regular expression pattern of Hong-Kong mobile phones
"""
GUAM_PREFIX_1 = "^[+| ]?67(1|0)(6|4)[0-9]{6,6}$"
GUAM_PREFIX_2 = "^67(168(6|7|8|9)[0-9]{4,4})|(048(3|4)[0-9]{4,4})"
GUAM_PREFIX_3 = "^48(3|4)[0-9]{4,4}$"

"""
Regular expression pattern of China mobile phones
"""
CHINA_PREFIX = "^[+| ]?8613[0-9]{9,9}$"

"""
Regular expression pattern of Singtel mobile phones
"""
SINGTEL_PREFIX = "^65[0-9]{8,8}$"

PH_CARRIERS = ['GLOBE', 'SMART', 'SUN', 'TM'] 

 
class DetermineCarrier(object):
    """
    This class determines the telco provider of a given mobile number.
    """
    def __init__(self, mobile):  
        """
        Construct the class for DetermineCarrier
        """ 
        if mobile and type(mobile) is not bool:   
            alter = self.alter_ph_mobile(mobile)
            if alter and type(alter) is int:
                self.mobile = int(self.alter_ph_mobile(mobile))
            else:
                self.mobile = mobile
    
    def get_carrier(self): 
        """
        Identifies the telco provider of a given mobile number.
        """
        if not getattr(self, 'mobile', None):
            return None 
        carrier = None  
        if (self.mobile >= 639168200000 and self.mobile <= 639169999999) or \
            (self.mobile >= 639261000000 and self.mobile <= 639269999999) or \
            (self.mobile >= 639260000200 and self.mobile <= 639260000403) or \
            (self.mobile >= 639068000000 and self.mobile <= 639069999999) or \
            (self.mobile >= 639350000000 and self.mobile <= 639352999999) or \
            (self.mobile >= 639354000000 and self.mobile <= 639359999999) or \
            (self.mobile >= 639051300000 and self.mobile <= 639051799999) or \
            (self.mobile >= 639055800000 and self.mobile <= 639056599999) or \
            (self.mobile >= 639056700000 and self.mobile <= 639059799999):
            carrier = "TM"
        elif self.globe_pattern.match(self.mobile):
            carrier = "GLOBE"
        elif self.smart_pattern.match(self.mobile):
            carrier = "SMART"
        elif self.sun_pattern.match(self.mobile):
            carrier = "SUN"
        elif self.hk_pattern.match(self.mobile):
            carrier = "HK"
        elif self.china_pattern.match(self.mobile):
            carrier = "CHINA"
        elif self.singtel_pattern.match(self.mobile):
            carrier = "SINGTEL"
         
        is_guam = False
        for i in range(1,3):
            if self.guam_pattern(i).match(self.mobile):
                is_guam = True
        if is_guam:
            carrier = "GUAM"  
        return carrier
        
    def alter_ph_mobile(self, mobile):
        """
        @param mobile: Integer, mobile number
        
        Converts the given mobile number to philippine
        mobile number format.
        """
        if not mobile:
            return mobile  
        if mobile.startswith('0'):
            return '63%s' % mobile[1:]
        elif mobile.startswith('+'):
            return mobile[1:]
        elif mobile.startswith('9'):
            return '63%s' % mobile
        else:
            return mobile
    
    @property
    def globe_pattern(self):
        """
        Getter for GLOBE regex
        """
        return re.compile(r"^((\+63)|63|0)9(%s)[0-9]{7,7}$" % GLOBE_PREFIX, re.IGNORECASE)
 
    @property
    def smart_pattern(self):
        """
        Getter for SMART regex
        """
        return re.compile(r"^((\+63)|63|0)9(%s)[0-9]{7,7}$" % SMART_PREFIX, re.IGNORECASE)
    
    @property
    def sun_pattern(self):
        """
        Getter for SUN regex
        """
        return re.compile(r"^((\+63)|63|0)9(%s)[0-9]{7,7}$" % SUN_PREFIX,re.IGNORECASE)
    
    @property
    def hk_pattern(self):
        """
        Getter for HONG-KONG regex
        """
        return re.compile(r"%s" % HK_PREFIX, re.IGNORECASE)
    
    def guam_pattern(self, pattern_no):
        """
        Getter for GUAM regex
        """
        patterns = {
                    '1': re.compile(r"%s" % GUAM_PREFIX_1, re.IGNORECASE),
                    '2': re.compile(r"%s" % GUAM_PREFIX_2, re.IGNORECASE),
                    '3': re.compile(r"%s" % GUAM_PREFIX_3, re.IGNORECASE)
                    } 
        return patterns[str(pattern_no)]
        
    @property
    def china_pattern(self):
        """
        Getter for CHINA regex
        """
        return re.compile(r"%s" % CHINA_PREFIX, re.IGNORECASE)
    
    @property
    def singtel_pattern(self):
        """
        Getter for SINGTEL regex
        """
        return re.compile(r"%s" % SINGTEL_PREFIX, re.IGNORECASE)

"""

<?
/*
 * This function returns the "carrier" (sometimes it's "brand" like 'TM') but
 * this was a compromise. Looking back, 'TM' should be returned as 'GLOBE' and a
 * separate function, say determine_brand(), would return 'TM', 'TNT', etc.
 */

echo determine_carrier($_GET['mobile']);


function determine_carrier($phoneNumber)
{
    $carrier = "";
    
    $globe_pattern1 = "^[+| ]?639(17|16|27|26|15|06|05|35|37)[0-9]{7,7}$";
    $globe_pattern2 = "^09(17|16|27|26|15|06|05|35|37)[0-9]{7,7}$";

    $smart_pattern1 = "^[+| ]?639(18|19|20|10|21|28|29|09|08|07|99|12|30|39|46|47|48|49|99)[0-9]{7,7}$";
    $smart_pattern2 = "^09(18|19|20|10|21|28|29|09|08|07|99|12|30|39|46|47|48|49|99)[0-9]{7,7}$";

    $sun_pattern    = "^[+| ]?639(22|23|25|32|33|42|43)[0-9]{7,7}$";
    $sun_pattern2    = "^09(22|23|25|32|33|42|43)[0-9]{7,7}$";

    $hk_pattern     = "^[+| ]?85[2|3][0-9]{8,8}$";

    $guam_pattern1  = "^[+| ]?67(1|0)(6|4)[0-9]{6,6}$";
    $guam_pattern2  = "^67(168(6|7|8|9)[0-9]{4,4})|(048(3|4)[0-9]{4,4})"; // $guam_pattern2  = "^68(6|7|8|9)[0-9]{4,4}$";
    $guam_pattern3  = "^48(3|4)[0-9]{4,4}$"; // Saipan, really

    $china_pattern     = "^[+| ]?8613[0-9]{9,9}$";

    $singtel_pattern = "^65[0-9]{8,8}$";

    //because Touch Mobile is a subset of Globe, check it first
    if (
        ($phoneNumber >= 639168200000) && ($phoneNumber <= 639169999999)
        ||
        ($phoneNumber >= 639261000000) && ($phoneNumber <= 639269999999)
        ||
        ($phoneNumber >= 639260000200) && ($phoneNumber <= 639260000403)
        ||
        ($phoneNumber >= 639068000000) && ($phoneNumber <= 639069999999)
        ||
        //($phoneNumber >= 639350000000) && ($phoneNumber <= 639359999999)
        ($phoneNumber >= 639350000000) && ($phoneNumber <= 639352999999)
        ||
        ($phoneNumber >= 639354000000) && ($phoneNumber <= 639359999999)
        ||
        ($phoneNumber >= 639051300000) && ($phoneNumber <= 639051799999)
        ||
        ($phoneNumber >= 639055800000) && ($phoneNumber <= 639056599999)
        ||
        ($phoneNumber >= 639056700000) && ($phoneNumber <= 639059799999)
       )
    {
        $carrier = 'TM';
    }
    else if (ereg($globe_pattern1, $phoneNumber) OR ereg($globe_pattern2, $phoneNumber))
    {
        $carrier = 'GLOBE';
    }
    else if (ereg($smart_pattern1, $phoneNumber) OR ereg($smart_pattern2, $phoneNumber))
    {
        $carrier = 'SMART';
    }
    else if (ereg($sun_pattern, $phoneNumber) OR ereg($sun_pattern2, $phoneNumber))
    {
        $carrier = 'SUN';
    }
    else if (ereg($hk_pattern, $phoneNumber))
    {
        $carrier = 'HK';
    }
    else if (ereg($guam_pattern1, $phoneNumber)) //OR ereg($guam_pattern2, $phoneNumber) OR ereg($guam_pattern3, $phoneNumber))
    {
        $carrier = 'GUAM';
    }
    else if (ereg($china_pattern, $phoneNumber))
    {
        $carrier = 'CHINA';
    }
    else if (ereg($singtel_pattern, $phoneNumber))
    {
        $carrier = 'SINGTEL';
    }

    return $carrier;
}
?>
"""
