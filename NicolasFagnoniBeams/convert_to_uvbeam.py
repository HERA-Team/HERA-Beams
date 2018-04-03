import os
from glob import glob
import subprocess
import argparse
from pyuvdata import UVBeam

a = argparse.ArgumentParser(description="A command-line script to convert Nicolas "
                            "Fagnoni's CST simulations to UVBeam FITS files.")
a.add_argument("nf_repo_path", type=str, help="Path to Nicolas Fagnoni's git repo")

args = a.parse_args()
nf_repo_path = os.path.expanduser(args.nf_repo_path)

if not os.path.isdir(nf_repo_path):
    raise ValueError("Path to Nicolas Fagnoni's simulations not found.")

model_name = 'E-field pattern - Rigging height 4.9 m'
file_path = os.path.join(nf_repo_path, 'Radiation patterns/' + model_name + '/')
beam_files = beam_files = glob(file_path + '*/*E-pattern*.txt')

git_origin = subprocess.check_output(['git', '-C', nf_repo_path, 'config',
                                      '--get', 'remote.origin.url'],
                                     stderr=subprocess.STDOUT).strip()
git_hash = subprocess.check_output(['git', '-C', nf_repo_path, 'rev-parse', 'HEAD'],
                                   stderr=subprocess.STDOUT).strip()
git_branch = subprocess.check_output(['git', '-C', nf_repo_path, 'rev-parse',
                                      '--abbrev-ref', 'HEAD'],
                                     stderr=subprocess.STDOUT).strip()
version_str = ('  Git origin: ' + git_origin +
               '.  Git branch: ' + git_branch +
               '.  Git hash: ' + git_hash + '.')

beam = UVBeam()
beam.read_cst_beam(beam_files, beam_type='efields', telescope_name='HERA',
                   feed_name='PAPER_dipole', feed_version='0.1',
                   model_name=model_name, model_version='1.0')

beam.history = 'CST simulations by Nicolas Fagnoni.' + version_str
beam.write_beamfits("NF_HERA_efield_beam.fits", clobber=True)

beam.efield_to_power()
beam.write_beamfits("NF_HERA_power_beam.fits", clobber=True)

beam.az_za_to_healpix()
beam.write_beamfits("NF_HERA_power_beam_healpix.fits", clobber=True)
