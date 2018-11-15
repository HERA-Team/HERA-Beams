import os
import subprocess
import argparse
import six
import fnmatch
import numpy as np
from pyuvdata import UVBeam

a = argparse.ArgumentParser(description="A command-line script to convert Nicolas "
                            "Fagnoni's CST simulations to UVBeam FITS files.")
a.add_argument('nf_repo_path', type=str, help="Path to Nicolas Fagnoni's git repo")
a.add_argument('--efield', help='Efield rather than power beams',
               action='store_true', default=False)
a.add_argument('--calc_cross_pols', help='Calculate cross pol power beams '
               '(i.e. xy, yx). Only applies if efield is not True.',
               action='store_true', default=False)
a.add_argument('--peak_normalize', help='Peak normalize the beam.',
               action='store_true', default=False)
a.add_argument('--healpix', help='Convert to HEALPix',
               action='store_true', default=True)
a.add_argument("--hp_nside", default=None, type=int, help="If converting to HEALpix, use"
               "this NSIDE. Default is closest, yet higher, resolution to input resolution.")
a.add_argument('--outfile', type=str, help='Output file name', default=None)
a.add_argument('-f', '--freq_range', nargs=2, type=float,
               help='Frequency range to include in MHz')

args = a.parse_args()
nf_repo_path = os.path.expanduser(args.nf_repo_path)

if not os.path.isdir(nf_repo_path):
    raise ValueError("Path to Nicolas Fagnoni's simulations not found.")

model_name = 'E-field pattern - Rigging height 4.9 m'
file_path = os.path.join(nf_repo_path, 'Radiation patterns/' + model_name + '/')

beam_files = []
for root, dirnames, filenames in os.walk(file_path):
    for filename in fnmatch.filter(filenames, '*E-pattern*.txt'):
        beam_files.append(os.path.join(root, filename))

git_origin = subprocess.check_output(['git', '-C', nf_repo_path, 'config',
                                      '--get', 'remote.origin.url'],
                                     stderr=subprocess.STDOUT).strip()
git_hash = subprocess.check_output(['git', '-C', nf_repo_path, 'rev-parse', 'HEAD'],
                                   stderr=subprocess.STDOUT).strip()
git_branch = subprocess.check_output(['git', '-C', nf_repo_path, 'rev-parse',
                                      '--abbrev-ref', 'HEAD'],
                                     stderr=subprocess.STDOUT).strip()

if six.PY3:
    git_origin = git_origin.decode('utf8')
    git_hash = git_hash.decode('utf8')
    git_branch = git_branch.decode('utf8')

version_str = ('  Git origin: ' + git_origin
               + '.  Git branch: ' + git_branch
               + '.  Git hash: ' + git_hash + '.')

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

if args.peak_normalize:
    beam.peak_normalize()

if args.healpix:
    beam.interpolation_function = 'az_za_simple'
    beam.to_healpix(nside=hp_nside)
    default_out_file += '_healpix'

default_out_file += '.fits'
if args.outfile is not None:
    outfile = args.outfile
else:
    outfile = default_out_file

beam.write_beamfits(outfile, clobber=True)
