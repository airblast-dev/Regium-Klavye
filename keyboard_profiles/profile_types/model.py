from typing import TypedDict


class Model(TypedDict):
    name: str
    #  The name is the short version of the device name.
    #  For example, the name for RK 68 Super Edition would be just RK 68.

    long_name: str
    #  Long name represents a more specific name for the device.
    #  This includes special editions and/or specific connection protocols.

    connection_protocols: list[str]
    #  This is for different connection protocols such as USB, BT and or 2.4GHz.

    vendor_id: int
    product_id: int
    endpoint: int
    usage: int
    usage_page: int
