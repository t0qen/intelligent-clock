from picobricks import WS2812

'''
ws2812 = WS2812(6,brightness=1) Setup
ws2812.pixels_show() Actualize
ws2812.pixels_fill((R,G,B))
'''
ws2812 = WS2812(6,brightness=1)


ws2812.pixels_fill((255,255,255))

ws2812.pixels_show()