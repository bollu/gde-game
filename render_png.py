#!/usr/bin/env python3.6
import imageio
png = imageio.imread('sprite2.png')
print(png.shape)

GRAYSCALE_SEQ = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`\'. '

# for i in range(png.shape[0]):
#     for j in range(png.shape[1]):
for i in range(64):
    for j in range(64):
        c = png[i][j]
        gray = (0.2989*c[0] + 0.5870*c[1] + 0.1140*c[2]) / 255.0
        # print(gray)
        c = GRAYSCALE_SEQ[int(gray  * len(GRAYSCALE_SEQ))]
        print(c, end='')
    print('\n', end='')
