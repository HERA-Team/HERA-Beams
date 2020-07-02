# HERA-Beams
Repository to hold beam models for HERA

Users who wish to contribute beam models should create a new directory with a descriptive name and include a readme describing where the model comes from, along with other useful information such as units, any relevant conventions, etc. It is also encouraged to include an example script for using the data.

# Installation
The data files in this repo are large and are actually stored in git LFS. To get the actual files (rather than just the small pointers), you'll need to install git LFS following the directions [here](https://help.github.com/en/articles/installing-git-large-file-storage).

If you install git LFS before you clone this repo, the files should be downloaded properly when you clone it normally (`git clone <repo_url>`). If you already have a clone of this repo and the files are just small pointers, you can use `git lfs pull` to get the actual files.
