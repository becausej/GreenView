from PIL import Image
import numpy as np

left_crop_amount = 43
right_crop_amount = 28
top_crop_amount = 47
bottom_crop_amount = 50

def crop_img(filename):
    im = Image.open(filename)
    width, height = im.size
    im1 = im.crop((left_crop_amount, top_crop_amount, width-right_crop_amount, height-bottom_crop_amount))
    return im1

def green(mask, num_row, num_col):
    skip_row = mask.shape[0] % num_row
    skip_col = mask.shape[1] % num_col
    mask = mask[:mask.shape[0] - skip_row, :mask.shape[1] - skip_col]
    mask = mask.reshape(num_row, num_col, mask.shape[0] // num_row, mask.shape[1] // num_col)
    return np.mean(mask, axis=(2, 3))

# Load image and convert to HSV
def one_img(filename, min_hue = 40, max_hue = 70, sat_min = 0.25, min_val = 20, num_row = 3, num_col = 3):
    im = crop_img(filename).convert('HSV')
    # Extract Hue channel and make Numpy array for fast processing
    Hue = np.array(im.getchannel('H'))
    rgb = im.convert('RGB')
    a = np.asarray(rgb, int)
    m = np.min(a,2).T
    M = np.max(a,2).T
    C = M - m
    Cmsk = C != 0
    V = M
    #print(a.T.shape)
    S = np.zeros_like(Hue, float).T
    S[Cmsk] = ((C[Cmsk]) / V[Cmsk])

    huesat_mask = np.zeros_like(Hue, dtype=np.uint8) 

    huesat_mask[(Hue>min_hue) & (Hue<max_hue) & (S.T > sat_min) & (V.T > min_val)] = 1
    return green(huesat_mask, num_row, num_col)
