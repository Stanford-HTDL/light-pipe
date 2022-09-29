import os
import random
import shutil
import time

import matplotlib.pyplot as plt
import numpy as np
from light_pipe import processing
from osgeo import gdal, ogr
from solaris import tile

gdal.UseExceptions()
ogr.UseExceptions()


tile_y = 128
tile_x = 128
dataset_filepath = './data/big_image.tif'
raster_dest_dir = './data/tests/test_pixel_tiling/solaris'


def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))       


def test_solaris():
    start = time.time()
    raster_tiler = tile.raster_tile.RasterTiler(dest_dir=raster_dest_dir,  # the directory to save images to
                                                    src_tile_size=(tile_y, tile_x),  # the size of the output chips
                                                    )
    raster_tiler.tile(dataset_filepath)
    onlyfiles = [os.path.join(raster_dest_dir, f) for f in os.listdir(raster_dest_dir) if \
        os.path.isfile(os.path.join(raster_dest_dir, f))]

    raster_tiles = [gdal.Open(fp).ReadAsArray() for fp in onlyfiles]  
    end = time.time()

    return end - start


def test_light_pipe():
    start = time.time()    
    lp_sample = processing.LightPipeSample(dataset_filepath, array_dtype=np.uint8)

    tiles = lp_sample.tile(tile_y=tile_y, tile_x=tile_x)

    tiles = list(tiles)   
    end = time.time()
    
    return end - start    


if __name__ == "__main__":
    if os.path.exists(raster_dest_dir):
        remove(raster_dest_dir) # Delete images if they already exist
    num_trials = 5
    plt_savepath = "./data/plots/test_pixel_tiling.png"

    tests = [
        ("solaris", test_solaris),
        ("light_pipe", test_light_pipe)
    ]

    colors = {
        "solaris": "m",
        "light_pipe": "c" 
    }    

    res = {tup[0]: list() for tup in tests}
    num_tests = len(tests)
    ids = list(range(num_tests))

    for trial in range(num_trials):
        random.shuffle(ids) # Randomize order
        for id in ids:
            test_name, test = tests[id]
            run_time = test()
            res[test_name].append(run_time)

    x = list(range(num_trials))
    plt.xlabel("Trial Number")
    plt.ylabel("Runtime in Seconds (Logarithmic Scale)")
    plt.title(f"Comparison of Runtimes When Using Pixel Coordinates")
    for key, val in res.items():
        plt.plot(x, val, linestyle='--', marker='o', label=key, color=colors[key])
    plt.yscale('log', base=10)         
    plt.legend()
    plt.savefig(plt_savepath)

    if os.path.exists(raster_dest_dir):
        remove(raster_dest_dir) # Delete images if they already exist
