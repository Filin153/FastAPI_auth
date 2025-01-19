import pyotp

totp = pyotp.TOTP('gAAAAABnjXrhTZhC0m1o9he2XSOdvfCUG71i2ZLvCelgR1leyOS-GoyT5ZPOr55iDC9bbdLC3XfkTPqTU3MmHexhbd5_8zy9V5hi-WKaOHGimvrmFMNVEIxLDhZzU-mzAYpoVYihcgIs')
print(totp.verify("900464"))