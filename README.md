# TimeseriesBenchmark
This program runs benchmarks on defined algorithms over datasets picked from UEA and UCR.
Results are logged into json files.

The json files can be analyzed and tables and plots can be generated automagically.


For this to happen the branch 'bath' of the sktime fork needs to be installed.


### Installation Instructions for MacOs:

#### Prerequisites
The build of the package requires Cython and OpenMP to be installed and enabled. For this, run the following commands as a prerequisite for the build of the modified sktime package.

Install Cython:

    pip install cython

Install OpenMP and set environment variables to allow OpenMP usage

    brew install libomp

    export CC=/usr/bin/clang
    export CXX=/usr/bin/clang++
    export CPPFLAGS="$CPPFLAGS -Xpreprocessor -fopenmp"
    export CFLAGS="$CFLAGS -I/usr/local/opt/libomp/include"
    export CXXFLAGS="$CXXFLAGS -I/usr/local/opt/libomp/include"
    export LDFLAGS="$LDFLAGS -L/usr/local/opt/libomp/lib -lomp"
    export DYLD_LIBRARY_PATH=/usr/local/opt/libomp/lib

We also need tslearn for the benchmarking:

    export CFLAGS="-I /usr/local/lib/python3.9/site-packages/numpy/core/include $CFLAGS"

    pip install --user tslearn

#### sktime installation

Clone the repository and switch to the correct branch

    git clone https:github.com/donnerluetjen/sktime

    cd sktime
    
    git checkout bath


Finally, install the package

    pip install .


In case of problems, there is an advanced installation instructional on the sktime website
https://www.sktime.org/en/latest/installation.html.

You need to remember, though, that you are installing a fork of the sktime library from a different repository.


### Start of Benchmark

Make sure you are in the TimeseriesBenchmark directory and run

    pyhon3 ts_benchmark.py

This will generate json files with the benchmark results for each SCB size.

In order to process them into tex files, you will need to split them up into the following filenames (wws is the window size aka SCB size)

    UEA_archive_wws--1.json
    UCR_archive_wws--1.json    
    UEA_archive_wws-0-3.json
    UCR_archive_wws-0-3.json
    UEA_archive_wws-0-1.json
    UCR_archive_wws-0-1.json

#### Tex File Generation
Once, the files are split into the right parts, you can run
    
    python3 generate_tables_and_plots.py
    
which will generate all the tex files.