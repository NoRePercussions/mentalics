from .ns_array import NSArray
from .ns_attributed_string import NSAttributedString
from .ns_color import NSColor
from .ns_color_space import NSColorSpace
from .ns_data import NSData
from .ns_date import NSDate
from .ns_dictionary import NSDictionary
from .ns_font import NSFont
from .ns_image import NSImage
from .ns_mutable_array import NSMutableArray
from .ns_mutable_data import NSMutableData
from .ns_mutable_dictionary import NSMutableDictionary
from .ns_null import NSNull
from .ns_point import NSPoint
from .ns_size import NSSize
from .ns_url import NSURL
from .ns_uuid import NSUUID

NS_TYPES = {
    "NSArray": NSArray,
    "NSAttributedString": NSAttributedString,
    "NSColor": NSColor,
    "NSColorSpace": NSColorSpace,
    "NSData": NSData,
    "NSDate": NSDate,
    "NSDictionary": NSDictionary,
    "NSFont": NSFont,
    "NSImage": NSImage,
    "NSMutableArray": NSMutableArray,
    "NSMutableData": NSMutableData,
    "NSMutableDictionary": NSMutableDictionary,
    "NSNull": NSNull,
    "NSPoint": NSPoint,
    "NSSize": NSSize,
    "NSURL": NSURL,
    "NSUUID": NSUUID,
    }
