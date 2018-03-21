from pylab import *
from PIL import Image
from PIL import ImageEnhance
from scipy import ndimage as ndimage
import numpy as np
import os
import pywt
import cv2
import Tkinter
import tkMessageBox
from tkFileDialog import askopenfilename
from tkFileDialog import askdirectory

__author__ = 'Nicklas'
DEBUG = 0
top = Tkinter.Tk()

def pad_to_square(a, pad_value=0):
  m = a.reshape((a.shape[0], -1))
  padded = pad_value * np.ones(2 * [max(m.shape)], dtype=m.dtype)
  padded[0:m.shape[0], 0:m.shape[1]] = m
  return padded

def make_divisible_by(a, k=3):
    if a.shape[0] % k == 0:
        return a
    else:
        b = np.zeros((a.shape[0]+1, a.shape[1]+1))
        b[:-1,:-1] = a
        return make_divisible_by(b, k)

def make_blocks(a):
    step = a.shape[0]/3
    blockArray = []

    for i in xrange(0, a.shape[0], step):
        for j in xrange(0, a.shape[1], step):
            block = a[i:i+step, j:j+step]
            block = np.array(cv2.blur((block), (2, 2))) #blur block for OCR
            blockArray.append((np.mean(block))/1000)
            #print (np.mean(block))/1000

    return blockArray

def threshold(a, t):
    for index, value in ndenumerate(a):
        if value > t:
            new_value = 0
        else:
            new_value = 255
        a[index] = new_value

    return a


def partition(a, lo, hi):
    pIndex = hi
    pValue = a[pIndex]
    a[pIndex], a[hi] = a[hi], a[pIndex]
    storeIndex  = lo

    for i in xrange(lo, hi):
        if a[i][0].stop < pValue[0].start:
            a[i], a[storeIndex] = a[storeIndex], a[i]
            storeIndex = storeIndex +1
            continue
        if a[i][0].stop > pValue[0].start:
            if a[i][1].stop < pValue[1].start:
                a[i], a[storeIndex] = a[storeIndex], a[i]
                storeIndex = storeIndex +1


    a[storeIndex], a[hi] = a[hi], a[storeIndex]
    return storeIndex

def sort_letters(a, lo, hi):
    #print "test"
    #print a[lo][0].start


    if lo < hi:
        p = partition(a, lo, hi)
        sort_letters(a, lo, p - 1)
        sort_letters(a, p + 1, hi)

def normalCallBack():
    filename = askopenfilename()
    im = Image.open(filename)
    im = im.convert('L')
    im_array = np.array(im, float)
    Image.fromarray(im_array).show()

    enh = ImageEnhance.Contrast(im)
    im = enh.enhance(1.5)
    im_array = np.array(im, float)
    Image.fromarray(im_array).show()

    # simple threshold function
    im_array = threshold(im_array, 90)

    Image.fromarray(im_array).show()

    # extract characters

    s = ndimage.generate_binary_structure(2, 2)
    labeled_array, num_features = ndimage.label(im_array, s)
    #print(num_features)

    tuple_list = ndimage.find_objects(labeled_array)

    sort_letters(tuple_list, 0, len(tuple_list)-1)
    sort_letters(tuple_list, 0, len(tuple_list)-1)
    sort_letters(tuple_list, 0, len(tuple_list)-1)
    labeled_array = threshold(labeled_array, 0)

    #Image.fromarray(labeled_array).show()



    i = 0
    arrayList = []
    directory = askdirectory(title='Please select a directory')
    for tuple in tuple_list:
        #print tuple[0].start
        array = labeled_array[tuple[0].start:tuple[0].stop, tuple[1].start:tuple[1].stop]
        array = pad_to_square(array, 255)
        if array.shape[0] < 40:
            continue
        array = make_divisible_by(array)

        averageArray = make_blocks(array)

        arrayList.append(averageArray)


        #np.savetxt('C:\Users\Nicklas\Dropbox\school\Image processing\OCR\src\\values.txt', arrayList, fmt = "%.5f", delimiter=' ')
        np.savetxt(directory + "\\values.txt", arrayList, fmt = "%.5f", delimiter=' ')

        Image.fromarray(array).convert('RGB').save(directory + "\\letter"
                                                   + str(i) + ".jpg")
        i = i + 1

    print "Done, choose another operation or exit"
