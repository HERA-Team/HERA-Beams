import os
import subprocess
import argparse
import six
import fnmatch
import numpy as np
from pyuvdata import UVBeam
import glob

a = argparse.ArgumentParser(description="A command-line script to convert Nicolas "
                            "Fagnoni's CST simulations to UVBeam FITS files.")
a.add_argument('data_dir', type=str, help="Directory holding Nicolas Fagnoni's CST file outputs with *MHz.txt ending.")
a.add_argument('--efield', help='Efield rather than power beams',
               action='store_true', default=False)
a.add_argument('--calc_cross_pols', help='Calculate cross pol power beams '
               '(i.e. xy, yx). Only applies if efield is not True.',
               action='store_true', default=False)
a.add_argument('--peak_normalize', help='Peak normalize the beam.',
               action='store_true', default=False)
a.add_argument('--no_healpix', help='Convert to HEALPix',
               action='store_true', default=False)
a.add_argument("--hp_nside", default=None, type=int, help="If converting to HEALpix, use"
               "this NSIDE. Default is closest, yet higher, resolution to input resolution.")
a.add_argument("--interp_func", type=str, default="az_za_simple", help="If converting to HEALpix, "
               "use this interpolation function in pyuvdata.UVBeam. Only az_za_simple supported currently.")
a.add_argument('--outfile', type=str, help='Output file name', default=None)
a.add_argument('-f', '--freq_range', nargs=2, type=float,
               help='Frequency range to include in MHz')

args = a.parse_args()

beam_files = beam_files = sorted(glob.glob(os.path.join(args.data_dir, '*E-pattern*MHz.txt')))
model_name = os.path.basename(args.data_dir)
if model_name == "":
    model_name = "None"

# try to get git info
try:
    git_origin = subprocess.check_output(['git', '-C', args.data_dir, 'config',
                                          '--get', 'remote.origin.url'],
                                         stderr=subprocess.STDOUT).strip()
    git_hash = subprocess.check_output(['git', '-C', args.data_dir, 'rev-parse', 'HEAD'],
                                       stderr=subprocess.STDOUT).strip()
    git_branch = subprocess.check_output(['git', '-C', args.data_dir, 'rev-parse',
                                          '--abbrev-ref', 'HEAD'],
                                         stderr=subprocess.STDOUT).strip()

    if six.PY3:
        git_origin = git_origin.decode('utf8')
        git_hash = git_hash.decode('utf8')
        git_branch = git_branch.decode('utf8')

    version_str = ('  Git origin: ' + git_origin
                   + '.  Git branch: ' + git_branch
                   + '.  Git hash: ' + git_hash + '.')
except subprocess.CalledProcessError:
    version_str = "No Git info found."

beam = UVBeam()
default_out_file = 'NF_HERA'

if args.freq_range is not None:
    from pyuvdata.cst_beam import CSTBeam
    beam1 = CSTBeam()
    frequencies = [beam1.name2freq(f) for f in beam_files]
    # convert to MHz
    frequencies = np.array(frequencies) / 1e6
    files_to_use = np.where((frequencies >= args.freq_range[0])
                            & (frequencies <= args.freq_range[1]))[0]
    if files_to_use.size == 0:
        raise ValueError('No files included in freq_range.')

    beam_files = [beam_files[f] for f in files_to_use]

if args.efield or args.calc_cross_pols:
    read_beam_type = 'efield'
else:
    read_beam_type = 'power'

if args.efield:
    default_out_file += '_efield'
else:
    default_out_file += '_power'
default_out_file += '_beam'

beam.read_cst_beam(beam_files, beam_type=read_beam_type, telescope_name='HERA',
                   feed_name='PAPER_dipole', feed_version='0.1',
                   model_name=model_name, model_version='1.0')

if not args.efield and args.calc_cross_pols:
    beam.efield_to_power(nside=args.hp_nside)

beam.history = 'CST simulations by Nicolas Fagnoni.' + version_str

if not args.no_healpix:
    beam.interpolation_function = args.interp_func
    beam.to_healpix(nside=args.hp_nside)
    default_out_file += '_healpix'

if args.peak_normalize:
    beam.peak_normalize()

default_out_file += '.fits'
if args.outfile is not None:
    outfile = args.outfile
else:
    outfile = default_out_file

beam.write_beamfits(outfile, clobber=True)

# utility function for updating files of N. Fagnoni CST
# output for new Vivaldi feed into format compatible with above routine
# Dated: 2/12/2019
def change_name(filename):
    """Edits the filename of new feed .txt files to match old convention"""
    start = filename.find("f=") + 2
    end = filename[start:].find("[1]")-1
    freq = filename[start:][:end]
    pattern = "f={}".format(freq)
    newfile = "{}_{:06.2f}MHz.txt".format(filename[:start-3], float(freq))
    newfile = newfile.replace("farfield", "pattern")
    return newfile

def edit_new_files(filenames):
    """
    Updates the filename and content of new CST .txt files
    to match old .txt file format
    """
    for df in filenames:
        nf = change_name(df)
        with open(df, 'r') as f:
            lines = f.readlines()
        # update header e-field into v
        lines[0] = lines[0].replace("E-field", "V")
        with open(nf, 'w') as f:
            f.write(''.join(lines))
