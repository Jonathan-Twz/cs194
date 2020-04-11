# CS194-26 (CS294-26): Project 1 starter Python code

# these are just some suggested libraries
# instead of scikit-image you could use matplotlib and opencv to read, write, and display images

import numpy as np
import skimage as sk
from skimage.transform import rescale
import skimage.io as skio
from tqdm import tqdm
from matplotlib import pyplot as plt

def crop(img, percent):
    h,w = np.floor(img.shape[0]*percent).astype(np.int), np.floor(img.shape[1]*percent).astype(np.int)
    return img[h:-h, w:-w]

def shift(img, crop_percentage, shift_range, b, y=0, x=0):
    shift_yx=[]
    min_curr = 9999999999   #represent for a large number
    with tqdm(total = 2*shift_range) as pbar:
        for shift_x in range(x-shift_range, x+shift_range):
            for shift_y in range(y-shift_range, y+shift_range):
                img1=np.roll(img, shift_y, axis=0)
                img2=np.roll(img1, shift_x, axis=1)
                img_crop, b_crop=crop(img2, crop_percentage), crop(b, crop_percentage)
                ssd_curr = np.sum((img_crop - b_crop)**2)
                if ssd_curr < min_curr:
                    min_curr = ssd_curr
                    shift_yx=[shift_y, shift_x]
            pbar.update()
    return shift_yx

def roll(img, shift_yx):
    img1 = np.roll(img,shift_yx[0],axis=0)
    img2 = np.roll(img1,shift_yx[1], axis=1)
    return img2

def pyr(img, coef, b):
    depth = int(np.log(height/200)/np.log(coef))+1    # coef > 0
    curr_y, curr_x = 0, 0
    for d in range(depth+1):
        curr_y, curr_x = int(curr_y*coef), int(curr_x*coef)
        img_re = sk.transform.rescale(img, (1/coef)**(depth-d))
        b_re = sk.transform.rescale(b, (1/coef)**(depth-d))
        curr_y, curr_x = shift(img_re, 0.1, 5, b_re, curr_y, curr_x)
        print('curr_yx',curr_y,curr_x)
        print('Depth_remain:',depth-d)
    return [curr_y, curr_x]

def ssd(r, g, b, threshold, direction):
    """
    ssd_y and ssd_x representing brightness ssd
    on the edge ssd is extremely big
    so we can cut the edge
    """

    diff = (r-b)**2 + (b-g)**2 + (g-r)**2
    row_diffs = np.apply_along_axis(np.mean, 1, diff)
    col_diffs = np.apply_along_axis(np.mean, 0, diff)

    row_t = np.mean(row_diffs)*1.3
    col_t = np.mean(col_diffs)*1.3

    print(row_diffs.shape[0]//2)

    row_i = row_j = row_diffs.shape[0]//2
    col_i = col_j = col_diffs.shape[0]//2

    print(row_i, row_j)

    while row_diffs[row_i] < row_t and row_i>=0:
        row_i-=1
    while row_diffs[row_j] < row_t and row_j<row_diffs.shape[0]-1:
        row_j+=1
    while col_diffs[col_i] < col_t and col_i>=0:
        col_i-=1
    while col_diffs[col_j] < col_t and col_j<col_diffs.shape[0]-1:
        col_j+=1

    # plt.plot(row_diffs)
    # plt.show()

    im_out = np.dstack([r, g, b])
    # print(im_out[row_i:row_j, col_i:col_j, :].shape)
    im_out_final = im_out[row_i:row_j, col_i:col_j, :]
    skio.imshow(im_out)
    skio.show()
    skio.imsave("before_crop_1.jpg", im_out)
    skio.imsave("auto_crop_1.jpg", im_out_final)
    print(row_diffs.shape)
    print(col_diffs.shape)
    print(diff.shape)
    return None

# name of the input file
pic_names = ['church.jpg','building.jpg','cathedral.jpg','monastery.jpg','tobolsk.jpg','emir.tif','harvesters.tif','icon.tif','lady.tif','melons.tif','onion_church.tif','self_portrait.tif','three_generations.tif','train.tif','village.tif','workshop.tif']
pic_names = pic_names[0:1]
save = 0
show = 0

for i in range(len(pic_names)):
    pic_name = pic_names[i]
    imname = 'data\\{}'.format(pic_name)
    print(imname)
    # read in the image
    im = skio.imread(imname)

    # convert to double (might want to do this later on to save memory)    
    im = sk.img_as_float(im)
        
    # compute the height of each part (just 1/3 of total)
    height = np.floor(im.shape[0] / 3.0).astype(np.int)
    width = np.floor(im.shape[1]).astype(np.int)
    print('height & width:',height,width)

    # separate color channels
    b = im[:height]
    g = im[height: 2*height]
    r = im[2*height: 3*height]

    # functions that might be useful for aligning the images include:
    # np.roll, np.sum, sk.transform.rescale (for multiscale)
    r_shift = pyr(r, 1.8, b)
    g_shift = pyr(g, 1.8, b)
    print('r_shift,g_shift:', r_shift, g_shift)
    r_out = roll(r, r_shift)
    g_out = roll(g, g_shift)

    # auto-crop function
    # NOT finished yet 
    ssd(r_out, g_out, b, 0, 0)

    # create a color image
    im_out = np.dstack([r_out, g_out, b])

    # save the image
    fname = 'output\\{}'.format(pic_name.split('.')[0]+'-r'+str(r_shift)+'-g'+str(g_shift)+'.jpg')
    if save:
        skio.imsave(fname, im_out) 

    # display the image
    if show:
        skio.imshow(im_out)
        skio.show()