def blurryCallBack():
    filename = askopenfilename()
    im = Image.open(filename)
    im = im.convert('L')
    #Image.fromarray(im_array).show()

    #sharpening image
    sharpener = ImageEnhance.Sharpness(im)
    sharpened_image = sharpener.enhance(5)

    filter_blurred_l = ndimage.gaussian_filter(im, 1)
    alpha = 30
    sharpened = im + alpha * (im - filter_blurred_l)

    enh = ImageEnhance.Contrast(sharpened_image)
    im = enh.enhance(1.9)
    im_array = np.array(im, float)
    Image.fromarray(im_array).show()

    # simple threshold function
    im_array = threshold(im_array, 110)

    Image.fromarray(im_array).show()

    s = ndimage.generate_binary_structure(2, 2)
    labeled_array, num_features = ndimage.label(im_array, s)
    #print(num_features)

    tuple_list = ndimage.find_objects(labeled_array)
    #print tuple_list

    sort_letters(tuple_list, 0, len(tuple_list)-1)
    sort_letters(tuple_list, 0, len(tuple_list)-1)
    sort_letters(tuple_list, 0, len(tuple_list)-1)

    labeled_array = threshold(labeled_array, 0)

    #Image.fromarray(labeled_array).show()



    i = 0
    arrayList = []
    directory = askdirectory(title='Please select a directory')
    for tuple in tuple_list:
        array = labeled_array[tuple[0].start:tuple[0].stop, tuple[1].start:tuple[1].stop]
        array = pad_to_square(array, 255)
        if array.shape[0] < 40:
            continue
        array = make_divisible_by(array)

        averageArray = make_blocks(array)

        arrayList.append(averageArray)

        #np.savetxt('C:\Users\Nicklas\Dropbox\school\Image processing\OCR\src\\values.txt', arrayList, fmt = "%.5f", delimiter=' ')
        np.savetxt(directory + "\\values.txt", arrayList, fmt = "%.5f", delimiter=' ')

        Image.fromarray(array).convert('RGB').save(directory + "\\letter"
                                                   + str(i) + ".jpg")
        i = i + 1

    print "Done, choose another operation or exit"

def darkCallback():
    filename = askopenfilename()
    im = Image.open(filename)
    im = im.convert('L')

    #brighten
    im = im.point(lambda p: p * 2)
    im_array = np.array(im, float)
    Image.fromarray(im_array).show()

    # simple threshold function
    im_array = threshold(im_array, 55)
    Image.fromarray(im_array).show()

    #extract letters
    s = ndimage.generate_binary_structure(2, 2)
    labeled_array, num_features = ndimage.label(im_array, s)
    #print(num_features)

    tuple_list = ndimage.find_objects(labeled_array)
    #print tuple_list

    sort_letters(tuple_list, 0, len(tuple_list)-1)
    sort_letters(tuple_list, 0, len(tuple_list)-1)
    sort_letters(tuple_list, 0, len(tuple_list)-1)

    labeled_array = threshold(labeled_array, 0)

    #Image.fromarray(labeled_array).show()



    i = 0
    arrayList = []
    directory = askdirectory(title='Please select a directory')
    for tuple in tuple_list:
        array = labeled_array[tuple[0].start:tuple[0].stop, tuple[1].start:tuple[1].stop]

        array = pad_to_square(array, 255)
        if array.shape[0] < 40:
            continue
        array = make_divisible_by(array)

        averageArray = make_blocks(array)

        arrayList.append(averageArray)

        #np.savetxt('C:\Users\Nicklas\Dropbox\school\Image processing\OCR\src\\values.txt', arrayList, fmt = "%.5f", delimiter=' ')
        np.savetxt(directory + "\\values.txt", arrayList, fmt = "%.5f", delimiter=' ')

        Image.fromarray(array).convert('RGB').save(directory + "\\letter"
                                                   + str(i) + ".jpg")
        i = i + 1

    print "Done, choose another operation or exit"
    #print arrayList

def testCallBack():
    im = Image.open("test4.jpg")
    im = im.convert('L')
    enh = ImageEnhance.Contrast(im)

    im_array = np.array(enh.enhance(1.5), float)
    Image.fromarray(im_array).show()
    random_data = np.random.randn(im_array.shape[0],im_array.shape[1])
    im_array = im_array + 100.*random_data
    Image.fromarray(im_array).show()
    im_array = ndimage.gaussian_filter(im_array, sigma=5)
    Image.fromarray(im_array).show()
    # simple threshold function
   # im_array = threshold(im_array, 55)
    #Image.fromarray(im_array).show()





normal_button = Tkinter.Button(top, text ="normal image", command = normalCallBack)
test_button = Tkinter.Button(top, text ="test image", command = testCallBack)
blurry_button = Tkinter.Button(top, text = "blurry image", command = blurryCallBack)
dark_button = Tkinter.Button(top, text = "dark image", command = darkCallback)

normal_button.pack()
blurry_button.pack()
dark_button.pack()
if DEBUG == 1:
    test_button.pack()
top.mainloop()
