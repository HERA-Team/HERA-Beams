The beams here originate from Nicolas Fagnoni's simulations, found at:

https://github.com/Nicolas-Fagnoni/Simulations

These are power beams and the script `convert_to_healpix.py` was used to convert the directivity beams from the CST output to healpix (after unzipping the `.zip` files in `Radiation patterns/Directivity/` directory<sup>[1](#foot1)</sup>). This was done on 12 May, 2017, using Simulations git has 587e076. Only "East" polarization is available from the simulation, but "North" can be created by rotating ninety degrees because there is nothing in the simulation that would break the symmetry.

The beams are centered at theta = 0, and East at phi = 0 in healpix coordinate. An example script to read in the data and plot is provided, `example_beam_read.py`.

The script `convert_to_uvbeam` was used to convert the E-field and power beam patterns from CST to pyuvdata's UVBeam object and the beam FITS format. This was done on 2 April 2018 (using the Simulations git hash 72bb3c3), generating the following files:
NF_HERA_efield_beam.fits
NF_HERA_power_beam.fits
NF_HERA_power_beam_healpix.fits

These files follow the pyuvdata beamfits format (described here: https://github.com/HERA-Team/pyuvdata/blob/master/docs/references/beamfits_memo.pdf),
and can be read into pyuvdata's UVBeam object using the `UVBeam.read_fits` method.

<a name="foot1">1</a>: As of commit c06c980, this directory was renamed to `Radiation patterns/Directivity - Rigging height 4.9 m/`.
